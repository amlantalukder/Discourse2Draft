from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from pydantic import BaseModel, Field
from ..utils import Config
from .common import StateContentManager, StateOutlineManager, extractLLMResponse
from .prompts import setPrompt
from pathlib import Path
from langchain.chains.summarize import load_summarize_chain
from ..vectordb import getLoader

class SummarizeSchema(BaseModel):
    '''
    Returns the summary of the provided content
    '''
    summary: str = Field(description='Summary of the provided content')

# ---------------------------------------------------------------------------
class Summarize:

    summarize_system_prompt = f'''\
    You are an expert on writing summary of a given content.
    <Instructions>
    - The summary must not contain more than {Config.NUM_TOKENS_SUMMARY} tokens. 
    - The summary must include all important aspects of a given content.
    </Instructions>
    '''

    summarize_human_prompt = '''
    <Content>
    {content}
    </Content>
    
    <Instructions>
    - Generate a comprehensive summary of the content.
    
    - Provide the output in the following format.
    {format_instructions}

    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm, input_field=None, output_field=None, dir_path_ref_files=None):

        self.input_field = input_field
        self.output_field = output_field
        self.dir_path_ref_files = Path(dir_path_ref_files) if (dir_path_ref_files is not None and Path(dir_path_ref_files).exists()) else None

        if self.dir_path_ref_files:
            self.summarize_chain = load_summarize_chain(llm=llm, chain_type='map_reduce')
        else:
            parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=SummarizeSchema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
            self.summarize_prompt = setPrompt(self.summarize_system_prompt, self.summarize_human_prompt, parser)
            self.summarize_chain = self.summarize_prompt | llm | parser

    def __call__(self, state: StateContentManager | StateOutlineManager):
        '''LLM generates summary for a given content'''

        if self.dir_path_ref_files:
            docs = []
            for file in Path(self.dir_path_ref_files).glob('*'):
                docs += getLoader(file)

            summary = self.summarize_chain.invoke(docs)

            return {self.output_field: summary, 'steps': ['Summarize']}

        return extractLLMResponse(task_name = 'Summarize', 
                                  chain = self.summarize_chain,
                                  kargs = {'content': state[self.input_field]},
                                  keys_to_find = ['summary'],
                                  value_names = [self.output_field])