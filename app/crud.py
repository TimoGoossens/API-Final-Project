from sqlalchemy.orm import Session

import auth
import models
import schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()


def get_player_by_name(db: Session, name: str):
    return db.query(models.Player).filter(models.Player.name == name).first()


def get_player_by_mmr(db: Session, mmr: int):
    return db.query(models.Player).filter(models.Player.mmr == mmr).first()


def get_player_by_level(db: Session, level: int):
    return db.query(models.Player).filter(models.Player.level == level).first()


def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()


def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(name=player.name, mmr=player.mmr, level=player.level)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def update_player(db: Session, player_id: int, player: schemas.PlayerCreate):
    db_player = db.query(models.Player).filter(models.Player.player_id == player_id).first()
    db_player.name = player.name
    db_player.mmr = player.mmr
    db_player.level = player.level
    db.commit()
    db.refresh(db_player)
    return db_player

def delete_player(db: Session, id: int):
    db_player = db.query(models.Player).filter(models.Player.id == id).first()
    db.delete(db_player)
    db.commit()
    db.refresh(db_player)
    return None