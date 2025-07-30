from chromadb import HttpClient
from langchain_chroma import Chroma
from .ai.llms import getAIModel
from .utils import Config
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_graph_retriever.transformers import ShreddingTransformer
from langchain_graph_retriever.adapters.chroma import ChromaAdapter
from langchain_graph_retriever import GraphRetriever
from graph_retriever.strategies import Eager
from langchain_core.documents.base import Document
from langchain_community.document_loaders import CSVLoader, JSONLoader, PyPDFLoader
from langchain_unstructured import UnstructuredLoader
from pathlib import Path
import truststore
truststore.inject_into_ssl()

class ChromaDB:

    def __init__(self, embedding: str = 'text-embedding-3-large'):

        self.client = HttpClient(host=Config.env_config['CHROMA_HOST'],  port=Config.env_config['CHROMA_PORT'])

        self.embedding = getAIModel(model_name=embedding, is_embedding=True)

    def create(self, collection_name: str, delete_if_exists: bool = False):

        if delete_if_exists and collection_name in self.client.list_collections():
            self.client.delete_collection(collection_name)

        self.vector_store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embedding,
            create_collection_if_not_exists=True
        )

    def get(self, collection_name: str, is_graph: bool = False):

        self.vector_store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embedding,
            create_collection_if_not_exists=False
        )

        if not is_graph:
            self.retriever = self.vector_store.as_retriever(search_type=Config.SIMILARITY_METRIC, 
                                                        search_kwargs={'k': Config.NUM_DOCS_MAX, 
                                                                        'score_threshold': Config.SIMILARITY_THRESHOLD
                                                                        }
                                                        )
        else:    
            self.retriever = GraphRetriever(store=self.vector_store, 
                                            strategy = Eager(select_k=Config.NUM_DOCS_MAX, start_k=Config.NUM_DOCS_MAX, max_depth=2))

    def add(self, docs: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200, is_graph: bool = False):

        if not is_graph:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap,
                length_function=len,
                add_start_index=True
            )

            document_chunks = text_splitter.split_documents(docs)
        else:
            shredder = ShreddingTransformer()
            document_chunks = list(shredder.transform_documents(docs))

        # Index chunks
        _ = self.vector_store.add_documents(documents=document_chunks)

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
        case '.pdf':
            loader = PyPDFLoader(file_path=file_path)
        case _:
            loader = UnstructuredLoader(file_path=file_path)

    return loader.lazy_load()

def deleteCollection(collection_name: str):

    client = ChromaDB().client

    if collection_name in client.list_collections():
        client.delete_collection(collection_name)
    
