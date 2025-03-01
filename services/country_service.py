from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from database.models import Country, User, GovernmentType, Ideology, MilitaryUnit, UnitType
from utils.error_handler import ValidationError, ResourceError, PermissionError
from utils.logger import get_logger
from config import config

logger = get_logger("country_service")

class CountryService:
    """Service for country-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_country_by_id(self, country_id: int) -> Optional[Country]:
        """
        Get a country by ID
        
        Args:
            country_id: Country ID
            
        Returns:
            Optional[Country]: Country object if found, None otherwise
        """
        return self.db.query(Country).filter(Country.id == country_id).first()
    
    def get_country_by_name(self, name: str) -> Optional[Country]:
        """
        Get a country by name
        
        Args:
            name: Country name
            
        Returns:
            Optional[Country]: Country object if found, None otherwise
        """
        return self.db.query(Country).filter(Country.name == name).first()
    
    def get_countries_by_user_id(self, user_id: int) -> List[Country]:
        """
        Get all countries owned by a user
        
        Args:
            user_id: User ID
            
        Returns:
            List[Country]: List of country objects
        """
        return self.db.query(Country).filter(Country.user_id == user_id).all()
    
    def create_country(
        self, 
        user_id: int, 
        name: str, 
        government_type: str, 
        ideology: str
    ) -> Country:
        """
        Create a new country
        
        Args:
            user_id: User ID
            name: Country name
            government_type: Government type
            ideology: Ideology
            
        Returns:
            Country: Created country object
            
        Raises:
            ValidationError: If validation fails
            ResourceError: If user already has a country
        """
        # Check if country name already exists
        existing_country = self.get_country_by_name(name)
        if existing_country:
            raise ValidationError(
                f"Country with name '{name}' already exists",
                f"A country with the name '{name}' already exists. Please choose a different name."
            )
        
        # Check if user already has a country
        user_countries = self.get_countries_by_user_id(user_id)
        if user_countries:
            raise ResourceError(
                f"User {user_id} already has a country",
                "You already have a country. You can only have one country at a time."
            )
        
        # Create country
        try:
            gov_type_enum = GovernmentType(government_type)
            ideology_enum = Ideology(ideology)
        except ValueError as e:
            raise ValidationError(str(e))
        
        # Set initial values
        initial_population = 1_000_000  # 1M
        initial_gdp = 1_000_000_000  # $1B
        initial_military_power = 10
        
        country = Country(
            name=name,
            user_id=user_id,
            government_type=gov_type_enum,
            ideology=ideology_enum,
            population=initial_population,
            gdp=initial_gdp,
            military_power=initial_military_power,
            resources=config.INITIAL_RESOURCES,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        self.db.add(country)
        self.db.commit()
        self.db.refresh(country)
        
        # Create initial military units
        self._create_initial_military_units(country.id)
        
        logger.info(f"Created new country: {country}")
        
        return country
    
    def _create_initial_military_units(self, country_id: int) -> None:
        """
        Create initial military units for a country
        
        Args:
            country_id: Country ID
        """
        # Create initial units
        initial_units = [
            (UnitType.INFANTRY, 100),
            (UnitType.TANK, 10),
            (UnitType.SHIP, 5),
            (UnitType.AIRCRAFT, 5)
        ]
        
        for unit_type, quantity in initial_units:
            unit = MilitaryUnit(
                country_id=country_id,
                unit_type=unit_type,
                quantity=quantity,
                technology_level=1
            )
            self.db.add(unit)
        
        self.db.commit()
        logger.info(f"Created initial military units for country {country_id}")
    
    def get_country_status(self, country_id: int) -> dict:
        """
        Get country status
        
        Args:
            country_id: Country ID
            
        Returns:
            dict: Country status
            
        Raises:
            ValidationError: If country not found
        """
        country = self.get_country_by_id(country_id)
        if not country:
            raise ValidationError(
                f"Country with ID {country_id} not found",
                "Country not found. Please check your country ID."
            )
        
        # Get military units
        military_units = self.db.query(MilitaryUnit).filter(
            MilitaryUnit.country_id == country_id
        ).all()
        
        # Format military units
        military_info = {}
        for unit in military_units:
            military_info[unit.unit_type.value] = {
                "quantity": unit.quantity,
                "technology_level": unit.technology_level
            }
        
        # Calculate total military strength
        total_strength = sum(unit.quantity * unit.technology_level for unit in military_units)
        
        # Format country status
        status = {
            "id": country.id,
            "name": country.name,
            "government_type": country.government_type.value,
            "ideology": country.ideology.value,
            "population": country.population,
            "gdp": country.gdp,
            "military_power": country.military_power,
            "resources": country.resources,
            "military": {
                "units": military_info,
                "total_strength": total_strength
            },
            "created_at": country.created_at.isoformat(),
            "last_updated": country.last_updated.isoformat()
        }
        
        return status
    
    def update_resources(self, country_id: int, amount: int, description: str) -> Tuple[int, int]:
        """
        Update country resources
        
        Args:
            country_id: Country ID
            amount: Amount to add (positive) or subtract (negative)
            description: Transaction description
            
        Returns:
            Tuple[int, int]: (Previous resources, New resources)
            
        Raises:
            ValidationError: If country not found
            ResourceError: If not enough resources
        """
        country = self.get_country_by_id(country_id)
        if not country:
            raise ValidationError(
                f"Country with ID {country_id} not found",
                "Country not found. Please check your country ID."
            )
        
        previous_resources = country.resources
        
        # Check if enough resources for negative amount
        if amount < 0 and country.resources + amount < 0:
            raise ResourceError(
                f"Not enough resources: {country.resources} < {abs(amount)}",
                f"Not enough resources. You need {abs(amount)} but only have {country.resources}."
            )
        
        # Update resources
        country.resources += amount
        country.last_updated = datetime.utcnow()
        
        # Log transaction
        transaction = TransactionLog(
            country_id=country_id,
            transaction_type="resources",
            amount=amount,
            description=description,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"Updated resources for country {country_id}: {previous_resources} -> {country.resources}")
        
        return previous_resources, country.resources
    
    def check_ownership(self, country_id: int, user_id: int) -> bool:
        """
        Check if a user owns a country
        
        Args:
            country_id: Country ID
            user_id: User ID
            
        Returns:
            bool: True if user owns the country, False otherwise
            
        Raises:
            ValidationError: If country not found
            PermissionError: If user doesn't own the country
        """
        country = self.get_country_by_id(country_id)
        if not country:
            raise ValidationError(
                f"Country with ID {country_id} not found",
                "Country not found. Please check your country ID."
            )
        
        if country.user_id != user_id:
            raise PermissionError(
                f"User {user_id} doesn't own country {country_id}",
                "You don't have permission to perform this action on this country."
            )
        
        return True