import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class Config(BaseModel):
    # Bot configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///geopolitical_sim.db")
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Game configuration
    DAILY_UPDATE_TIME: str = "00:00"  # UTC time for daily updates
    
    # Game balance settings
    MIN_POPULATION: int = 1_000_000  # 1M
    MAX_POPULATION: int = 1_000_000_000  # 1B
    MIN_GDP: int = 1_000_000_000  # $1B
    MAX_GDP: int = 100_000_000_000_000  # $100T
    MIN_MILITARY_POWER: int = 1
    MAX_MILITARY_POWER: int = 100
    
    # Cooldown settings (in seconds)
    ATTACK_COOLDOWN: int = 3600  # 1 hour
    BUILD_COOLDOWN: int = 1800  # 30 minutes
    DEVELOPMENT_COOLDOWN: int = 3600  # 1 hour
    
    # Development time settings (in seconds)
    MIN_DEVELOPMENT_TIME: int = 86400  # 1 day
    MAX_DEVELOPMENT_TIME: int = 604800  # 7 days
    
    # Diplomatic relations range
    MIN_RELATIONS: int = -100
    MAX_RELATIONS: int = 100
    
    # Resource settings
    INITIAL_RESOURCES: int = 1000
    DAILY_RESOURCE_GAIN: int = 100
    
    # Military maintenance costs (per unit per day)
    INFANTRY_MAINTENANCE: int = 1
    TANK_MAINTENANCE: int = 5
    SHIP_MAINTENANCE: int = 10
    AIRCRAFT_MAINTENANCE: int = 8

config = Config()