from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from database.models import Country, Development, DevelopmentCategory, DevelopmentStatus
from utils.error_handler import ValidationError, ResourceError
from utils.logger import get_logger
from config import config

logger = get_logger("development_service")

class DevelopmentService:
    """Service for development-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Development options with costs and bonuses
        self.development_options = {
            DevelopmentCategory.INFRASTRUCTURE: [
                {
                    "name": "Road Network",
                    "description": "Improve road infrastructure to boost economy",
                    "cost": 200,
                    "time_days": 1,
                    "infrastructure_bonus": 0.05,
                    "research_bonus": 0,
                    "trade_bonus": 0.02
                },
                {
                    "name": "Power Grid",
                    "description": "Upgrade power generation and distribution",
                    "cost": 300,
                    "time_days": 2,
                    "infrastructure_bonus": 0.08,
                    "research_bonus": 0.01,
                    "trade_bonus": 0.01
                },
                {
                    "name": "Urban Development",
                    "description": "Expand and modernize cities",
                    "cost": 500,
                    "time_days": 3,
                    "infrastructure_bonus": 0.1,
                    "research_bonus": 0.02,
                    "trade_bonus": 0.03
                }
            ],
            DevelopmentCategory.RESEARCH: [
                {
                    "name": "Basic Research",
                    "description": "Fund basic scientific research",
                    "cost": 250,
                    "time_days": 2,
                    "infrastructure_bonus": 0,
                    "research_bonus": 0.05,
                    "trade_bonus": 0
                },
                {
                    "name": "Military Technology",
                    "description": "Develop advanced military technology",
                    "cost": 400,
                    "time_days": 3,
                    "infrastructure_bonus": 0,
                    "research_bonus": 0.08,
                    "trade_bonus": 0.01
                },
                {
                    "name": "Advanced Research Center",
                    "description": "Build a cutting-edge research facility",
                    "cost": 600,
                    "time_days": 5,
                    "infrastructure_bonus": 0.02,
                    "research_bonus": 0.12,
                    "trade_bonus": 0.02
                }
            ],
            DevelopmentCategory.TRADE: [
                {
                    "name": "Trade Agreements",
                    "description": "Negotiate favorable trade agreements",
                    "cost": 150,
                    "time_days": 1,
                    "infrastructure_bonus": 0,
                    "research_bonus": 0,
                    "trade_bonus": 0.05
                },
                {
                    "name": "Port Expansion",
                    "description": "Expand port facilities for international trade",
                    "cost": 350,
                    "time_days": 2,
                    "infrastructure_bonus": 0.03,
                    "research_bonus": 0,
                    "trade_bonus": 0.08
                },
                {
                    "name": "Global Trade Network",
                    "description": "Establish a global trade network",
                    "cost": 550,
                    "time_days": 4,
                    "infrastructure_bonus": 0.02,
                    "research_bonus": 0.01,
                    "trade_bonus": 0.15
                }
            ]
        }
    
    def get_development_options(self, category_str: str) -> List[Dict]:
        """
        Get development options for a category
        
        Args:
            category_str: Development category as string
            
        Returns:
            List[Dict]: List of development options
            
        Raises:
            ValidationError: If category is invalid
        """
        try:
            category = DevelopmentCategory(category_str)
        except ValueError:
            valid_categories = [c.value for c in DevelopmentCategory]
            raise ValidationError(
                f"Invalid development category: {category_str}",
                f"Invalid development category. Valid categories are: {', '.join(valid_categories)}"
            )
        
        return self.development_options[category]
    
    def get_active_developments(self, country_id: int) -> List[Development]:
        """
        Get active developments for a country
        
        Args:
            country_id: Country ID
            
        Returns:
            List[Development]: List of active developments
        """
        return self.db.query(Development).filter(
            Development.country_id == country_id,
            Development.status == DevelopmentStatus.IN_PROGRESS
        ).all()
    
    def get_completed_developments(self, country_id: int) -> List[Development]:
        """
        Get completed developments for a country
        
        Args:
            country_id: Country ID
            
        Returns:
            List[Development]: List of completed developments
        """
        return self.db.query(Development).filter(
            Development.country_id == country_id,
            Development.status == DevelopmentStatus.COMPLETED
        ).all()
    
    def start_development(
        self, 
        country_id: int, 
        category_str: str, 
        option_name: str
    ) -> Development:
        """
        Start a development project
        
        Args:
            country_id: Country ID
            category_str: Development category as string
            option_name: Development option name
            
        Returns:
            Development: Created development object
            
        Raises:
            ValidationError: If validation fails
            ResourceError: If not enough resources
        """
        # Validate category
        try:
            category = DevelopmentCategory(category_str)
        except ValueError:
            valid_categories = [c.value for c in DevelopmentCategory]
            raise ValidationError(
                f"Invalid development category: {category_str}",
                f"Invalid development category. Valid categories are: {', '.join(valid_categories)}"
            )
        
        # Find development option
        options = self.development_options[category]
        option = next((o for o in options if o["name"] == option_name), None)
        
        if not option:
            option_names = [o["name"] for o in options]
            raise ValidationError(
                f"Invalid development option: {option_name}",
                f"Invalid development option. Valid options for {category.value} are: {', '.join(option_names)}"
            )
        
        # Get country
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            raise ValidationError(
                f"Country with ID {country_id} not found",
                "Country not found. Please check your country ID."
            )
        
        # Check if enough resources
        if country.resources < option["cost"]:
            raise ResourceError(
                f"Not enough resources: {country.resources} < {option['cost']}",
                f"Not enough resources. {option['name']} costs {option['cost']} resources, but you only have {country.resources}."
            )
        
        # Calculate end time
        time_seconds = option["time_days"] * 86400  # Convert days to seconds
        end_time = datetime.utcnow() + timedelta(seconds=time_seconds)
        
        # Create development
        development = Development(
            country_id=country_id,
            category=category,
            name=option["name"],
            description=option["description"],
            resource_cost=option["cost"],
            start_time=datetime.utcnow(),
            end_time=end_time,
            status=DevelopmentStatus.IN_PROGRESS,
            infrastructure_bonus=option["infrastructure_bonus"],
            research_bonus=option["research_bonus"],
            trade_bonus=option["trade_bonus"]
        )
        
        # Update country resources
        country.resources -= option["cost"]
        country.last_updated = datetime.utcnow()
        
        # Log transaction
        transaction = TransactionLog(
            country_id=country_id,
            transaction_type="development",
            amount=-option["cost"],
            description=f"Started development: {option['name']}",
            timestamp=datetime.utcnow()
        )
        
        self.db.add(development)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(development)
        
        logger.info(f"Started development {option['name']} for country {country_id}")
        
        return development
    
    def check_completed_developments(self) -> List[Development]:
        """
        Check for completed developments
        
        Returns:
            List[Development]: List of newly completed developments
        """
        # Find developments that are in progress and past their end time
        completed = self.db.query(Development).filter(
            Development.status == DevelopmentStatus.IN_PROGRESS,
            Development.end_time <= datetime.utcnow()
        ).all()
        
        # Update status to completed
        for development in completed:
            development.status = DevelopmentStatus.COMPLETED
            
            # Apply bonuses to country
            country = self.db.query(Country).filter(Country.id == development.country_id).first()
            if country:
                # Apply bonuses (simplified for now)
                country.gdp = int(country.gdp * (1 + development.infrastructure_bonus))
                country.military_power = int(country.military_power * (1 + development.research_bonus))
                country.resources += int(country.resources * development.trade_bonus)
                country.last_updated = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Completed {len(completed)} developments")
        
        return completed
    
    def get_development_progress(self, development_id: int) -> Dict:
        """
        Get development progress
        
        Args:
            development_id: Development ID
            
        Returns:
            Dict: Development progress
            
        Raises:
            ValidationError: If development not found
        """
        development = self.db.query(Development).filter(Development.id == development_id).first()
        if not development:
            raise ValidationError(
                f"Development with ID {development_id} not found",
                "Development not found. Please check your development ID."
            )
        
        # Calculate progress
        now = datetime.utcnow()
        
        if development.status == DevelopmentStatus.COMPLETED:
            progress = 100
            time_left = 0
        elif development.status == DevelopmentStatus.CANCELLED:
            progress = 0
            time_left = 0
        else:
            total_time = (development.end_time - development.start_time).total_seconds()
            elapsed_time = (now - development.start_time).total_seconds()
            
            progress = min(100, int(elapsed_time / total_time * 100))
            time_left = max(0, (development.end_time - now).total_seconds())
        
        return {
            "id": development.id,
            "name": development.name,
            "category": development.category.value,
            "description": development.description,
            "cost": development.resource_cost,
            "start_time": development.start_time.isoformat(),
            "end_time": development.end_time.isoformat(),
            "status": development.status.value,
            "progress": progress,
            "time_left_seconds": time_left,
            "bonuses": {
                "infrastructure": development.infrastructure_bonus,
                "research": development.research_bonus,
                "trade": development.trade_bonus
            }
        }