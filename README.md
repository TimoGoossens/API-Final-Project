# **Welkom!**
> Hallo, in deze readme krijg je een overzicht van wat ik allemaal gedaan heb voor mijn API project.
## **inhoudstafel**
> Hier kan je zien wat je allemaal te wachten staat.

**1.Inleiding**

**2.Algemene eisen & documentatie (screenshots + uitleg)**

**3.Aanvulling front-end**

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
1. 
>![image](https://user-images.githubusercontent.com/91054406/211034680-7fddbd64-aaa6-45e4-b67d-f3700b0de94d.png)

>en hier zie je dat het met een bearer token wel lukt
![image](https://user-images.githubusercontent.com/91054406/211071528-252168ad-b287-4df6-bc3d-37ebbd708ba1.png)

2. 
>![image](https://user-images.githubusercontent.com/91054406/211045454-506f6ca9-f628-441e-80ea-d23ba8665762.png)
  
>ik heb ingelogd met test@test.com
>![image](https://user-images.githubusercontent.com/91054406/211072662-3a734fb6-3064-4531-be2c-5d45957dbd86.png)

>hier zie je dat het wel werkt met een bearer token
>![image](https://user-images.githubusercontent.com/91054406/211073014-ba65dfc2-edfa-4f0a-949b-ece74af160db.png)


>hier vraag je alle players op via postman
3. 
>![image](https://user-images.githubusercontent.com/91054406/211045088-091914df-b5ae-420a-a3ef-0085c0fd1125.png)

>hier vraag je een random pllayer op via postman
4. 
>![image](https://user-images.githubusercontent.com/91054406/211045646-19ae77d0-6cd9-4304-ba17-de1c2055f38d.png)

>hier vraag je naar een bepaalde player doormiddel van zijn/haar id via postman
5. 
>![image](https://user-images.githubusercontent.com/91054406/211045878-cc516228-ba5d-496a-9158-c63c8fe9d78a.png)

>**POST requests**

>hier maak je een player aan via postman

1. 
>![image](https://user-images.githubusercontent.com/91054406/211046404-7c84f48e-884a-4a64-9f70-58fbf9f491f2.png)

hier maak je een user aan via postman
2. 
>![image](https://user-images.githubusercontent.com/91054406/211074376-b9a10de3-799b-400f-b8b2-c57d4306f7fb.png)

>Ik weet niet of dit gaat in postman maar heb dit via openAPI /docs gedaan --> dit is om een bearer token te krijgen voor een user zodat deze acces heeft tot de Gets van users --> ik heb alleen de gets van users op authentication gezet.
3. 
>![Schermafbeelding 2023-01-06 185617](https://user-images.githubusercontent.com/91054406/211074636-fe6b4908-1fa2-480e-8677-bfbf52c701dc.png)
>![Schermafbeelding 2023-01-06 185638](https://user-images.githubusercontent.com/91054406/211074651-01a8678b-9571-4ad9-95a6-760ac56513b7.png)


>**PUT requests**

>hier verander ik Tester naar Tester2 via postman
1. 
>![image](https://user-images.githubusercontent.com/91054406/211050971-6ed84885-0aaa-4bbc-a150-9f2299cd8049.png)


>**DELETE requests**

>hier delete ik Tester2 via postman
1. 
>![image](https://user-images.githubusercontent.com/91054406/211051292-5993dc15-cae6-4920-90f2-6c3232a35f52.png)

### openapi /docs

>screenshot met volledige openapi --> niet ingelogd

![image](https://user-images.githubusercontent.com/91054406/211052143-2652a450-02dc-4294-899d-5e9286b83a42.png)

>screenshot met volledige openapi --> ingelogd

![image](https://user-images.githubusercontent.com/91054406/211075568-7a49fdfd-28ce-4eb8-9f9e-1dc84b250096.png)

>hier zie je dat ik inlog met test@test.com
>![image](https://user-images.githubusercontent.com/91054406/211072662-3a734fb6-3064-4531-be2c-5d45957dbd86.png)

>**Post requests**

>request 1 --> hier maak ik een speler aan met mijn naam
>![image](https://user-images.githubusercontent.com/91054406/211077181-5a93ef72-e38a-4028-8a54-68b3e478fafd.png)

>request 2 --> hier maak ik test@test.com aan
>![image](https://user-images.githubusercontent.com/91054406/211077378-9789d5ee-65c5-4efd-af38-a20178e050d4.png)

>request 3 --> hier maak ik een bearing token aan voor test@test.com
> ![Schermafbeelding 2023-01-06 185617](https://user-images.githubusercontent.com/91054406/211074636-fe6b4908-1fa2-480e-8677-bfbf52c701dc.png)
> ![Schermafbeelding 2023-01-06 185638](https://user-images.githubusercontent.com/91054406/211074651-01a8678b-9571-4ad9-95a6-760ac56513b7.png)

>**GET requests**

>request 1 --> hier vraag ik naar alle players die ik gemaakt heb --> Ik heb mijn volume moeten destroyen omdat mijn OAuth anders niet wilde werken daarom dat ik nu even maar 2 spelers laat zien in deze screenshot
>![image](https://user-images.githubusercontent.com/91054406/211078194-e2fe012f-9ce5-4982-8425-18b6bd0b561b.png)

>request 2 --> hier vraag ik een random speler uit de lijst van de spelers dit heb ik gedaan met import random (geleerd bij python)
>![image](https://user-images.githubusercontent.com/91054406/211078646-ed26ea6f-d6cf-4ec2-956e-8434fa171b54.png)

>request 3 --> hier vraag ik via het id van een player een bepaalde player op.
>![image](https://user-images.githubusercontent.com/91054406/211079084-8c90695d-0077-41c6-adc5-27d165c32e28.png)

>request 4 --> als ik niet ingelogd was dan had ik nu dit niet kunnen opvragen maar hier vraag ik de users die zich hebben toegevoegd.
>![image](https://user-images.githubusercontent.com/91054406/211079252-726bdb89-9947-485d-b9c8-14f47628ba79.png)

>request 5 --> zoals hierboven kan ik dit niet opvragen als er geen authenticatie is gebeurt --> ik vraag ik de current user op.
>![image](https://user-images.githubusercontent.com/91054406/211079721-c34a3a33-f6cf-4fa7-894e-b6cf08e35894.png)

>**PUT requests**

>bij deze PUT verander je de player via het ID van de player die je wilt aanpassen --> in de request body vul je in waar je de player in wilt veranderen. 
>![image](https://user-images.githubusercontent.com/91054406/211080677-16bcb210-6116-47e2-afc6-17f9f3272cb1.png)

>**DELETE requests**

>eerst heb ik even een player aangemaakt die ik kan verwijderen(zie screenshot hieronder)
>![image](https://user-images.githubusercontent.com/91054406/211081275-58bbc3da-dbc5-4fa6-ac6a-53a59ad3f0bc.png)

>hier is dan de DELETE request --> hiermee delete je een user op basis van zijn/haar id.
>![image](https://user-images.githubusercontent.com/91054406/211081525-803c36c8-4efd-40cf-b925-4b5a0441efcd.png)



### github actions en okteto

>dit is een screenshot van github actions van de repo "api-final-project"
>![image](https://user-images.githubusercontent.com/91054406/211086840-f36a29d0-4bed-4d94-9a64-2b8a5c6ffa7b.png)


```
FROM python:3.10.0-alpine
WORKDIR /code
EXPOSE 8000
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code
RUN mkdir -p /code/sqlitedb
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

>de image van de container wordt opgehaald van dockerhub --> door de github workflow.
>![image](https://user-images.githubusercontent.com/91054406/211089103-86d40394-6375-4f16-bd62-a2ecda63523c.png)

>hier is ook nog de code van requirements.txt --> als je wil dat iets geinstalleerd word zodat je bepaalde imports kunt gebruiken moet je het hier inzetten ik heb deze geinstalleerd:


```fastapi>=0.68.0,<0.69.0
pydantic>=1.8.0,<2.0.0
uvicorn>=0.15.0,<0.16.0
sqlalchemy==1.4.42
passlib[bcrypt,argon2]
python-jose[cryptography]
python-multipart
```

>dit zijn screenshots van okteto waar je kunt zien dat ik de containers laat runnen via docker-compose op okteto
>![image](https://user-images.githubusercontent.com/91054406/211087346-2987c74a-d67c-4fe4-b940-fb020220ca4f.png)

```version: "3.9"
services:
 system-service:
  image: timogoossens/api-final-project
  ports:
    - "8000:8000"
  volumes:
    - sqlite_playeritems_volume:/code/sqlitedb

volumes:
  sqlite_playeritems_volume:
  ```
 
## Aanvullingen: front-end

>Dit is de Github actions workflow van mijn front-end repo
>![image](https://user-images.githubusercontent.com/91054406/211108233-4c5ddfb3-bf47-4e84-ab55-c60b6f8bb9ed.png)

### eerste GET request van de site --> hier laat ik een tabel zien met daarin alle players
>![image](https://user-images.githubusercontent.com/91054406/211107453-fa27b908-3751-4380-aa7a-e82614f05e50.png)
>![image](https://user-images.githubusercontent.com/91054406/211094881-2d5a359d-68c3-4fb4-8cc8-10e742319bd6.png)

### tweede GET request van de site --> hier laat ik een random players zien als je op de knop drukt
>![image](https://user-images.githubusercontent.com/91054406/211095253-f50c6307-c129-4735-86f9-2d0bba3bb6c7.png)
>![image](https://user-images.githubusercontent.com/91054406/211095353-c8d82549-8cfb-4112-963e-bfe1fc8882b2.png)

### --> hier laat ik de speler zien die het laatste is aangemaakt
>![image](https://user-images.githubusercontent.com/91054406/211107539-3631c1ac-0cf3-43e4-bf11-d45436802f0c.png)


### eerste POST request van de site --> hier kan je een user aanmaken 
>![image](https://user-images.githubusercontent.com/91054406/211104157-30ceac37-4b45-4623-b32d-c5ad9c0254b8.png)
>![image](https://user-images.githubusercontent.com/91054406/211104194-d67905e3-16b9-4b33-96c4-60cf72767cfd.png)

### tweede POST request van de site --> hier kan je een player aanmaken
>![image](https://user-images.githubusercontent.com/91054406/211104590-f8d63989-998e-4890-914c-ddc671c53350.png)
>![image](https://user-images.githubusercontent.com/91054406/211104639-bb401d2d-42c5-47e0-a04c-3d233d8f60d7.png)

>jammer genoeg kunnen niet alle gets op de site gezet worden zoals bv. de GET request waar we om users vragen deze vereist een inlog en het zou ook niet logisch zijn om dit op een site te plaatsen.

## Slotwoord

> Het was een heel leuk project ik wil zo van deze dingen vaker doen maar liever niet zo kort voor een examen.
>Voor het eerste jaar dat dit vak recht staat vindt ik het een enorme prestatie van jullie!
>Ik hoop dat het allemaal een beetje duidelijk is en als er iets niet duidelijk is heb je nog altijd de code om na te kijken.
>Dit is het einde van mijn documentatie!




