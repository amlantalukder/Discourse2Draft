
from ..backend.ai.architecture import (ContentWriterArchitecture,
                                       AbstractSectionDetectorArchitecture,
                                       AbstractWriterArchitecture)
from src.backend.db import generated_files_ai_architecture
from utils import Config
from dataclasses import dataclass
from enum import Enum

class ContentGenerationScope(Enum):
    DO_NOT_GENERATE = 'Do Not Generate'
    GENERATE_IF_NEEDED = 'Generate Content If Needed'

class SpecialSectionTypes(Enum):
    CONTENT = 'content'

class ContentTypes(Enum):
    IS_ABSTRACT = 'is_abstract'
    INSTRUCTIONS = 'instructions'
    CONTENT_USER = 'content_user'
    CONTENT_AI = 'content_ai'
    CONTENT_PRE_SUMMARY = 'content_pre_summary'
    CONCEPT_MAP = 'concept_map'

@dataclass
class ConfigApp:

    email: str = ''
    session_id: str = ''
    settings_id: int | None = None
    llm: str = Config.env_config['DEFAULT_AI_MODEL']
    temperature: float = 0.0
    instructions: str = ''
    file_name: str = ''
    outline: str = ''
    generated_files_id: int | None = None
    vector_db_collections_id: int | None = None
    vector_db_collections_id_lit_search: int | None = None
    is_writing: bool = False
    agent: object | None = None
    agent_abstract_detector: object | None = None
    agent_abstract_writer: object | None = None

    def resetContentVars(self):

        self.file_name = ''
        self.outline = ''
        self.generated_files_id = None
        self.vector_db_collections_id = None
        self.vector_db_collections_id_lit_search = None
        self.is_writing = False

    def setAgent(self):
        
        ai_architecture = generated_files_ai_architecture.BASE.value

        if self.vector_db_collections_id:
            vector_db_collection_name = f'{Config.APP_NAME_AS_PREFIX}_collection_{self.vector_db_collections_id}'
            ai_architecture = generated_files_ai_architecture.RAG.value
        else:
            vector_db_collection_name = ''

        if self.vector_db_collections_id_lit_search:
            vector_db_collection_name_lit_search = f'{Config.APP_NAME_AS_PREFIX}_collection_{self.vector_db_collections_id_lit_search}'
            ai_architecture = generated_files_ai_architecture.RAG.value
        else:
            vector_db_collection_name_lit_search = ''
        
        self.agent = ContentWriterArchitecture(model_name=self.llm, 
                                        temperature=self.temperature, 
                                        instructions=self.instructions, 
                                        type=ai_architecture,
                                        collection_name= vector_db_collection_name,
                                        collection_name_lit_search=vector_db_collection_name_lit_search).agent
        
        self.agent_abstract_detector = AbstractSectionDetectorArchitecture().agent
        self.agent_abstract_writer = AbstractWriterArchitecture().agent
        
    def __repr__(self):
        return f'''ConfigApp(email={self.email}, 
            session_id={self.session_id}, 
            settings_id={self.settings_id}, 
            llm={self.llm}, 
            temperature={self.temperature}, 
            instructions={self.instructions}, 
            file_name={self.file_name}, 
            outline={self.outline}, 
            generated_files_id={self.generated_files_id}, 
            vector_db_collections_id={self.vector_db_collections_id}, 
            vector_db_collections_id_lit_search={self.vector_db_collections_id_lit_search}, 
            is_writing={self.is_writing},
            agent={self.agent},
            agent_abstract_detector={self.agent_abstract_detector},
            agent_abstract_writer={self.agent_abstract_writer})'''

