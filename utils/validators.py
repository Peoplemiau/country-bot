from typing import Dict, Any, List, Optional, Tuple
from utils.error_handler import ValidationError

class Validator:
    """Validator for command inputs"""
    
    @staticmethod
    def validate_country_name(name: str) -> str:
        """
        Validate country name
        
        Args:
            name: Country name
            
        Returns:
            str: Validated country name
            
        Raises:
            ValidationError: If validation fails
        """
        if not name:
            raise ValidationError("Country name cannot be empty")
        
        if len(name) < 3:
            raise ValidationError("Country name must be at least 3 characters long")
        
        if len(name) > 50:
            raise ValidationError("Country name must be at most 50 characters long")
        
        return name
    
    @staticmethod
    def validate_government_type(gov_type: str) -> str:
        """
        Validate government type
        
        Args:
            gov_type: Government type
            
        Returns:
            str: Validated government type
            
        Raises:
            ValidationError: If validation fails
        """
        valid_types = [
            "democracy", "monarchy", "dictatorship", "republic", 
            "theocracy", "communist", "socialist", "oligarchy"
        ]
        
        if not gov_type:
            raise ValidationError("Government type cannot be empty")
        
        gov_type = gov_type.lower()
        
        if gov_type not in valid_types:
            raise ValidationError(
                f"Invalid government type. Valid types are: {', '.join(valid_types)}"
            )
        
        return gov_type
    
    @staticmethod
    def validate_ideology(ideology: str) -> str:
        """
        Validate ideology
        
        Args:
            ideology: Ideology
            
        Returns:
            str: Validated ideology
            
        Raises:
            ValidationError: If validation fails
        """
        valid_ideologies = [
            "capitalist", "communist", "socialist", "fascist", 
            "liberal", "conservative", "nationalist", "religious", "progressive"
        ]
        
        if not ideology:
            raise ValidationError("Ideology cannot be empty")
        
        ideology = ideology.lower()
        
        if ideology not in valid_ideologies:
            raise ValidationError(
                f"Invalid ideology. Valid ideologies are: {', '.join(valid_ideologies)}"
            )
        
        return ideology
    
    @staticmethod
    def validate_unit_type(unit_type: str) -> str:
        """
        Validate military unit type
        
        Args:
            unit_type: Unit type
            
        Returns:
            str: Validated unit type
            
        Raises:
            ValidationError: If validation fails
        """
        valid_types = ["infantry", "tank", "ship", "aircraft"]
        
        if not unit_type:
            raise ValidationError("Unit type cannot be empty")
        
        unit_type = unit_type.lower()
        
        if unit_type not in valid_types:
            raise ValidationError(
                f"Invalid unit type. Valid types are: {', '.join(valid_types)}"
            )
        
        return unit_type
    
    @staticmethod
    def validate_quantity(quantity: str) -> int:
        """
        Validate quantity
        
        Args:
            quantity: Quantity as string
            
        Returns:
            int: Validated quantity
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            quantity = int(quantity)
        except ValueError:
            raise ValidationError("Quantity must be a number")
        
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")
        
        return quantity
    
    @staticmethod
    def validate_development_category(category: str) -> str:
        """
        Validate development category
        
        Args:
            category: Development category
            
        Returns:
            str: Validated category
            
        Raises:
            ValidationError: If validation fails
        """
        valid_categories = ["infrastructure", "research", "trade"]
        
        if not category:
            raise ValidationError("Development category cannot be empty")
        
        category = category.lower()
        
        if category not in valid_categories:
            raise ValidationError(
                f"Invalid development category. Valid categories are: {', '.join(valid_categories)}"
            )
        
        return category
    
    @staticmethod
    def validate_alliance_name(name: str) -> str:
        """
        Validate alliance name
        
        Args:
            name: Alliance name
            
        Returns:
            str: Validated alliance name
            
        Raises:
            ValidationError: If validation fails
        """
        if not name:
            raise ValidationError("Alliance name cannot be empty")
        
        if len(name) < 3:
            raise ValidationError("Alliance name must be at least 3 characters long")
        
        if len(name) > 50:
            raise ValidationError("Alliance name must be at most 50 characters long")
        
        return name