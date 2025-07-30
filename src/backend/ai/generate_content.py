from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from .common import State
from .prompts import setPrompt
from ..utils import Config

class GenerateContentSchema(BaseModel):
    '''
    Returns the content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')

# ---------------------------------------------------------------------------
class GenerateContent:

    generate_content_system_prompt = '''\
    <Instructions>
    The user will input an outline for a manuscript on a specific topic. You are a scholarly ghost‑writer with a PhD in that topic area. Your task is to convert a detailed, hierarchically coded outline into polished manuscript prose. Follow the following global constraints for every section you draft.

    **Your writing must be consistent with previous section**

    **Voice & register**
    
    - Doctoral‑level, formal scientific style (as in a peer‑reviewed journal).
    - Integrate definitions, mechanisms, empirical findings and theoretical nuance as appropriate.
    - Write at great enough depth that the reader will fully understand the various aspects of the sub section, but avoid being overly redundant with other sections.
    
    **Form**

    - Only paragraphs — no headings, no numbering, no bullet points, no embedded outline codes.
    - You may use multiple paragraphs if needed to cover the content deeply and coherently.
    
    **Use of outline**
    
    - Each outline line is structured as “<alphanumeric code> -> <level‑1 topic> -> <level‑2 topic> -> …”.
    - Treat higher‑level nodes as contextual background, lower‑level nodes as focal content.
    - Avoid repeating detailed explanations already supplied for earlier sections unless essential for clarity; instead, use concise forward/backward references if necessary.
    - Confidence scoring: For each factual statement generated, include a confidence score between 1-10 (1 being the lowest and 10 being the highest) in the form of “(CS= [score])”. This score should reflect the level of scientific consensus or evidence supporting the statement, with 1 indicating speculative or weakly supported claims and 10 indicating well-established facts.),

    **Writing Depth and Style**
    
    - Where deemed necessary to illustrate a point/provide clarity, employ specific/detailed examples that help the reader better understand critical concepts.
    - When responding your sole values should be scientific accuracy, application of rigorous scientific reasoning, and material reasoning/rationality.
    - Identify hidden biases in your answer and correct them.
    </Instructions>
    '''

    generate_content_human_prompt = lambda self, instructions: f'''
    <Previous Content Summary>
    {{content_pre}}
    </Previous Content Summary>

    <Current Section>
    {{current_section}}
    </Current Section>
    
    <Instructions>
    {instructions}
    - Read the Previous Content Summary. 
    - Find the <content> tag in Current Section. 
    - Write output texts that will fit in the <content> tag position and that will maintain continuity and relevance with the text above and below it.

    - Provide the output in the following format.
    {{format_instructions}}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateContentSchema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.generate_content_prompt = setPrompt(self.generate_content_system_prompt, 
                                                self.generate_content_human_prompt(instructions), 
                                                parser)
        
        self.generate_content_chain = self.generate_content_prompt | llm | parser


    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        
        response = self.generate_content_chain.invoke(input={'content_pre': state['content_pre'],
                                                             'current_section': state['current_section']})
        try:
            content = dict(response)['content']
        except:
            raise Exception(f'GenerateContent response does not have content, response: {response}')

        return {'content': content, 'steps': ['Generate Content']}