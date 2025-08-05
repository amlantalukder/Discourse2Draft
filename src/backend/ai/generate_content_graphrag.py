from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables.base import RunnableLambda
from langchain.output_parsers.fix import OutputFixingParser
from langchain_core.tools import tool
from langchain.chains import GraphQAChain
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from .llms import getAIModel
from .common import State
from .prompts import setPrompt
from ..utils import Config

@tool
def graphSearch(query: str) -> str:
    '''
    This tool provides the answer of a query using graph search
    '''
    llm = getAIModel('azure-gpt-4o')
    result = []
    for app_file_id, nx_graph in d_nx_graph.items():
        chain = GraphQAChain.from_llm(
            llm=llm, 
            graph=nx_graph
        )

        result.append(f'<{app_file_id}>{chain.invoke(query)['result']}</{app_file_id}>')

    return '\n\n'.join(result)

class GenerateContentGraphRAGSchema(BaseModel):
    '''
    Returns the content to fill the provided outline section
    '''
    content: str = Field(description='Content to fill the provided outline section')

# ---------------------------------------------------------------------------
class GenerateContentGraphRAG:

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
    
    <Instructions>
    {instructions}
    - Read the Previous Content Summary.
    - Find the <content> tag in Current Section. 
    - Write output texts that will fit in the <content> tag position and that will maintain continuity and relevance with the text above and below it.
    <Adding text from context>
    - You can get the RAG Context calling the tool with any query. If the tool response is not enough, you can call the tool multiple times.
    - The RAG context from the tool is provided within file_id tag. In your writing, take context from the RAG Context whenever possible. 
    - At the end of your writing from the context, cite the RAG context with the file_id by within "[" and "]" in the following format: \[CITE(file_id)\].
    - If the context of a line is taken from the RAG context of multiple file_id's, you can cite all the file_ids in a comma separated string within "[" and "]" in the following format: \[CITE(file_id1, file_id2)\].
    - Do not put the citation after texts if the written texts are not from the RAG context.
    - If the written texts from RAG context is divided into multiple paragraphs, put citation at the end of each of the paragraphs.
    </Adding text from context>

    - Provide the output in the following format.
    {{format_instructions}}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm, instructions):

        self.llm = llm

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=GenerateContentGraphRAGSchema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.generate_content_prompt = setPrompt(self.generate_content_system_prompt, 
                                                self.generate_content_human_prompt(instructions), 
                                                parser)
        
        llm_with_tools = create_react_agent(model=llm, tools=[graphSearch]) 

        self.generate_content_chain = self.generate_content_prompt | llm_with_tools | RunnableLambda(lambda x: x['messages'][-1]) | parser


    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''

        global d_nx_graph
        d_nx_graph = state['graphrag_context']
        
        response = self.generate_content_chain.invoke(input={'content_pre': state['content_pre'],
                                                             'current_section': state['current_section']})

        try:
            content = dict(response)['content']
        except:
            raise Exception(f'GenerateContent response does not have content, response: {response}')

        return {'content': content, 'steps': ['Generate Content']}