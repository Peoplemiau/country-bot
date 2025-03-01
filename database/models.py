from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Table, Enum, Text, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from database import Base
from config import config

# Association table for country alliances
country_alliance = Table(
    'country_alliance',
    Base.metadata,
    Column('country_id', Integer, ForeignKey('countries.id')),
    Column('alliance_id', Integer, ForeignKey('alliances.id'))
)

# Enum types
import enum

class GovernmentType(enum.Enum):
    DEMOCRACY = "democracy"
    MONARCHY = "monarchy"
    DICTATORSHIP = "dictatorship"
    REPUBLIC = "republic"
    THEOCRACY = "theocracy"
    COMMUNIST = "communist"
    SOCIALIST = "socialist"
    OLIGARCHY = "oligarchy"

class Ideology(enum.Enum):
    CAPITALIST = "capitalist"
    COMMUNIST = "communist"
    SOCIALIST = "socialist"
    FASCIST = "fascist"
    LIBERAL = "liberal"
    CONSERVATIVE = "conservative"
    NATIONALIST = "nationalist"
    RELIGIOUS = "religious"
    PROGRESSIVE = "progressive"

class UnitType(enum.Enum):
    INFANTRY = "infantry"
    TANK = "tank"
    SHIP = "ship"
    AIRCRAFT = "aircraft"

class DevelopmentCategory(enum.Enum):
    INFRASTRUCTURE = "infrastructure"
    RESEARCH = "research"
    TRADE = "trade"

class DevelopmentStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class BattleResult(enum.Enum):
    VICTORY = "victory"
    DEFEAT = "defeat"
    DRAW = "draw"

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    countries = relationship("Country", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"

# Country model
class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    government_type = Column(Enum(GovernmentType), nullable=False)
    ideology = Column(Enum(Ideology), nullable=False)
    population = Column(Integer, nullable=False)
    gdp = Column(BigInteger, nullable=False)
    military_power = Column(Integer, nullable=False)
    resources = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(f'population >= {config.MIN_POPULATION} AND population <= {config.MAX_POPULATION}'),
        CheckConstraint(f'gdp >= {config.MIN_GDP} AND gdp <= {config.MAX_GDP}'),
        CheckConstraint(f'military_power >= {config.MIN_MILITARY_POWER} AND military_power <= {config.MAX_MILITARY_POWER}'),
    )
    
    # Relationships
    user = relationship("User", back_populates="countries")
    military_units = relationship("MilitaryUnit", back_populates="country")
    diplomatic_relations = relationship("DiplomaticRelation", 
                                       foreign_keys="[DiplomaticRelation.country_id]",
                                       back_populates="country")
    developments = relationship("Development", back_populates="country")
    battles_as_attacker = relationship("Battle", 
                                      foreign_keys="[Battle.attacker_id]",
                                      back_populates="attacker")
    battles_as_defender = relationship("Battle", 
                                      foreign_keys="[Battle.defender_id]",
                                      back_populates="defender")
    alliances = relationship("Alliance", secondary=country_alliance, back_populates="members")
    achievements = relationship("CountryAchievement", back_populates="country")
    
    def __repr__(self):
        return f"<Country(id={self.id}, name={self.name}, user_id={self.user_id})>"

# Military Unit model
class MilitaryUnit(Base):
    __tablename__ = "military_units"
    
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    unit_type = Column(Enum(UnitType), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    technology_level = Column(Integer, nullable=False, default=1)
    
    # Relationships
    country = relationship("Country", back_populates="military_units")
    
    def __repr__(self):
        return f"<MilitaryUnit(id={self.id}, country_id={self.country_id}, unit_type={self.unit_type}, quantity={self.quantity})>"

# Diplomatic Relations model
class DiplomaticRelation(Base):
    __tablename__ = "diplomatic_relations"
    
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    target_country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    relation_value = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(f'relation_value >= {config.MIN_RELATIONS} AND relation_value <= {config.MAX_RELATIONS}'),
    )
    
    # Relationships
    country = relationship("Country", foreign_keys=[country_id], back_populates="diplomatic_relations")
    target_country = relationship("Country", foreign_keys=[target_country_id])
    
    def __repr__(self):
        return f"<DiplomaticRelation(country_id={self.country_id}, target_country_id={self.target_country_id}, relation_value={self.relation_value})>"

# Development model
class Development(Base):
    __tablename__ = "developments"
    
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    category = Column(Enum(DevelopmentCategory), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    resource_cost = Column(Integer, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(DevelopmentStatus), nullable=False, default=DevelopmentStatus.IN_PROGRESS)
    infrastructure_bonus = Column(Float, nullable=True)
    research_bonus = Column(Float, nullable=True)
    trade_bonus = Column(Float, nullable=True)
    
    # Relationships
    country = relationship("Country", back_populates="developments")
    
    def __repr__(self):
        return f"<Development(id={self.id}, country_id={self.country_id}, category={self.category}, name={self.name})>"

# Alliance model
class Alliance(Base):
    __tablename__ = "alliances"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    founder_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    founder = relationship("Country", foreign_keys=[founder_id])
    members = relationship("Country", secondary=country_alliance, back_populates="alliances")
    
    def __repr__(self):
        return f"<Alliance(id={self.id}, name={self.name}, founder_id={self.founder_id})>"

# Battle model
class Battle(Base):
    __tablename__ = "battles"
    
    id = Column(Integer, primary_key=True)
    attacker_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    defender_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    attacker_strength = Column(Integer, nullable=False)
    defender_strength = Column(Integer, nullable=False)
    result = Column(Enum(BattleResult), nullable=False)
    casualties_attacker = Column(Integer, nullable=False, default=0)
    casualties_defender = Column(Integer, nullable=False, default=0)
    territory_gained = Column(Integer, nullable=False, default=0)
    resources_captured = Column(Integer, nullable=False, default=0)
    battle_date = Column(DateTime, default=datetime.utcnow)
    battle_report = Column(Text, nullable=True)
    
    # Relationships
    attacker = relationship("Country", foreign_keys=[attacker_id], back_populates="battles_as_attacker")
    defender = relationship("Country", foreign_keys=[defender_id], back_populates="battles_as_defender")
    
    def __repr__(self):
        return f"<Battle(id={self.id}, attacker_id={self.attacker_id}, defender_id={self.defender_id}, result={self.result})>"

# Achievement model
class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(255), nullable=False)
    
    # Relationships
    country_achievements = relationship("CountryAchievement", back_populates="achievement")
    
    def __repr__(self):
        return f"<Achievement(id={self.id}, name={self.name})>"

# Country Achievement model (many-to-many relationship)
class CountryAchievement(Base):
    __tablename__ = "country_achievements"
    
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    achieved_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    country = relationship("Country", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="country_achievements")
    
    def __repr__(self):
        return f"<CountryAchievement(country_id={self.country_id}, achievement_id={self.achievement_id})>"

# Transaction Log model
class TransactionLog(Base):
    __tablename__ = "transaction_logs"
    
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    transaction_type = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    country = relationship("Country")
    
    def __repr__(self):
        return f"<TransactionLog(id={self.id}, country_id={self.country_id}, transaction_type={self.transaction_type}, amount={self.amount})>"

# Command Log model (for rate limiting and anti-cheat)
class CommandLog(Base):
    __tablename__ = "command_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    command = Column(String(255), nullable=False)
    arguments = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<CommandLog(id={self.id}, user_id={self.user_id}, command={self.command})>"