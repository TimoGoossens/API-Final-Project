from sqlalchemy.orm import Session

import models
import schemas


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
