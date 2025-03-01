from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import get_logger

logger = get_logger("error_handler")

class BotError(Exception):
    """Base exception class for bot errors"""
    def __init__(self, message, user_message=None):
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)

class ResourceError(BotError):
    """Exception raised when there are not enough resources"""
    pass

class PermissionError(BotError):
    """Exception raised when user doesn't have permission"""
    pass

class RateLimitError(BotError):
    """Exception raised when user hits rate limit"""
    pass

class ValidationError(BotError):
    """Exception raised when input validation fails"""
    pass

class DatabaseError(BotError):
    """Exception raised for database errors"""
    pass

async def global_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler for the bot"""
    # Log the error
    logger.error(f"Update {update} caused error: {context.error}")
    
    # Get the user that triggered the error
    user = update.effective_user
    
    # Send a message to the user
    error_message = "An unexpected error occurred. Please try again later."
    
    if isinstance(context.error, BotError):
        error_message = context.error.user_message
    
    if update.effective_message:
        await update.effective_message.reply_text(
            f"❌ Error: {error_message}"
        )

def handle_exceptions(func):
    """Decorator to handle exceptions in command handlers"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except BotError as e:
            logger.warning(f"Handled error in {func.__name__}: {e.message}")
            await update.effective_message.reply_text(f"❌ Error: {e.user_message}")
        except Exception as e:
            logger.exception(f"Unhandled error in {func.__name__}: {str(e)}")
            await update.effective_message.reply_text(
                "❌ An unexpected error occurred. The error has been logged."
            )
            # Re-raise for the global error handler
            raise
    
    return wrapper