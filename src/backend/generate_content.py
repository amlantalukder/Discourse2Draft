from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from .utils import State, retryInvoke
from .prompts import setPrompt

class GenerateContentSchema(BaseModel):
    '''
    Returns the content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')

# ---------------------------------------------------------------------------
class GenerateContent:

    generate_content_system_prompt = lambda self, instructions: f'''\
    <Instructions>
    {instructions}
    </Instructions>
    '''

    generate_content_human_prompt = '''
    <Previous Content Summary>
    {content_pre}
    </Previous Content Summary>

    <Current Section>
    {current_section}
    </Current Section>
    
    <Instructions>
    - Read the Previous Content Summary. 
    - Find the <content> tag in Current Section. 
    - Write output texts that will fit in the <content> tag position and that will maintain continuity and relevance with the text above and below it.

    - Provide the output in the following format.
    {format_instructions}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateContentSchema), llm=llm)
        self.generate_content_prompt = setPrompt(self.generate_content_system_prompt(instructions), 
                                                self.generate_content_human_prompt, 
                                                parser)
        self.generate_content_chain = self.generate_content_prompt | llm | parser


    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        
        response = retryInvoke(self.generate_content_chain, input={'content_pre': state['content_pre'],
                                                            'current_section': state['current_section']})
        try:
            response = dict(response)['content']
        except:
            raise Exception(f'GenerateContent response does not have content, response: {response}')

        return {'response': response, 'steps': ['Generate Content']}