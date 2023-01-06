# **Welkom!**
> Hallo, in deze readme krijg je een overzicht van wat ik allemaal gedaan heb voor mijn API project.
## **inhoudstafel**
> Hier kan je zien wat je allemaal te wachten staat.

**1.Inleiding**

**2.Algemene eisen & documentatie (screenshots + uitleg)**

**3.Eindresultaat**

**4.Slotwoord**

## 1.inleiding
> Voor het Final Project van API heb ik een API met minstens 1 POST, 3 GET's, 1 PUT en een DELETE endpoints enzovoort.
De API staat in verbinding met een database en dit wordt gerunned via okteto, vervolgens wordt de data via okteto doorgestuurd naar de webpagina op netlify.
> het Thema is nog altijd Rocket League.

## 2.algemene eisen & documentatie (screenshots + uitleg)

### Links

>Dit word gerunned op okteto in een cloud omgeving. [klik hier](https://system-service-timogoossens.cloud.okteto.net/)

>De webpagina staat op netlify [klik hier](https://timogoossens-api-final-project.netlify.app/)

>De repository voor de API [klik hier](https://github.com/TimoGoossens/api-final-project)

>De link naar de repository die gehost word op netlify [klik hier](https://github.com/TimoGoossens/TG-Final-Project.github.io)

### minstens 3 GET, 1 POST, 1 DELETE, 1 PUT endpoints
> zoals je ziet heb ik het minimum aantal endpoints bereikt.
![Schermafbeelding 2023-01-06 144904](https://user-images.githubusercontent.com/91054406/211025967-c5c66af1-9392-44d8-ba8d-1d8c2827f1f3.png)

### minstens 3 entiteiten(zie code in repo)
```
  from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
  from sqlalchemy.orm import relationship

  from database import Base


  class Player(Base):
      __tablename__ = "players"

      id = Column(Integer, primary_key=True, index=True)
      name = Column(String, unique=True, index=True)
      mmr = Column(Integer)
      level = Column(Integer)



  class User(Base):
      __tablename__ = "users"

      id = Column(Integer, primary_key=True, index=True) 
      email = Column(String, unique=True, index=True)
      hashed_password = Column(String)
      is_active = Column(Boolean, default=True)

      items = relationship("Item", back_populates="owner")


  class Item(Base):
      __tablename__ = "items"

      id = Column(Integer, primary_key=True, index=True)
      name = Column(String, index=True)
      description = Column(String, index=True)
      owner_id = Column(Integer, ForeignKey("users.id"))

      owner = relationship("User", back_populates="items")

```
### Implementatie van hashing en OAuth
>hier zie je dat ik OAuth heb gebruikt:
![image](https://user-images.githubusercontent.com/91054406/211028727-16418271-080d-4aa0-b308-d6b4f2b3da71.png)
![image](https://user-images.githubusercontent.com/91054406/211028811-c7d497af-784d-4571-a31d-01626c6e3171.png)

>hier zie je dat ik hashing heb gebruikt:
![image](https://user-images.githubusercontent.com/91054406/211029158-d5d57344-1cbb-47aa-b8f7-c8eeaa14ee9a.png)

### Totale API

>code voor de workflow met github --> en dockerhub

```
    name: Deliver container

    on: push

    jobs:
      delivery:
        runs-on: ubuntu-latest
        name: Deliver container
        steps:
          - name: Check out repository
            uses: actions/checkout@v1

          - name: Docker login
            run: docker login -u ${{ secrets.DOCKER_USER }} -p ${{ secrets.DOCKER_PASSWORD }}

          - name: Docker Build
            run: docker build -t ${{ secrets.DOCKER_USER }}/api-final-project:latest .

          - name: Upload container to Docker Hub with Push
            run: docker push ${{ secrets.DOCKER_USER }}/api-final-project:latest
```
>code van auth.py --> hierin zitten alle security features

```
    from passlib.context import CryptContext
    import crud
    from sqlalchemy.orm import Session
    from jose import JWTError, jwt
    from datetime import datetime, timedelta
    from fastapi.security import OAuth2PasswordBearer
    from fastapi import Depends, HTTPException, status

    # to get a string like this run:
    # openssl rand -hex 32
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

    def get_password_hash(password):
        return pwd_context.hash(password)

    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(db: Session, username: str, password: str):
        user = crud.get_user_by_email(db, username)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(data: dict):
        to_encode = data.copy()
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Default to 15 minutes of expiration time if ACCESS_TOKEN_EXPIRE_MINUTES variable is empty
            expire = datetime.utcnow() + timedelta(minutes=15)
        # Adding the JWT expiration time case
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = crud.get_user_by_email(db, username)
        if user is None:
            raise credentials_exception
        return user

    def get_current_active_user(db: Session, token: str = Depends(oauth2_scheme)):
        current_user = get_current_user(db, token)
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
```
>code van crud --> hierin komen alle functie die moeten uitgevoerd worden zoals bv. de spelers in de database zetten.
```
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
        hashed_password = auth.get_password_hash(player.password)
        db_player = db.query(models.Player).filter(models.Player.player_id == player_id).first()
        db_player.name = player.name
        db_player.mmr = player.mmr
        db_player.level = player.level
        db_player.password = hashed_password
        db.commit()
        db.refresh(db_player)
        return db_player

    def delete_player(db: Session, id: int):
        db_player = db.query(models.Player).filter(models.Player.id == id).first()
        db.delete(db_player)
        db.commit()
        db.refresh(db_player)
        return None
```
>code van database.py --> dit is de code waarmee er verbinding word gemaakt met de database.
```
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlitedb/sqlitedata.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```
>code voor main.py --> hier worden alle endpoints geconfigureerd en komen alle files samen.
```
from fastapi import Depends, FastAPI, HTTPException, Path, Query
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import random
import os
import crud
import models
import schemas
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import auth


print("We are in the main.......")
if not os.path.exists('.\sqlitedb'):
    print("Making folder.......")
    os.makedirs('.\sqlitedb')

print("Creating tables.......")
models.Base.metadata.create_all(bind=engine)
print("Tables created.......")

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/players/create/", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player_by_name(db, name=player.name)
    if db_player:
        raise HTTPException(status_code=400, detail="Name already registered")
    return crud.create_player(db=db, player=player)

@app.post("/users/create/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Name already registered")
    return crud.create_user(db=db, user=user)

@app.get("/players/", response_model=list[schemas.Player])
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = crud.get_players(db, skip=skip, limit=limit)
    return players


@app.get("/players/random/", response_model=schemas.Player)
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = crud.get_players(db, skip=skip, limit=limit)
    return random.choice(players)


@app.get("/players/{player_id}", response_model=schemas.Player)
def read_user(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

@app.put("/update/player/{player_id}", response_model=schemas.Player)
async def update_player(player: schemas.PlayerCreate, db: Session = Depends(get_db),player_id: int = Path(ge=0, le=60, default=1)):
    return crud.update_player(db=db, player=player, player_id=player_id)
    
@app.delete("/delete/player/{player_id}", response_model=schemas.Player)
async def delete_player(player: schemas.PlayerCreate, db: Session = Depends (get_db), player_id: int = Path(ge=0, le=60, default=1)):
    return crud.delete_player(db=db, player=player, player_id=player_id)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #Try to authenticate the user
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Add the JWT case sub with the subject(user)
    access_token = auth.create_access_token(
        data={"sub": user.email}
    )
    #Return the JWT as a bearer token to be placed in the headers
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/me", response_model=schemas.User)
def read_users_me(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_active_user(db, token)
    return current_user
```
>code voor models.py --> hierin worden de tables en de waardes gemaakt.
```
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    mmr = Column(Integer)
    level = Column(Integer)

    

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) 
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
```
>code voor schemas.py --> is er om classes aan te maken voor elke entetie
```
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    mmr = Column(Integer)
    level = Column(Integer)

    

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) 
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
```

### Postman
>**Get Requests**
>hier zie je ook dat de security werkt
1. ![image](https://user-images.githubusercontent.com/91054406/211034680-7fddbd64-aaa6-45e4-b67d-f3700b0de94d.png)
>en hier zie je dat het met een bearer token wel lukt
    ![image](https://user-images.githubusercontent.com/91054406/211071528-252168ad-b287-4df6-bc3d-37ebbd708ba1.png)

2. ![image](https://user-images.githubusercontent.com/91054406/211045454-506f6ca9-f628-441e-80ea-d23ba8665762.png)

3. ![image](https://user-images.githubusercontent.com/91054406/211045088-091914df-b5ae-420a-a3ef-0085c0fd1125.png)

4. ![image](https://user-images.githubusercontent.com/91054406/211045646-19ae77d0-6cd9-4304-ba17-de1c2055f38d.png)

5. ![image](https://user-images.githubusercontent.com/91054406/211045878-cc516228-ba5d-496a-9158-c63c8fe9d78a.png)
>**POST requests**

1. ![image](https://user-images.githubusercontent.com/91054406/211046404-7c84f48e-884a-4a64-9f70-58fbf9f491f2.png)
    
2. 

3. 

>**PUT requests**

>hier verander ik Tester naar Tester2
1. ![image](https://user-images.githubusercontent.com/91054406/211050971-6ed84885-0aaa-4bbc-a150-9f2299cd8049.png)


>**DELETE requests**

>hier delete ik Tester2
1. ![image](https://user-images.githubusercontent.com/91054406/211051292-5993dc15-cae6-4920-90f2-6c3232a35f52.png)

### openapi /docs

![image](https://user-images.githubusercontent.com/91054406/211052143-2652a450-02dc-4294-899d-5e9286b83a42.png)










      



