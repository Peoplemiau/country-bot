from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from database.models import Country, Alliance, country_alliance
from utils.error_handler import ValidationError, PermissionError
from utils.logger import get_logger

logger = get_logger("alliance_service")

class AllianceService:
    """Service for alliance-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_alliance_by_id(self, alliance_id: int) -> Optional[Alliance]:
        """
        Get an alliance by ID
        
        Args:
            alliance_id: Alliance ID
            
        Returns:
            Optional[Alliance]: Alliance object if found, None otherwise
        """
        return self.db.query(Alliance).filter(Alliance.id == alliance_id).first()
    
    def get_alliance_by_name(self, name: str) -> Optional[Alliance]:
        """
        Get an alliance by name
        
        Args:
            name: Alliance name
            
        Returns:
            Optional[Alliance]: Alliance object if found, None otherwise
        """
        return self.db.query(Alliance).filter(Alliance.name == name).first()
    
    def get_country_alliances(self, country_id: int) -> List[Alliance]:
        """
        Get all alliances a country is a member of
        
        Args:
            country_id: Country ID
            
        Returns:
            List[Alliance]: List of alliance objects
        """
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            return []
        
        return country.alliances
    
    def create_alliance(self, founder_id: int, name: str, description: str = None) -> Alliance:
        """
        Create a new alliance
        
        Args:
            founder_id: Founder country ID
            name: Alliance name
            description: Alliance description
            
        Returns:
            Alliance: Created alliance object
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if alliance name already exists
        existing_alliance = self.get_alliance_by_name(name)
        if existing_alliance:
            raise ValidationError(
                f"Alliance with name '{name}' already exists",
                f"An alliance with the name '{name}' already exists. Please choose a different name."
            )
        
        # Check if founder country exists
        founder = self.db.query(Country).filter(Country.id == founder_id).first()
        if not founder:
            raise ValidationError(
                f"Country with ID {founder_id} not found",
                "Founder country not found. Please check your country ID."
            )
        
        # Create alliance
        alliance = Alliance(
            name=name,
            description=description,
            founder_id=founder_id
        )
        
        self.db.add(alliance)
        self.db.commit()
        self.db.refresh(alliance)
        
        # Add founder as member
        self.join_alliance(founder_id, alliance.id)
        
        logger.info(f"Created new alliance: {alliance}")
        
        return alliance
    
    def join_alliance(self, country_id: int, alliance_id: int) -> None:
        """
        Add a country to an alliance
        
        Args:
            country_id: Country ID
            alliance_id: Alliance ID
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if country exists
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            raise ValidationError(
                f"Country with ID {country_id} not found",
                "Country not found. Please check your country ID."
            )
        
        # Check if alliance exists
        alliance = self.get_alliance_by_id(alliance_id)
        if not alliance:
            raise ValidationError(
                f"Alliance with ID {alliance_id} not found",
                "Alliance not found. Please check the alliance ID."
            )
        
        # Check if already a member
        if alliance in country.alliances:
            raise ValidationError(
                f"Country {country_id} is already a member of alliance {alliance_id}",
                f"Your country is already a member of the {alliance.name} alliance."
            )
        
        # Add country to alliance
        country.alliances.append(alliance)
        self.db.commit()
        
        logger.info(f"Country {country.name} joined alliance {alliance.name}")
    
    def leave_alliance(self, country_id: int, alliance_id: int) -> None:
        """
        Remove a country from an alliance
        
        Args:
            country_id: Country ID
            alliance_id: Alliance ID
            
        Raises:
            ValidationError: If validation fails
            PermissionError: If country is the founder
        """
        # Check if country exists
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            raise ValidationError(
                f"Country with ID {country_id} not found",
                "Country not found. Please check your country ID."
            )
        
        # Check if alliance exists
        alliance = self.get_alliance_by_id(alliance_id)
        if not alliance:
            raise ValidationError(
                f"Alliance with ID {alliance_id} not found",
                "Alliance not found. Please check the alliance ID."
            )
        
        # Check if a member
        if alliance not in country.alliances:
            raise ValidationError(
                f"Country {country_id} is not a member of alliance {alliance_id}",
                f"Your country is not a member of the {alliance.name} alliance."
            )
        
        # Check if founder
        if alliance.founder_id == country_id:
            raise PermissionError(
                f"Country {country_id} is the founder of alliance {alliance_id}",
                f"You are the founder of the {alliance.name} alliance. You must disband the alliance or transfer leadership before leaving."
            )
        
        # Remove country from alliance
        country.alliances.remove(alliance)
        self.db.commit()
        
        logger.info(f"Country {country.name} left alliance {alliance.name}")
    
    def disband_alliance(self, country_id: int, alliance_id: int) -> None:
        """
        Disband an alliance
        
        Args:
            country_id: Country ID of the founder
            alliance_id: Alliance ID
            
        Raises:
            ValidationError: If validation fails
            PermissionError: If country is not the founder
        """
        # Check if alliance exists
        alliance = self.get_alliance_by_id(alliance_id)
        if not alliance:
            raise ValidationError(
                f"Alliance with ID {alliance_id} not found",
                "Alliance not found. Please check the alliance ID."
            )
        
        # Check if founder
        if alliance.founder_id != country_id:
            raise PermissionError(
                f"Country {country_id} is not the founder of alliance {alliance_id}",
                f"You are not the founder of the {alliance.name} alliance. Only the founder can disband the alliance."
            )
        
        # Remove all members
        for country in alliance.members:
            country.alliances.remove(alliance)
        
        # Delete alliance
        self.db.delete(alliance)
        self.db.commit()
        
        logger.info(f"Alliance {alliance.name} disbanded")
    
    def get_alliance_details(self, alliance_id: int) -> Dict:
        """
        Get alliance details
        
        Args:
            alliance_id: Alliance ID
            
        Returns:
            Dict: Alliance details
            
        Raises:
            ValidationError: If alliance not found
        """
        alliance = self.get_alliance_by_id(alliance_id)
        if not alliance:
            raise ValidationError(
                f"Alliance with ID {alliance_id} not found",
                "Alliance not found. Please check the alliance ID."
            )
        
        # Get founder
        founder = self.db.query(Country).filter(Country.id == alliance.founder_id).first()
        
        # Format members
        members = []
        for country in alliance.members:
            members.append({
                "id": country.id,
                "name": country.name,
                "is_founder": country.id == alliance.founder_id
            })
        
        # Format alliance details
        details = {
            "id": alliance.id,
            "name": alliance.name,
            "description": alliance.description,
            "founder": {
                "id": founder.id if founder else None,
                "name": founder.name if founder else "Unknown"
            },
            "members": members,
            "member_count": len(members),
            "created_at": alliance.created_at.isoformat()
        }
        
        return details