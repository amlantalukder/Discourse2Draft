from chromadb import HttpClient
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from .utils import Config
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document
from langchain_community.document_loaders import CSVLoader, JSONLoader
from langchain_unstructured import UnstructuredLoader
from pathlib import Path

class ChromaDB:

    def __init__(self, collection_name: str, embedding: str = 'text-embedding-3-large', delete_if_exists: bool = False):

        client = HttpClient(host=Config.env_config['CHROMA_HOST'],  port=Config.env_config['CHROMA_PORT'])

        self.embedding = OpenAIEmbeddings(
            model=embedding, 
            base_url=Config.env_config.get('AI_BASE_URL'), 
            api_key=Config.env_config.get('AI_API_KEY')
        )

        if delete_if_exists and collection_name in [c.name for c in client.list_collections()]:
            client.delete_collection(collection_name)

        self.vector_store = Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=self.embedding,
        )

        self.retriever = self.vector_store.as_retriever(search_type=Config.SIMILARITY_METRIC, 
                                                        search_kwargs={'k': Config.NUM_DOCS_MAX, 
                                                                        'score_threshold': Config.SIMILARITY_THRESHOLD
                                                                        }
                                                        )

    def add(self, docs: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True
        )

        all_splits = text_splitter.split_documents(docs)

        # Index chunks
        _ = self.vector_store.add_documents(documents=all_splits)

    def invoke(self, query: str):
        return self.retriever.invoke(query)

def getLoader(file_path: Path):

    assert file_path.suffix in [".csv", ".json", ".pdf", ".epub", ".doc", ".docx", ".txt", ".xlsm"], \
    'Provided file type is not supported. Only the following file types are supported, ".csv", ".json", ".pdf", ".epub", ".doc", ".docx", ".txt"'
        
    match file_path.suffix:
        case '.csv':
            loader = CSVLoader(file_path=file_path)
        case '.json':
            loader = JSONLoader(file_path=file_path)
        case _:
            loader = UnstructuredLoader(file_path=file_path)

    return loader.lazy_load()

def deleteCollection(collection_name: str):

    client = HttpClient(host=Config.env_config['CHROMA_HOST'],  port=Config.env_config['CHROMA_PORT'])

    if collection_name in [c.name for c in client.list_collections()]:
        client.delete_collection(collection_name)
    
