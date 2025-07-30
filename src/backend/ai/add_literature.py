from langchain_core.documents.base import Document
from langsmith import traceable
from ..utils import Config
from .common import State
from .tools.search_pubmed import search_pubmed_article_async, formatAPA
from ..vectordb import ChromaDB
from ..db import selectFromDB, insertIntoDB
from datetime import datetime
import asyncio
import nest_asyncio

nest_asyncio.apply()

class AddLiterature:

    @traceable
    def addLiteratureToVectorDBCollection(self, literature_list: list[dict]):

        docs = [Document(page_content=lit['content'].strip(), metadata={'app_file_id': lit['ref_doi'], 'app_file_name': lit['ref']}) for lit in literature_list]
        self.db.add(docs=docs)
    
    def __init__(self, collection_name: str):
        self.db = ChromaDB()
        self.collection_name = collection_name
        self.db.get(collection_name=collection_name)
    
    def addLiterature(self, ref_id, ref):

        current_time = datetime.now()

        vector_db_collections_id = int(self.collection_name.split('_')[-1])

        records = selectFromDB(table_name='vector_db_collection_files',
                               field_names=['vector_db_collections_id', 'literature_id'],
                               field_values=[[vector_db_collections_id], [ref_id]])
        
        if not records.empty: return

        records = selectFromDB(table_name='literature',
                               field_names=['id'],
                               field_values=[[ref_id]],
                               limit=1)
        
        if records.empty:

            insertIntoDB(table_name='literature',
                                field_names=['id', 'authors', 'title', 'year', 'journal', 'volume', 'issue', 'pages', 'doi', 'pmcid', 'pmid', 'create_date', 'update_date'],
                                field_values=[[ref_id], [str(ref['authors'])], [ref['title']], [ref['year']], [ref['journal']], [ref['volume']], 
                                              [ref['issue']], [ref['pages']], [ref['doi']], [ref['pmcid']], [ref.get('pmid')], [current_time], [current_time]])
            
        insertIntoDB(table_name='vector_db_collection_files', 
                    field_names=['vector_db_collections_id', 'literature_id', 'create_date', 'update_date'],
                    field_values=[[vector_db_collections_id], [ref_id], [current_time], [current_time]])

    async def gatherLiterature(self, queries):

        literature_list_all = []
        for query in queries:
            literature_list = await search_pubmed_article_async(query=query, max_results=1, api_key=Config.env_config['NCBI_API_KEY'])
            literature_list_all += literature_list
        return literature_list_all
        
    @traceable
    def __call__(self, state: State):
        '''Adds literature to vector database'''

        literature_list = asyncio.run(self.gatherLiterature(queries=state['keyphrases']))
        
        refs_in_db = set()
        literature_list_filtered = []
        for lit in literature_list:
            ref = lit['ref']
            ref_doi = ref['doi']
            if ref_doi not in refs_in_db:
                literature_list_filtered.append({'ref_doi': ref_doi, 'ref': formatAPA(ref), 'content': lit['content'].strip()})
                self.addLiterature(ref_doi, ref)
                refs_in_db.add(ref_doi)
        
        if literature_list_filtered: self.addLiteratureToVectorDBCollection(literature_list_filtered[:Config.NUM_MAX_LITERATURE])

