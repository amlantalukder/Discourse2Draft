from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from ..utils import Config
from .common import StateContentManager, extractLLMResponse, Config
from .prompts import setPrompt

# ---------------------------------------------------------------------------
class WriteAbstractSchema(BaseModel):
    '''
    Returns the abstract content
    '''
    content: str = Field(description='Content of the abstract')

# ---------------------------------------------------------------------------
class WriteAbstract:

    write_abstract_system_prompt = '''
    You are an expert in writing abstracts from given content.

    <Instructions> 
    - Abstact must summarize the key points of the content provided.
    - The abstract should be concise (within 300 words), clear, and informative.
    - Avoid including any new information that is not present in the main content.
    - Avoid using technical jargon; the abstract should be understandable to a broad audience.
    - Avoid using citations or references in the abstract.
    </Instructions>'''

    write_abstract_human_prompt = lambda self, instructions: (f'''
    <Content>
    {{content}}
    </Content>
                                                              
    <Instructions>
    {instructions}
    
    - Provide the output in the following format.
    {{format_instructions}}
    </Instructions>
    ''')


    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=WriteAbstractSchema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.write_abstract_prompt = setPrompt(self.write_abstract_system_prompt, 
                                                 self.write_abstract_human_prompt(instructions),
                                                 parser)
        
        self.write_abstract_chain = self.write_abstract_prompt | llm | parser


    def __call__(self, state: StateContentManager):
        '''LLM generates an abstract content'''

        return extractLLMResponse(task_name = 'Write Abstract', 
                                  chain = self.write_abstract_chain,
                                  kargs = {'content': state['content_pre']},
                                  key_to_find = 'content',
                                  value_name = 'content')