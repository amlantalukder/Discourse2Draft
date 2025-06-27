from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from .utils import Config, State
from .prompts import setPrompt

class AnalyzeQuerySchema(BaseModel):
    '''
    Represents the list of keyphrases extracted from user query
    to get context on.
    '''
    keyphrases: list[str] = Field(f'List of maximum {Config.MAX_KEYWORDS} keyphrases', max_length=Config.MAX_KEYWORDS)

class AnalyzeQuery:

    analyze_query_system_prompt = (f'''
        You will be given a query. Analyze the query and find a list of independent 'keyphrases' on which you need information to answer the query. Always follow the rules below

        ** Rules **
        - List maximum of {Config.MAX_KEYWORDS} key phrases. THE LIST MUST NOT BE MORE THAN {Config.MAX_KEYWORDS}.
        - Answer the query in the JSON format
        '''
        +
        '''
        ```json
        {{
            "keyphrases": ["keyphrase 1", "keyphrase 2", "keyphrase 3", ...]
        }}
        ```
        ''')

    analyze_query_human_prompt = '''

        <Previous Content Summary>
        {content_pre}
        </Previous Content Summary>

        <Current Section>
        {current_section}
        </Current Section>

        <Instructions>
        - Read the Previous Content Summary.
        - Provide a list of keyphrases on which you need information to write text under the current section.

        - Provide the output in the following format.
        {format_instructions}
        
        - Output must be in JSON format with `json` tags.
        </Instructions>

        '''

    def __init__(self, llm):
        parser = parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=AnalyzeQuerySchema), llm=llm)
        self.analyze_query_prompt = setPrompt(self.analyze_query_system_prompt, 
                                              self.analyze_query_human_prompt, 
                                              parser)
        self.analyze_query_chain = self.analyze_query_prompt | llm | parser

    def __call__(self, state: State) -> State:
        '''
        Extracts keyphrases from user query
        '''

        response = self.analyze_query_chain.invoke(
            {
                'content_pre': state.get('content_pre'),
                'current_section': state.get('current_section')
            }
        )

        response = dict(response)['keyphrases']
        
        return {'keyphrases': response, 'steps': ['analyze_query']}