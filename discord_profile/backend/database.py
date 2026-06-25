import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Pegando a URL do banco do arquivo .env (com um valor padrão de erro caso não exista)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@host/dbname")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()