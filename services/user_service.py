from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from database.models import User
from utils.logger import get_logger

logger = get_logger("user_service")

class UserService:
    """Service for user-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Get a user by Telegram ID
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def create_user(self, telegram_id: int, username: Optional[str] = None) -> User:
        """
        Create a new user
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            
        Returns:
            User: Created user object
        """
        user = User(
            telegram_id=telegram_id,
            username=username,
            registered_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Created new user: {user}")
        
        return user
    
    def get_or_create_user(self, telegram_id: int, username: Optional[str] = None) -> User:
        """
        Get a user by Telegram ID or create a new one if not found
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            
        Returns:
            User: User object
        """
        user = self.get_user_by_telegram_id(telegram_id)
        
        if not user:
            user = self.create_user(telegram_id, username)
        else:
            # Update username and last active time
            user.username = username
            user.last_active = datetime.utcnow()
            self.db.commit()
        
        return user
    
    def update_last_active(self, user_id: int) -> None:
        """
        Update user's last active time
        
        Args:
            user_id: User ID
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if user:
            user.last_active = datetime.utcnow()
            self.db.commit()