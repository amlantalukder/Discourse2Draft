from ..vectordb import ChromaDB
from ..utils import Config
from .common import StateContentManager
from rich import print
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs.networkx_graph import NetworkxEntityGraph
from .llms import getAIModel
import asyncio
import nest_asyncio
import logging

nest_asyncio.apply()

# ---------------------------------------------------------------------------
class GatherContextGraph:
    
    def gatherContext(self, keyphrases):
        
        graph_documents = []
        d_docs_by_file_id = {}
        for kw in keyphrases[:Config.MAX_KEYPHRASES]:
            try:
                docs = self.db.invoke(kw)
                for d in docs:
                    app_file_id = d.metadata['app_file_id']
                    d_docs_by_file_id[app_file_id] = d_docs_by_file_id.get(app_file_id, []) + [d]
            except Warning as w:
                logging.info(f'Resource retriever for keyphrase: {kw}: {str(w)}')

        d_nx_graph = {}
        for app_file_id, docs in d_docs_by_file_id.items():
            graph_documents = asyncio.run(self.llm_transformer.aconvert_to_graph_documents(docs))
            nx_graph = NetworkxEntityGraph()
            for g in graph_documents:
                for n in g.nodes:
                    nx_graph.add_node(n.id)

                for r in g.relationships:
                    nx_graph._graph.add_edge(r.source.id, r.target.id, relation=r.type)

            d_nx_graph[app_file_id] = nx_graph

        return d_nx_graph

    def __init__(self, llm, collection_name):

        self.db = ChromaDB()
        self.db.get(collection_name=collection_name)
        #self.llm_transformer = LLMGraphTransformer(llm=llm)
        self.llm_transformer = LLMGraphTransformer(llm=getAIModel(model_name='azure-gpt-4o'))

    def __call__(self, state: StateContentManager) -> StateContentManager:
        '''
        Gather context using keyphrases extracted from user query
        '''

        d_nx_graph = self.gatherContext(state.get('keyphrases'))
        
        return {'graphrag_context': d_nx_graph, 'steps': ['Gather context graph']}