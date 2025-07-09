from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from .utils import StateOutline, retryInvoke, Config
from .prompts import setPrompt

# ---------------------------------------------------------------------------
class GenerateOutlineSchema(BaseModel):
    '''
    Returns the outline on the provided topic
    '''
    content: str = Field(description='Outline on the provided topic')

# ---------------------------------------------------------------------------
class GenerateOutline:

    generate_outline_system_prompt = '''
    You are an expert in generating outline for content on a given topic.

    <Instructions>
    - Read the given topic. 
    - Generate an outline with section, subsection headers.
    - Each outline must start with a "Title".
    - Do not provide "References" section or any other extra sections or sub-sections that may not have content on the topic. 
    - Place "<content>" tag wherever the content should be written.
    </Instructions>

    <Output format>
    - The outline must have "<content>" tag in place of actual content.
    - Generate output in markdown format. Strictly follow the following example.
    </Output format>

    <Example>
    Topic: Hypertensive Disorders of Pregnancy
    
    Output:
    
    # Title: Hypertensive Disorders of Pregnancy: A Comprehensive Review of Pathophysiology, Clinical Management, Long-Term Implications, and Future Directions
    ## I. Introduction
    <content>
    ### A. Historical Perspective and Evolution of Understanding
    <content>
    ### B. Definition and Significance of Hypertensive Disorders of Pregnancy (HDP)
    #### 1. Global Burden of Disease (Maternal and Perinatal Morbidity & Mortality)
    <content>
    </Example>
    '''

    generate_outline_human_prompt = lambda self, instructions: (f'''
    <Instructions>
    {instructions}
    </Instructions>
    '''
    +
    '''
    <Topic>
    {topic}
    </Topic>
    ''')


    def __init__(self, llm, instructions):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateOutlineSchema), llm=llm)
        self.generate_outline_prompt = setPrompt(self.generate_outline_system_prompt, 
                                                 self.generate_outline_human_prompt(instructions),
                                                 parser)
        self.generate_outline_chain = self.generate_outline_prompt | llm | parser


    def __call__(self, state: StateOutline):
        '''LLM generates reports from a given outline'''
        
        for _ in range(Config.RETRY_COUNTER):
            
            response = retryInvoke(self.generate_outline_chain, input={'topic': state['topic']})
            try:
                response = dict(response)['content']
            except:
                raise Exception(f'GenerateOutline response does not have content, response: {response}')
            
            if '<content>' in response:
                break

            print('Response does not have <content> tag. Retrying...')


        return {'response': response, 'steps': ['Generate Outline']}