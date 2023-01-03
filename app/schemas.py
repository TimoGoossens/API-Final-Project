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

class ItemBase(BaseModel):
    name: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True