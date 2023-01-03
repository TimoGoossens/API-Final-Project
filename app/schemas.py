from pydantic import BaseModel


class PlayerBase(BaseModel):
    name: str
    mmr: int
    level: int

class PlayerCreate(PlayerBase):
    name: str
    mmr: int
    level: int

class Player(PlayerBase):
    id: int
    name: str
    mmr: int
    level: int
    

    class Config:
        orm_mode = True

