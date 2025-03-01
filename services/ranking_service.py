from typing import List, Dict
from sqlalchemy.orm import Session
from database.models import Country
from utils.logger import get_logger

logger = get_logger("ranking_service")

class RankingService:
    """Service for ranking-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_top_countries(self, limit: int = 10) -> List[Dict]:
        """
        Get top countries by military power
        
        Args:
            limit: Maximum number of countries to return
            
        Returns:
            List[Dict]: List of top countries
        """
        countries = self.db.query(Country).order_by(Country.military_power.desc()).limit(limit).all()
        
        result = []
        for i, country in enumerate(countries):
            result.append({
                "rank": i + 1,
                "id": country.id,
                "name": country.name,
                "military_power": country.military_power,
                "gdp": country.gdp,
                "population": country.population
            })
        
        return result
    
    def get_top_economies(self, limit: int = 10) -> List[Dict]:
        """
        Get top countries by GDP
        
        Args:
            limit: Maximum number of countries to return
            
        Returns:
            List[Dict]: List of top economies
        """
        countries = self.db.query(Country).order_by(Country.gdp.desc()).limit(limit).all()
        
        result = []
        for i, country in enumerate(countries):
            result.append({
                "rank": i + 1,
                "id": country.id,
                "name": country.name,
                "gdp": country.gdp,
                "military_power": country.military_power,
                "population": country.population
            })
        
        return result
    
    def get_top_populations(self, limit: int = 10) -> List[Dict]:
        """
        Get top countries by population
        
        Args:
            limit: Maximum number of countries to return
            
        Returns:
            List[Dict]: List of top populations
        """
        countries = self.db.query(Country).order_by(Country.population.desc()).limit(limit).all()
        
        result = []
        for i, country in enumerate(countries):
            result.append({
                "rank": i + 1,
                "id": country.id,
                "name": country.name,
                "population": country.population,
                "gdp": country.gdp,
                "military_power": country.military_power
            })
        
        return result
    
    def get_country_rank(self, country_id: int) -> Dict:
        """
        Get a country's rank in different categories
        
        Args:
            country_id: Country ID
            
        Returns:
            Dict: Country ranks
        """
        # Get country
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            return {
                "military_rank": None,
                "economy_rank": None,
                "population_rank": None,
                "total_countries": 0
            }
        
        # Count total countries
        total_countries = self.db.query(Country).count()
        
        # Get military rank
        military_rank = self.db.query(Country).filter(Country.military_power > country.military_power).count() + 1
        
        # Get economy rank
        economy_rank = self.db.query(Country).filter(Country.gdp > country.gdp).count() + 1
        
        # Get population rank
        population_rank = self.db.query(Country).filter(Country.population > country.population).count() + 1
        
        return {
            "military_rank": military_rank,
            "economy_rank": economy_rank,
            "population_rank": population_rank,
            "total_countries": total_countries
        }