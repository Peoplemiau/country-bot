import random
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from database.models import Country, MilitaryUnit, UnitType, Battle, BattleResult
from utils.error_handler import ValidationError, ResourceError, PermissionError
from utils.logger import get_logger
from config import config

logger = get_logger("military_service")

class MilitaryService:
    """Service for military-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Unit costs
        self.unit_costs = {
            UnitType.INFANTRY: 10,
            UnitType.TANK: 50,
            UnitType.SHIP: 100,
            UnitType.AIRCRAFT: 80
        }
        
        # Unit strength multipliers
        self.unit_strength = {
            UnitType.INFANTRY: 1,
            UnitType.TANK: 5,
            UnitType.SHIP: 10,
            UnitType.AIRCRAFT: 8
        }
    
    def get_military_units(self, country_id: int) -> List[MilitaryUnit]:
        """
        Get all military units for a country
        
        Args:
            country_id: Country ID
            
        Returns:
            List[MilitaryUnit]: List of military unit objects
        """
        return self.db.query(MilitaryUnit).filter(MilitaryUnit.country_id == country_id).all()
    
    def get_military_unit(self, country_id: int, unit_type: UnitType) -> Optional[MilitaryUnit]:
        """
        Get a specific military unit for a country
        
        Args:
            country_id: Country ID
            unit_type: Unit type
            
        Returns:
            Optional[MilitaryUnit]: Military unit object if found, None otherwise
        """
        return self.db.query(MilitaryUnit).filter(
            MilitaryUnit.country_id == country_id,
            MilitaryUnit.unit_type == unit_type
        ).first()
    
    def build_army(
        self, 
        country_id: int, 
        unit_type_str: str, 
        quantity: int
    ) -> Tuple[MilitaryUnit, int]:
        """
        Build military units
        
        Args:
            country_id: Country ID
            unit_type_str: Unit type as string
            quantity: Quantity to build
            
        Returns:
            Tuple[MilitaryUnit, int]: (Updated military unit, Cost)
            
        Raises:
            ValidationError: If validation fails
            ResourceError: If not enough resources
        """
        # Validate unit type
        try:
            unit_type = UnitType(unit_type_str)
        except ValueError:
            valid_types = [t.value for t in UnitType]
            raise ValidationError(
                f"Invalid unit type: {unit_type_str}",
                f"Invalid unit type. Valid types are: {', '.join(valid_types)}"
            )
        
        # Validate quantity
        if quantity <= 0:
            raise ValidationError(
                "Quantity must be greater than 0",
                "Quantity must be greater than 0"
            )
        
        # Calculate cost
        cost = self.unit_costs[unit_type] * quantity
        
        # Get country
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            raise ValidationError(
                f"Country with ID {country_id} not found",
                "Country not found. Please check your country ID."
            )
        
        # Check if enough resources
        if country.resources < cost:
            raise ResourceError(
                f"Not enough resources: {country.resources} < {cost}",
                f"Not enough resources. Building {quantity} {unit_type.value} units costs {cost} resources, but you only have {country.resources}."
            )
        
        # Get or create military unit
        unit = self.get_military_unit(country_id, unit_type)
        if not unit:
            unit = MilitaryUnit(
                country_id=country_id,
                unit_type=unit_type,
                quantity=0,
                technology_level=1
            )
            self.db.add(unit)
        
        # Update unit quantity
        unit.quantity += quantity
        
        # Update country resources
        country.resources -= cost
        country.last_updated = datetime.utcnow()
        
        # Log transaction
        transaction = TransactionLog(
            country_id=country_id,
            transaction_type="build_army",
            amount=-cost,
            description=f"Built {quantity} {unit_type.value} units",
            timestamp=datetime.utcnow()
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"Built {quantity} {unit_type.value} units for country {country_id}")
        
        return unit, cost
    
    def calculate_military_strength(self, country_id: int) -> int:
        """
        Calculate total military strength for a country
        
        Args:
            country_id: Country ID
            
        Returns:
            int: Total military strength
        """
        units = self.get_military_units(country_id)
        
        total_strength = 0
        for unit in units:
            unit_strength = unit.quantity * self.unit_strength[unit.unit_type] * unit.technology_level
            total_strength += unit_strength
        
        return total_strength
    
    def attack(self, attacker_id: int, defender_id: int) -> Dict:
        """
        Attack another country
        
        Args:
            attacker_id: Attacker country ID
            defender_id: Defender country ID
            
        Returns:
            Dict: Battle result
            
        Raises:
            ValidationError: If validation fails
            ResourceError: If not enough resources
        """
        # Validate countries
        attacker = self.db.query(Country).filter(Country.id == attacker_id).first()
        if not attacker:
            raise ValidationError(
                f"Attacker country with ID {attacker_id} not found",
                "Attacker country not found. Please check your country ID."
            )
        
        defender = self.db.query(Country).filter(Country.id == defender_id).first()
        if not defender:
            raise ValidationError(
                f"Defender country with ID {defender_id} not found",
                "Defender country not found. Please check the target country ID."
            )
        
        # Check if attacking self
        if attacker_id == defender_id:
            raise ValidationError(
                "Cannot attack own country",
                "You cannot attack your own country."
            )
        
        # Calculate military strengths
        attacker_strength = self.calculate_military_strength(attacker_id)
        defender_strength = self.calculate_military_strength(defender_id)
        
        # Check if attacker has any military units
        if attacker_strength <= 0:
            raise ResourceError(
                "Attacker has no military units",
                "You don't have any military units. Build an army before attacking."
            )
        
        # Calculate battle result
        result, casualties_attacker, casualties_defender, territory_gained, resources_captured = self._calculate_battle_result(
            attacker_strength, defender_strength, attacker, defender
        )
        
        # Apply casualties
        self._apply_casualties(attacker_id, casualties_attacker)
        self._apply_casualties(defender_id, casualties_defender)
        
        # Transfer resources if attacker won
        if result == BattleResult.VICTORY:
            attacker.resources += resources_captured
            defender.resources -= resources_captured
        
        # Create battle report
        battle_report = self._generate_battle_report(
            attacker, defender, attacker_strength, defender_strength,
            result, casualties_attacker, casualties_defender, territory_gained, resources_captured
        )
        
        # Create battle record
        battle = Battle(
            attacker_id=attacker_id,
            defender_id=defender_id,
            attacker_strength=attacker_strength,
            defender_strength=defender_strength,
            result=result,
            casualties_attacker=casualties_attacker,
            casualties_defender=casualties_defender,
            territory_gained=territory_gained,
            resources_captured=resources_captured,
            battle_date=datetime.utcnow(),
            battle_report=battle_report
        )
        
        self.db.add(battle)
        self.db.commit()
        
        logger.info(f"Battle between {attacker.name} and {defender.name}: {result.value}")
        
        # Return battle result
        return {
            "battle_id": battle.id,
            "attacker": attacker.name,
            "defender": defender.name,
            "result": result.value,
            "attacker_strength": attacker_strength,
            "defender_strength": defender_strength,
            "casualties_attacker": casualties_attacker,
            "casualties_defender": casualties_defender,
            "territory_gained": territory_gained,
            "resources_captured": resources_captured,
            "battle_report": battle_report
        }
    
    def _calculate_battle_result(
        self, 
        attacker_strength: int, 
        defender_strength: int,
        attacker: Country,
        defender: Country
    ) -> Tuple[BattleResult, int, int, int, int]:
        """
        Calculate battle result
        
        Args:
            attacker_strength: Attacker military strength
            defender_strength: Defender military strength
            attacker: Attacker country
            defender: Defender country
            
        Returns:
            Tuple[BattleResult, int, int, int, int]: (Result, Attacker casualties, Defender casualties, Territory gained, Resources captured)
        """
        # Base strength ratio
        strength_ratio = attacker_strength / max(defender_strength, 1)
        
        # Random factor (±20%)
        random_factor = random.uniform(0.8, 1.2)
        
        # Adjusted strength ratio
        adjusted_ratio = strength_ratio * random_factor
        
        # Determine result
        if adjusted_ratio > 1.2:
            result = BattleResult.VICTORY
        elif adjusted_ratio < 0.8:
            result = BattleResult.DEFEAT
        else:
            result = BattleResult.DRAW
        
        # Calculate casualties
        base_casualty_rate = random.uniform(0.1, 0.3)  # 10-30%
        
        if result == BattleResult.VICTORY:
            attacker_casualty_rate = base_casualty_rate * 0.7  # Lower casualties for winner
            defender_casualty_rate = base_casualty_rate * 1.3  # Higher casualties for loser
        elif result == BattleResult.DEFEAT:
            attacker_casualty_rate = base_casualty_rate * 1.3  # Higher casualties for loser
            defender_casualty_rate = base_casualty_rate * 0.7  # Lower casualties for winner
        else:  # Draw
            attacker_casualty_rate = base_casualty_rate
            defender_casualty_rate = base_casualty_rate
        
        casualties_attacker = int(attacker_strength * attacker_casualty_rate)
        casualties_defender = int(defender_strength * defender_casualty_rate)
        
        # Calculate territory gained and resources captured
        if result == BattleResult.VICTORY:
            territory_gained = int(random.uniform(0.05, 0.15) * 100)  # 5-15% of territory
            resources_captured = int(random.uniform(0.1, 0.2) * defender.resources)  # 10-20% of resources
        else:
            territory_gained = 0
            resources_captured = 0
        
        return result, casualties_attacker, casualties_defender, territory_gained, resources_captured
    
    def _apply_casualties(self, country_id: int, total_casualties: int) -> None:
        """
        Apply casualties to military units
        
        Args:
            country_id: Country ID
            total_casualties: Total casualties to apply
        """
        units = self.get_military_units(country_id)
        
        # Calculate total strength
        total_strength = sum(unit.quantity * self.unit_strength[unit.unit_type] for unit in units)
        
        # If no units or strength, return
        if not units or total_strength == 0:
            return
        
        # Distribute casualties proportionally
        remaining_casualties = total_casualties
        
        for unit in units:
            unit_strength = unit.quantity * self.unit_strength[unit.unit_type]
            unit_proportion = unit_strength / total_strength
            
            # Calculate unit casualties
            unit_casualties = int(total_casualties * unit_proportion)
            unit_casualties = min(unit_casualties, unit.quantity)  # Can't lose more than we have
            
            # Apply casualties
            unit.quantity -= unit_casualties
            remaining_casualties -= unit_casualties * self.unit_strength[unit.unit_type]
        
        self.db.commit()
    
    def _generate_battle_report(
        self,
        attacker: Country,
        defender: Country,
        attacker_strength: int,
        defender_strength: int,
        result: BattleResult,
        casualties_attacker: int,
        casualties_defender: int,
        territory_gained: int,
        resources_captured: int
    ) -> str:
        """
        Generate battle report
        
        Args:
            attacker: Attacker country
            defender: Defender country
            attacker_strength: Attacker military strength
            defender_strength: Defender military strength
            result: Battle result
            casualties_attacker: Attacker casualties
            casualties_defender: Defender casualties
            territory_gained: Territory gained
            resources_captured: Resources captured
            
        Returns:
            str: Battle report
        """
        report = f"Battle Report: {attacker.name} vs {defender.name}\n"
        report += f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += f"Initial Forces:\n"
        report += f"- {attacker.name}: {attacker_strength} military strength\n"
        report += f"- {defender.name}: {defender_strength} military strength\n\n"
        
        # Add random battle events
        battle_events = [
            "The battle began with a surprise attack at dawn.",
            "Heavy rain made the battlefield muddy and difficult to navigate.",
            "Fog covered the battlefield, reducing visibility for both sides.",
            "The battle took place in mountainous terrain, giving defenders an advantage.",
            "Naval support provided additional firepower for the attacking forces.",
            "Air superiority played a crucial role in the battle outcome.",
            "Urban combat made progress slow and casualties high.",
            "Desert conditions caused equipment failures on both sides.",
            "A brilliant flanking maneuver changed the course of the battle.",
            "Superior logistics allowed for sustained combat operations."
        ]
        
        report += f"Battle Details:\n"
        report += f"- {random.choice(battle_events)}\n"
        report += f"- {random.choice(battle_events)}\n\n"
        
        report += f"Outcome: {result.value.upper()}\n\n"
        
        report += f"Casualties:\n"
        report += f"- {attacker.name}: {casualties_attacker} ({int(casualties_attacker/max(attacker_strength, 1)*100)}%)\n"
        report += f"- {defender.name}: {casualties_defender} ({int(casualties_defender/max(defender_strength, 1)*100)}%)\n\n"
        
        if result == BattleResult.VICTORY:
            report += f"Spoils of War:\n"
            report += f"- Territory Gained: {territory_gained}%\n"
            report += f"- Resources Captured: {resources_captured}\n"
        
        return report