import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

from backend.database import SessionLocal, engine, Base
from backend.models import User, Comment

load_dotenv()

# Cria as tabelas do banco de dados (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurações usando variáveis de ambiente
CLIENT_ID = os.getenv("CLIENT_ID", "1519752401945362582")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "jN36MSochAWLlkshS7qYyekCorJtiUz3")

# URL do frontend (ajuste se estiver rodando em outra porta)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500/discord_profile/frontend/index.html")

REDIRECT_URI = "http://localhost:8000/auth/discord/callback"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================
# MODELS
# ==========================

class CommentCreate(BaseModel):
    user_id: int
    author_name: str
    content: str


# ==========================
# HOME
# ==========================

@app.get("/")
def home():
    return {"status": "online"}


# ==========================
# LOGIN DISCORD
# ==========================

@app.get("/login")
def login():

    discord_url = (
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=identify"
    )

    return RedirectResponse(discord_url)


# ==========================
# CALLBACK DISCORD
# ==========================

@app.get("/auth/discord/callback")
def discord_callback(code: str):

    token_response = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    token_data = token_response.json()

    if "access_token" not in token_data:
        return token_data

    access_token = token_data["access_token"]

    user_response = requests.get(
        "https://discord.com/api/users/@me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    user_data = user_response.json()

    db = SessionLocal()

    user = (
        db.query(User)
        .filter(User.discord_id == user_data["id"])
        .first()
    )

    avatar_url = None

    if user_data.get("avatar"):
        avatar_url = (
            f"https://cdn.discordapp.com/avatars/"
            f"{user_data['id']}/"
            f"{user_data['avatar']}.png"
        )

    if not user:

        user = User(
            discord_id=user_data["id"],
            username=user_data["username"],
            global_name=user_data.get("global_name"),
            avatar=avatar_url,
            bio="Meu perfil no MuralDisc",
            profile_slug=user_data["username"].lower()
        )

        db.add(user)

    else:

        user.username = user_data["username"]
        user.global_name = user_data.get("global_name")
        user.avatar = avatar_url

    db.commit()
    db.refresh(user)

    # Redireciona de volta para o frontend com o ID do usuário na URL
    redirect_url = f"{FRONTEND_URL}?user_id={user.id}"
    return RedirectResponse(url=redirect_url)


# ==========================
# USUÁRIOS
# ==========================

@app.get("/users")
def get_users():

    db: Session = SessionLocal()

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "discord_id": user.discord_id,
            "username": user.username,
            "global_name": user.global_name,
            "avatar": user.avatar,
            "bio": user.bio,
            "profile_slug": user.profile_slug
        }
        for user in users
    ]

@app.get("/users/{user_id}")
def get_user(user_id: int):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return {"error": "User not found"}
        
    return {
        "id": user.id,
        "discord_id": user.discord_id,
        "username": user.username,
        "global_name": user.global_name,
        "avatar": user.avatar,
        "bio": user.bio,
        "profile_slug": user.profile_slug
    }


# ==========================
# COMENTÁRIOS
# ==========================

@app.get("/comments/{user_id}")
def get_comments(user_id: int):

    db: Session = SessionLocal()

    comments = (
        db.query(Comment)
        .filter(Comment.user_id == user_id)
        .all()
    )

    return [
        {
            "author": comment.author_name,
            "content": comment.content
        }
        for comment in comments
    ]


@app.post("/comments")
def create_comment(data: CommentCreate):

    db = SessionLocal()

    comment = Comment(
        user_id=data.user_id,
        author_name=data.author_name,
        content=data.content
    )

    db.add(comment)
    db.commit()

    return {
        "success": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)