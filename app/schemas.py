from pydantic import BaseModel


class PlayerBase(BaseModel):
    name: str
    mmr: int
    level: int


class PlayerCreate(PlayerBase):
    name: str
    mmr: int
    level: int
    password: str

class Player(PlayerBase):
    id: int
    name: str
    mmr: int
    level: int
    password: str

    class Config:
        orm_mode = True