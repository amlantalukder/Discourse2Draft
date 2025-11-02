from ..backend.ai.architecture import Architecture
from src.backend.db import generated_files_ai_architecture
from utils import Config
from dataclasses import dataclass

@dataclass
class ConfigApp:

    email: str = ''
    session_id: str = ''
    settings_id: int | None = None
    llm: str = ''
    temperature: float = 0.0
    instructions: str = ''
    file_name: str = ''
    outline: str = ''
    generated_files_id: int | None = None
    vector_db_collections_id: int | None = None
    vector_db_collections_id_lit_search: int | None = None
    is_writing: bool = False
    write_faster: bool = False
    agent: object | None = None

    def resetContentVars(self):

        self.file_name = ''
        self.outline = ''
        self.generated_files_id = None
        self.vector_db_collections_id = None
        self.vector_db_collections_id_lit_search = None
        self.is_writing = False
        self.write_faster = False

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
        
        self.agent = Architecture(model_name=self.llm, 
                                        temperature=self.temperature, 
                                        instructions=self.instructions, 
                                        type=ai_architecture,
                                        collection_name= vector_db_collection_name,
                                        collection_name_lit_search=vector_db_collection_name_lit_search).agent

