from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from langgraph.graph import START, StateGraph
from typing import Literal
from typing_extensions import TypedDict

import tqdm
import pandas as pd

from .utils import Config
from ..ai.prompts import setPrompt
from ..ai.llms import getAIModel
from ..ai.summarize import Summarize

# ---------------------------------------------------------------------------
class ScoreWithReasonSchema(BaseModel):
    '''
    Returns a score within 0 to 100 for a particular criterion and a statement supporting the score
    '''
    score: int = Field(description='Score within 0 to 100')
    reason: str = Field(description='A short statement supporting the score')

# ---------------------------------------------------------------------------
class RateSectionContentSchema(BaseModel):
    '''
    Returns scores based on different criteria to rate the content of a structured document
    '''

    relevance: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates the Relevance of the content')
    continuity: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates the Continuity of the content')
    non_repetitiveness: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates the Uniqueness (or non-repetitiveness) of the content')
    specificity: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates the Specificity of the content')
    #relevance of citation (hallucination), accuracy of the content+citation (hallucination), specificity of the content

# ---------------------------------------------------------------------------
class StateRateContent(TypedDict):

    reference_text: str
    content: str
    rating_info: str

# ---------------------------------------------------------------------------
class RateContent:

    rate_content_system_prompt = f'''\
    You are a scholarly reviewer with expertise in the topic domain provided by the user. Your task is review and rate the provided content.
    
    <Instructions>
    - Rating must be an integer number within 0 (lowest) and 100 (highest).
    - Rating will base on the provided schema.
    </Instructions>
    '''

    rate_content_human_prompt = '''
    <ReferenceText>
    {reference_text}
    </ReferenceText>

    <Content>
    {content}
    </Content>
    
    <Instructions>
    - Read the "Content" and rate it. If any "ReferenceText" text is provided, rate the "Content" with respect to the "ReferenceText" text.
    - Provide the output in the following format.
    {format_instructions}
    
    - Output must be in JSON format with `json` tags.
    </Instructions>
    '''

    def __init__(self, llm, rating_schema):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=rating_schema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.rate_content_prompt = setPrompt(self.rate_content_system_prompt, self.rate_content_human_prompt, parser)
        
        self.rate_content_chain = self.rate_content_prompt | llm | parser


    def __call__(self, state: StateRateContent):
        '''LLM evaluates content on a given rating schema'''
        
        response = self.rate_content_chain.invoke(input={'reference_text': state['reference_text'], 'content': state['content']})
        try:
            content = dict(response)
        except:
            raise Exception(f'RateContent response does not have content, response: {response}')

        return {'rating_info': content, 'steps': ['Rate Content']}

# -----------------------------------------------------------------------
class RateContentArchitecture:

    def check_if_summary_needed(
            self,
            state: StateRateContent
    ) -> Literal['Summarize', 'Rate Content']:
        if len(state.get('reference_text').split()) > 500:
            return 'Summarize'
        return 'Rate Content'
     
    def __init__(self, model_name, temperature):
        llm = getAIModel(model_name=model_name, temperature=temperature)

        # Define a new graph
        workflow = StateGraph(state_schema=StateRateContent)

        # Define the (single) node in the graph
        workflow.add_node("Summarize", Summarize(llm=llm, input_field='reference_text'))
        workflow.add_node("Rate Content", RateContent(llm=llm, rating_schema=RateSectionContentSchema))

        workflow.add_conditional_edges(START, self.check_if_summary_needed)
        workflow.add_edge("Summarize", "Rate Content")

        self.agent = workflow.compile()

# -----------------------------------------------------------------------
def evalContent(eval_model_name: str, section_contents: dict) -> dict:

    """
    Evaluate section wise content with AI based on relevance, continuity, uniqueness, specificity of the content
    Arguments:
        eval_model_name: Base model name used by the AI evaluator
        section_contents: Section wise content. A mapping between section header and section content
    Returns: A dictionary of rating responses for each section
    """

    def formatRating(rating):
        rating_dict = {}
        for criterion in rating:
            rating_dict[f'{criterion} (score)'] = rating[criterion].score
            rating_dict[f'{criterion} (reason)'] = rating[criterion].reason

        return rating_dict

    agent = RateContentArchitecture(model_name=eval_model_name, temperature=0).agent
    
    content_pre_sets = ['' for _ in section_contents]
    rating_responses_section_wise = {}

    for i, (section_header, content) in tqdm.tqdm(enumerate(section_contents.items())):
        
        print(section_header)

        if content.strip() == '': continue

        reference_text = f'''<Previous Content Summary>
            {content_pre_sets[i]}
            </Previous Content Summary>
        
            <Current Section Header>
            {section_header}
            </Current Section Header>'''
        
        rating_response = agent.invoke({'reference_text': reference_text, 'content': content})['rating_info']
        rating_responses_section_wise[section_header] = formatRating(rating_response)
        content_pre_sets[i] += f'{section_header}\n\n{content}'

    return rating_responses_section_wise

# -----------------------------------------------------------------------
def evalAndCompareTools(section_sets: pd.DataFrame, gen_content_file_name: str, eval_model_name: str) -> None:

    """
    Evaluate and compare generated file contents by multiple tools with AI
    Arguments:
        eval_model_name: Base model name used by the AI evaluator
        gen_content_file_name: Generated content file name
    Returns: None
    """

    from pathlib import Path

    rating_responses_tool_wise = pd.DataFrame()
    
    for tool in list(section_sets.columns):

        print(f'Processing "{gen_content_file_name} with {eval_model_name} AI agent for {tool}"...')

        section_contents = section_sets[tool].to_dict()
        rating_responses_section_wise = evalContent(eval_model_name, section_contents)
        rating_responses_tool_wise = pd.concat([rating_responses_tool_wise,
                                                pd.DataFrame(rating_responses_section_wise).add_prefix(f'{tool} ', axis=0)])

    rating_score = rating_responses_tool_wise.loc[rating_responses_tool_wise.index.str.endswith('(score)')]
    rating_reason = rating_responses_tool_wise.loc[rating_responses_tool_wise.index.str.endswith('(reason)')]

    rating_score = rating_score.rename(index=lambda x:x.replace(' (score)', ''))
    rating_reason = rating_reason.rename(index=lambda x:x.replace(' (reason)', ''))

    (Config.dir_eval_with_tools / 'results' / 'scores' / eval_model_name).mkdir(parents=False, exist_ok=True)
    (Config.dir_eval_with_tools / 'results' / 'reasons' / eval_model_name).mkdir(parents=False, exist_ok=True)

    rating_score.to_csv(Config.dir_eval_with_tools / 'results' / 'scores' / eval_model_name / f'{Path(gen_content_file_name).stem}.csv', index=True)
    rating_reason.to_csv(Config.dir_eval_with_tools / 'results' / 'reasons' / eval_model_name / f'{Path(gen_content_file_name).stem}.csv', index=True)
