from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from typing import List
from pydantic import BaseModel, Field
from .common import State, ReferenceSchema
from .prompts import setPrompt
from ..utils import Config

# ---------------------------------------------------------------------------
class GenerateContentRAGSchema(BaseModel):
    '''
    The content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')
    references: List[ReferenceSchema] = Field(description='A list references of the citations in the content')

# ---------------------------------------------------------------------------
class GenerateContentRAG:

    generate_content_system_prompt = '''\
    You will be provided a manuscript section header with or without previously written content on a specific topic. You are a scholarly ghost writer with expertise in the corresponding topic area. Your task is write a detailed and polished content on the section.
    
    <Instructions>
    <Consistency>
    - Your writing must be consistent with previous section.
    - You must maintain the flow of writing.
    </Consistency>
    
    <Voice and register>
    - Doctoral‑level, formal scientific style (as in a peer‑reviewed journal).
    - Integrate definitions, mechanisms, empirical findings and theoretical nuance as appropriate.
    - Write at great enough depth that the reader will fully understand the various aspects of the sub section, but avoid being overly redundant with other sections.
    </Voice and register>
    
    <Form>
    - Only paragraphs — no headings, no numbering, no bullet points, no embedded outline codes.
    - You may use multiple paragraphs if needed to cover the content deeply and coherently.
    </Form>

    <Writing Depth and Style>
    - Avoid repeating detailed explanations already supplied for earlier sections unless essential for clarity; instead, use concise forward/backward references if necessary.
    - Where deemed necessary to illustrate a point/provide clarity, employ specific/detailed examples that help the reader better understand critical concepts.
    - When responding your sole values should be scientific accuracy, application of rigorous scientific reasoning, and material reasoning/rationality.
    - Identify hidden biases in your answer and correct them.
    </Writing Depth and Style
    </Instructions>
    '''

    generate_content_human_prompt = lambda self, instructions: f'''
    <Previous Content Summary>
    {{content_pre}}
    </Previous Content Summary>

    <Current Section>
    {{current_section}}
    </Current Section>

    <RAG Context>
    {{rag_context}}
    </RAG Context>
    
    <Instructions>
    {instructions}
    - Read the Previous Content Summary.
    - Find the <content> tag in Current Section. 
    - Write output texts that will fit in the <content> tag position and that will maintain continuity and relevance with the text above and below it.
    <Adding text from context>
    - The context is provided with RAG Context under file_id tags. Each file_id tag contains the reference and content.
    - In your writing, take context from the RAG Context whenever possible.
    - At the end of your writing from the context, cite the RAG context with the file_id within "[" and "]" in the following format: \[CITE(file_id)\].
    - If the context of a line is taken from the RAG context of multiple file_id's, you can cite all the file_ids in a comma separated string within "[" and "]" in the following format: \[CITE(file_id1, file_id2)\]. 
    - Do not put the citation after texts if the written texts are not from the RAG context.
    - If the written texts from RAG context is divided into multiple paragraphs, put citation at the end of each of the paragraphs.
    - You must put the citation before the ending "." of the corresponding line.
    </Adding text from context>

    - Provide the output in the following format.
    {{format_instructions}}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateContentRAGSchema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.generate_content_prompt = setPrompt(self.generate_content_system_prompt, 
                                                self.generate_content_human_prompt(instructions), 
                                                parser)
        
        self.generate_content_chain = self.generate_content_prompt | llm | parser

    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        
        response = self.generate_content_chain.invoke(input={'content_pre': state['content_pre'],
                                                             'current_section': state['current_section'],
                                                             'rag_context': state['rag_context']})
        try:
            response = dict(response)
            content = response['content']
            references = {}

            for ref in response['references']:
                references |= {ref.file_id: ref.file_name}

        except:
            raise Exception(f'GenerateContent response does not have content or references, response: {response}')

        return {'content': content, 'references': references, 'steps': ['Generate Content']}