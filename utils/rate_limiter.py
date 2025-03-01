from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import CommandLog, User
from utils.error_handler import RateLimitError
from utils.logger import get_logger

logger = get_logger("rate_limiter")

class RateLimiter:
    """Rate limiter to prevent command spam"""
    
    def __init__(self, db: Session):
        self.db = db
        self.limits = {
            # Command: (max_calls, period_seconds)
            "create_country": (1, 86400),  # 1 per day
            "attack": (5, 3600),  # 5 per hour
            "build_army": (10, 3600),  # 10 per hour
            "development": (5, 3600),  # 5 per hour
            "default": (30, 60),  # 30 per minute for other commands
        }
    
    def check_rate_limit(self, user_id: int, command: str) -> bool:
        """
        Check if a user has exceeded the rate limit for a command
        
        Args:
            user_id: Telegram user ID
            command: Command name
            
        Returns:
            bool: True if rate limit is not exceeded, False otherwise
            
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        # Get user from database
        user = self.db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            logger.warning(f"Rate limit check for unknown user: {user_id}")
            return True
        
        # Get rate limit for command
        max_calls, period_seconds = self.limits.get(command, self.limits["default"])
        period = timedelta(seconds=period_seconds)
        
        # Get command logs for this user and command within the period
        since = datetime.utcnow() - period
        count = self.db.query(CommandLog).filter(
            CommandLog.user_id == user.id,
            CommandLog.command == command,
            CommandLog.timestamp >= since
        ).count()
        
        # Check if rate limit is exceeded
        if count >= max_calls:
            logger.warning(f"Rate limit exceeded for user {user_id} on command {command}")
            wait_time = period_seconds // 60  # Convert to minutes
            raise RateLimitError(
                f"Rate limit exceeded for command {command}",
                f"You're using this command too frequently. Please wait {wait_time} minutes before trying again."
            )
        
        # Log the command
        log_entry = CommandLog(
            user_id=user.id,
            command=command,
            timestamp=datetime.utcnow()
        )
        self.db.add(log_entry)
        self.db.commit()
        
        return True