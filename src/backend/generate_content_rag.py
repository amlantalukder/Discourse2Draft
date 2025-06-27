from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from .utils import State, Config, retryInvoke
from .prompts import setPrompt

class GenerateContentRAGSchema(BaseModel):
    '''
    Returns the content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')

# ---------------------------------------------------------------------------
class GenerateContentRAG:

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

    <RAG Context>
    {rag_context}
    </RAG Context>
    
    <Instructions>
    - Read the Previous Content Summary.
    - Find the <content> tag in Current Section. 
    - Write output texts that will fit in the <content> tag position and that will maintain continuity and relevance with the text above and below it.
    <Adding text from context>
    - Read the RAG Context. 
    - The context is provided within file_id tag. In your writing, take context from the RAG Context whenever possible. 
    - At the end of your writing from the context, cite the RAG context with the file_id by beginning with "[" and ending with "]" in the following format: \[CITE(file_id)\].
    - Do not put the citation after texts if the written texts are not from the RAG context.
    - If the written texts from RAG context is divided into multiple paragraphs, put citation at the end of each of the paragraphs.
    </Adding text from context>

    - Provide the output in the following format.
    {format_instructions}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateContentRAGSchema), llm=llm)
        self.generate_content_prompt = setPrompt(self.generate_content_system_prompt(instructions), 
                                                self.generate_content_human_prompt, 
                                                parser)
        self.generate_content_chain = self.generate_content_prompt | llm | parser


    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        
        response = retryInvoke(self.generate_content_chain, input={'content_pre': state['content_pre'],
                                                            'current_section': state['current_section'],
                                                            'rag_context': state['rag_context']})
        try:
            response = dict(response)['content']
        except:
            raise Exception(f'GenerateContent response does not have content, response: {response}')

        return {'response': response, 'steps': ['Generate Report']}