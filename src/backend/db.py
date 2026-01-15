from pathlib import Path
import pandas as pd
import hashlib
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DateTime
from sqlalchemy.orm import mapped_column, Mapped, Session
from datetime import datetime
from typing import Literal, List, Optional
import dotenv
from enum import Enum
import logging
from utils import print_func_name

# -----------------------------------------------------------------------
@print_func_name
def encryptPassword(password):

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()
    # Convert the password to bytes and hash it
    hash_object.update(password.encode())
    # Get the hex digest of the hash
    return hash_object.hexdigest()

# -----------------------------------------------------------------------
class generated_files_status(Enum):

    CREATED = 'created' 
    RUNNING = 'running'
    SUCCESS = 'success' 
    ERROR = 'error' 
    CANCELLED = 'cancelled'
    DELETED = 'deleted'

# -----------------------------------------------------------------------
class generated_files_ai_architecture(Enum):

    BASE = 'base'
    RAG = 'rag'
    GRAPH_RAG = 'graphrag'

# -----------------------------------------------------------------------
class uploaded_files_status(Enum):

    UPLOADED = 'uploaded'
    DELETED = 'deleted'

# -----------------------------------------------------------------------
class vector_db_collections_type(Enum):

    UPLOADED_FILES = 'uploaded_files'
    LITERATURE = 'literature'

# -----------------------------------------------------------------------
class vector_db_collections_status(Enum):

    ACTIVE = 'active'
    DELETED = 'deleted'

# -----------------------------------------------------------------------
class Config:
    env_config = dotenv.dotenv_values(Path(".env"))

    generated_files_status_desc = {
        generated_files_status.CREATED.value: 'Created',
        generated_files_status.RUNNING.value: 'Writing in progress',
        generated_files_status.SUCCESS.value: 'Writing finished', 
        generated_files_status.ERROR.value: 'Writing stopped on error', 
        generated_files_status.CANCELLED.value: 'Writing stopped by user',
        generated_files_status.DELETED.value: 'Deleted'
    }
    
# -----------------------------------------------------------------------
Base = declarative_base()
    
# -----------------------------------------------------------------------
class Credentials(Base):

    __tablename__ = 'credentials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    email: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    password: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

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
    session: Mapped[str]
    llm: Mapped[str]
    temperature: Mapped[float]
    instructions: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])
    
# -----------------------------------------------------------------------
class GeneratedFiles(Base):

    __tablename__ = 'generated_files'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    email: Mapped[str]
    session: Mapped[str]
    file_name: Mapped[str]
    status: Mapped[str]
    settings_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('settings.id'))
    ai_architecture: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])

# -----------------------------------------------------------------------
class UploadedFiles(Base):

    __tablename__ = 'uploaded_files'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    email: Mapped[str]
    session: Mapped[str]
    file_name: Mapped[str]
    status: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])
    
# -----------------------------------------------------------------------
class Literature(Base):

    __tablename__ = 'literature'
    
    id: Mapped[str] = mapped_column(primary_key=True, index=True, unique=True)
    authors: Mapped[str]
    title: Mapped[str]
    year: Mapped[str]
    journal: Mapped[str]
    volume: Mapped[str]
    issue: Mapped[str]
    pages: Mapped[str]
    doi: Mapped[str]
    pmid: Mapped[Optional[str]]
    pmcid: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])
    
# -----------------------------------------------------------------------
class VectorDBCollections(Base):

    __tablename__ = 'vector_db_collections'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    email: Mapped[str]
    session: Mapped[str]
    type: Mapped[str]
    generated_files_id: Mapped[int] = mapped_column(sa.ForeignKey('generated_files.id'))
    status: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])

# -----------------------------------------------------------------------
class VectorDBCollectionFiles(Base):

    __tablename__ = 'vector_db_collection_files'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True, unique=True)
    vector_db_collections_id: Mapped[int] = mapped_column(sa.ForeignKey('vector_db_collections.id'))
    uploaded_files_id: Mapped[Optional[int]] = mapped_column(sa.ForeignKey('uploaded_files.id'))
    literature_id: Mapped[Optional[str]] = mapped_column(sa.ForeignKey('literature.id'))
    create_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __init__(self, data):
        for k in data:
            setattr(self, k, data[k])

    def __repr__(self):
        return '\n'.join([f'{k}: {v}' for k, v in self.__dict__.items()])


# -----------------------------------------------------------------------
try:
    engine = sa.create_engine(f'postgresql://{Config.env_config["USER"]}:{Config.env_config["PASSWORD"]}@{Config.env_config["HOST"]}/{Config.env_config["DATABASE"]}')
    Base.metadata.create_all(engine)
except Exception as exp:
    logging.error(exp)

# -----------------------------------------------------------------------
tables = {'credentials': Credentials, 
          'settings': Settings, 
          'generated_files': GeneratedFiles, 
          'uploaded_files': UploadedFiles,
          'literature': Literature,
          'vector_db_collections': VectorDBCollections,
          'vector_db_collection_files': VectorDBCollectionFiles}
    
# -----------------------------------------------------------------------
@print_func_name
def selectFromDB(table_name: str, 
                field_names: list, 
                field_values: list[list], 
                order_by_field_names: list = [], 
                order_by_types: List[Literal['ASC', 'DESC']] = [], 
                limit: int|None = None):

    table = tables[table_name]
    with Session(engine) as session:
        cursor = (session
                .query(table)
                .filter(*[getattr(table, name).in_(values) for name, values in zip(field_names, field_values)]) 
        )

        if order_by_field_names:
            if not order_by_types or len(order_by_types) < len(order_by_field_names): order_by_types = ['ASC'] * (len(order_by_field_names)-len(order_by_types))
            cursor = cursor.order_by(*[getattr(table, name).desc() if order_dir == 'DESC' else getattr(table, name).asc() for name, order_dir in zip(order_by_field_names, order_by_types)]) 
    
        if limit is not None:
            cursor = cursor.limit(limit)

        df = pd.DataFrame([c.__dict__ for c in cursor.all()])
        df = df.replace({float('nan'): None})

        return df
    
# -----------------------------------------------------------------------
@print_func_name
def insertIntoDB(table_name: str, field_names: list, field_values: list[list], 
                rel_field_names: list[str] = [], 
                rel_table_names: list[str] = [], 
                rel_table_field_names: list[list] = [], 
                rel_table_field_values: list[list[list]] = []):

    inserted_ids = []

    table = tables[table_name]
    with Session(engine) as session:
        
        for i, rel_field_name, rel_table_name in enumerate(zip(rel_field_names, rel_table_names)):
            table_rel = tables[rel_table_name]
            rel_field_obj_list = []
            df_data_rel = pd.DataFrame(dict(zip(rel_table_field_names[i], rel_table_field_values[i])))
            rel_table_field_names_row = list(df_data.columns)
            for i, rel_table_field_values_row in df_data_rel.iterrows():
                obj = table_rel(dict(zip(rel_table_field_names_row, rel_table_field_values_row)))
                rel_field_obj_list.append(obj)
            field_names.append(rel_field_name)
            field_values.append(rel_field_obj_list)
    
        df_data = pd.DataFrame(dict(zip(field_names, field_values)))
        field_names_row = list(df_data.columns)
        
        for i, field_values_row in df_data.iterrows():
            obj = table(dict(zip(field_names_row, field_values_row)))
            session.add(obj)
            session.commit()
            inserted_ids.append(obj.id)

    return inserted_ids

# -----------------------------------------------------------------------
@print_func_name
def updateDB(table_name: str, 
             update_fields: list, 
             update_values: list, 
             select_fields: list, 
             select_values: list[list]):

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