from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database.models import Country, Achievement, CountryAchievement
from utils.logger import get_logger

logger = get_logger("achievement_service")

class AchievementService:
    """Service for achievement-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Achievement definitions
        self.achievements = [
            # Military achievements
            {
                "name": "Military Beginner",
                "description": "Build your first military unit",
                "category": "military"
            },
            {
                "name": "Military Enthusiast",
                "description": "Have at least 1000 infantry units",
                "category": "military"
            },
            {
                "name": "Tank Commander",
                "description": "Have at least 100 tank units",
                "category": "military"
            },
            {
                "name": "Naval Power",
                "description": "Have at least 50 ship units",
                "category": "military"
            },
            {
                "name": "Air Superiority",
                "description": "Have at least 50 aircraft units",
                "category": "military"
            },
            {
                "name": "Superpower",
                "description": "Reach military power of 50",
                "category": "military"
            },
            
            # Economy achievements
            {
                "name": "Economic Beginner",
                "description": "Reach GDP of $2 billion",
                "category": "economy"
            },
            {
                "name": "Economic Growth",
                "description": "Reach GDP of $10 billion",
                "category": "economy"
            },
            {
                "name": "Economic Power",
                "description": "Reach GDP of $100 billion",
                "category": "economy"
            },
            {
                "name": "Economic Superpower",
                "description": "Reach GDP of $1 trillion",
                "category": "economy"
            },
            {
                "name": "Resource Hoarder",
                "description": "Accumulate 10,000 resources",
                "category": "economy"
            },
            
            # Development achievements
            {
                "name": "Developer",
                "description": "Complete your first development project",
                "category": "development"
            },
            {
                "name": "Infrastructure Expert",
                "description": "Complete 5 infrastructure projects",
                "category": "development"
            },
            {
                "name": "Research Pioneer",
                "description": "Complete 5 research projects",
                "category": "development"
            },
            {
                "name": "Trade Magnate",
                "description": "Complete 5 trade projects",
                "category": "development"
            },
            
            # Battle achievements
            {
                "name": "First Blood",
                "description": "Win your first battle",
                "category": "battle"
            },
            {
                "name": "Warmonger",
                "description": "Win 10 battles",
                "category": "battle"
            },
            {
                "name": "Conqueror",
                "description": "Win 50 battles",
                "category": "battle"
            },
            {
                "name": "Survivor",
                "description": "Survive 10 battles as defender",
                "category": "battle"
            },
            
            # Alliance achievements
            {
                "name": "Diplomat",
                "description": "Join your first alliance",
                "category": "alliance"
            },
            {
                "name": "Alliance Founder",
                "description": "Found an alliance",
                "category": "alliance"
            },
            {
                "name": "Popular Alliance",
                "description": "Have an alliance with 5 or more members",
                "category": "alliance"
            },
            
            # Misc achievements
            {
                "name": "Newcomer",
                "description": "Create your first country",
                "category": "misc"
            },
            {
                "name": "Active Player",
                "description": "Play for 7 consecutive days",
                "category": "misc"
            },
            {
                "name": "Veteran",
                "description": "Play for 30 consecutive days",
                "category": "misc"
            }
        ]
    
    def initialize_achievements(self) -> None:
        """
        Initialize achievements in the database
        """
        # Check if achievements already exist
        count = self.db.query(Achievement).count()
        if count > 0:
            logger.info(f"Achievements already initialized ({count} found)")
            return
        
        # Create achievements
        for achievement_data in self.achievements:
            achievement = Achievement(
                name=achievement_data["name"],
                description=achievement_data["description"],
                category=achievement_data["category"]
            )
            self.db.add(achievement)
        
        self.db.commit()
        logger.info(f"Initialized {len(self.achievements)} achievements")
    
    def get_achievement_by_name(self, name: str) -> Optional[Achievement]:
        """
        Get an achievement by name
        
        Args:
            name: Achievement name
            
        Returns:
            Optional[Achievement]: Achievement object if found, None otherwise
        """
        return self.db.query(Achievement).filter(Achievement.name == name).first()
    
    def get_country_achievements(self, country_id: int) -> List[Dict]:
        """
        Get all achievements for a country
        
        Args:
            country_id: Country ID
            
        Returns:
            List[Dict]: List of achievements
        """
        country_achievements = self.db.query(CountryAchievement).filter(
            CountryAchievement.country_id == country_id
        ).all()
        
        result = []
        for ca in country_achievements:
            achievement = ca.achievement
            result.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "category": achievement.category,
                "achieved_at": ca.achieved_at.isoformat()
            })
        
        return result
    
    def award_achievement(self, country_id: int, achievement_name: str) -> Optional[Achievement]:
        """
        Award an achievement to a country
        
        Args:
            country_ I'll continue from where I left off with the achievement_service.py file:

<boltArtifact id="geopolitical-simulation-bot-continued" title="Geopolitical Simulation Telegram Bot (Continued)">