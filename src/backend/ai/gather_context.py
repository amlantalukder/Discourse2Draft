from ..vectordb import ChromaDB
from ..utils import Config
from .common import State
from rich import print

# ---------------------------------------------------------------------------
class GatherContext:

    def gatherContext(self, keyphrases):

        def formatContext(docs):
            
            def estimateTokenLimits(docs):

                est = []
            
                for kw, doc_list in docs.items():
                    est += [[len(d.metadata['app_file_id'].strip().split()) + 
                             len(d.metadata['app_file_name'].strip().split()) + 
                             len(d.page_content.strip().split()), kw, i] for i, d in enumerate(doc_list)]

                est = sorted(est)
                
                d_tok_est = {}
                token_limit = Config.TOKENS_PER_LLM_CALL
                for j, (s, k, i) in enumerate(est):
                    d_tok_est[k] = {**d_tok_est.get(k, {}), **{i: 0}}
                    d_tok_est[k][i] = min(s, token_limit//(len(est)-j))
                    token_limit -= d_tok_est[k][i]

                return d_tok_est

            d_tok_est = estimateTokenLimits(docs)

            docs_str = ''
            for kw, doc_list in docs.items():
                docs_str += f'\n\n**{kw}**'
                d_docs = {}
                for i, d in enumerate(doc_list):
                    try:
                        content = ' '.join(d.page_content.strip().split()[:d_tok_est[kw][i]])
                        file_id = d.metadata['app_file_id']
                        file_name = d.metadata['app_file_name']
                        d_docs[(file_id, file_name)] = d_docs.get((file_id, file_name), '') + content + '\n\n'
                    except Warning as w:
                        print(f'Resource retriever formatting: {str(w)}')

                for (file_id, file_name), content in d_docs.items():
                    docs_str += '\n\n' + f'''\
                    <{file_id}>
                        <Reference>{file_name}</Reference>
                        <Content>{content}</Content>
                    </{file_id}>
                    '''

            return docs_str
        
        self.docs_res = {}
        for kw in keyphrases[:Config.MAX_KEYPHRASES]:
            try:
                docs = self.db.invoke(kw)
                if len(docs): self.docs_res[kw] = docs
            except Warning as w:
                print(f'Resource retriever for keyphrase: {kw}: {str(w)}')

        return formatContext(self.docs_res)
    
    def __init__(self, collection_name):

        self.db = ChromaDB()
        self.db.get(collection_name=collection_name)

    def __call__(self, state: State) -> State:
        '''
        Gather context using keyphrases extracted from user query
        '''

        response = self.gatherContext(state.get('keyphrases'))
        
        return {'rag_context': response, 'steps': ['gather_context']}