from pathlib import Path
import pandas as pd
import hashlib
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, Mapped, Session
from datetime import datetime
import dotenv

# -----------------------------------------------------------------------
def encryptPassword(password):

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()
    # Convert the password to bytes and hash it
    hash_object.update(password.encode())
    # Get the hex digest of the hash
    return hash_object.hexdigest()

# -----------------------------------------------------------------------
class Config:
    env_config = dotenv.dotenv_values(Path(".env"))

engine = sa.create_engine(f'postgresql://{Config.env_config["USER"]}:{Config.env_config["PASSWORD"]}@{Config.env_config["HOST"]}/{Config.env_config["DATABASE"]}')
Base = declarative_base()
    
# -----------------------------------------------------------------------
class Credentials(Base):

    __tablename__ = 'credentials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    email: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    password: Mapped[str]
    update_date: Mapped[datetime]

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])

# -----------------------------------------------------------------------
class Sessions(Base):

    __tablename__ = 'sessions'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    email: Mapped[str]
    session: Mapped[str]
    file_name: Mapped[str]
    file_status: Mapped[str]
    create_date: Mapped[datetime]
    update_date: Mapped[datetime]
    llm: Mapped[str]
    temperature: Mapped[float]

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])

# -----------------------------------------------------------------------
class Settings(Base):

    __tablename__ = 'settings'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    email: Mapped[str]
    llm: Mapped[str]
    temperature: Mapped[float]
    instructions: Mapped[str]
    update_date: Mapped[datetime]

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])

# -----------------------------------------------------------------------
Base.metadata.create_all(engine)

# -----------------------------------------------------------------------
tables = {'credentials': Credentials, 'sessions': Sessions, 'settings': Settings}

# -----------------------------------------------------------------------
def selectFromDB(table_name: str, field_names: list, field_values: list[list]):
    table = tables[table_name]
    with Session(engine) as session:
        cursor = (session
                  .query(table)
                  .filter(*[getattr(table, name).in_(values) for name, values in zip(field_names, field_values)])
        )
        return pd.DataFrame([c.__dict__ for c in cursor.all()])
    
# -----------------------------------------------------------------------
def insertIntoDB(table_name: str, field_names: list, field_values: list[list]):
    table = tables[table_name]
    with Session(engine) as session:
        df_data = pd.DataFrame(dict(zip(field_names, field_values)))
        field_names = list(df_data.columns)
        for i, field_values in df_data.iterrows():
            obj = table(dict(zip(field_names, field_values)))
            session.add(obj)
            session.commit()

# -----------------------------------------------------------------------
def updateDB(table_name: str, update_fields: list, update_values: list, select_fields: list, select_values: list[list]):

    table = tables[table_name]
    with Session(engine) as session:
        cursor = (session
                  .query(table)
                  .filter(*[getattr(table, name).in_(values) for name, values in zip(select_fields, select_values)])
        )
        for obj in cursor.all():
            for k, v in zip(update_fields, update_values):
                setattr(obj, k, v)

        session.commit()
