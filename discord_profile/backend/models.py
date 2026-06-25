from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    discord_id = Column(String(50))
    username = Column(String(100))
    global_name = Column(String(100))
    avatar = Column(String(255))
    banner = Column(String(255))
    bio = Column(Text)
    profile_slug = Column(String(100))

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    author_name = Column(String(100))
    content = Column(Text)