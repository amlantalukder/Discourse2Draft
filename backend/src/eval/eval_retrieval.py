from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from langgraph.graph import START, StateGraph
from typing import Literal
from typing_extensions import TypedDict

from .utils import Config
from ..ai.prompts import setPrompt
from ..ai.llms import getAIModel
from ..ai.summarize import Summarize

from app_utils import get_generated_file_section_chunks, \
                       _active_literature_collection_record, \
                       _vector_collection_name

rate_keyphrases_system_prompt = f'''\
You are a scholarly reviewer with expertise in the topic domain provided by the user. 
Your task is review and rate the provided list of keyphrases against provided reference text.

<Instructions>
- Rating must be an integer number within 0 (lowest) and 100 (highest).
- Rating will base on the provided schema.
</Instructions>
'''

rate_keyphrases_human_prompt = '''
<ReferenceText>
{reference_text}
</ReferenceText>

<Content>
{content}
</Content>

<Instructions>
- The "ReferenceText" text would contain a section header from a document and a summary on the previous content.
- The "Content" text would contain a list of keyphrases extracted from the section header.
- Rate the provided list of keyphrases against the provided reference text.
- Provide the output in the following format.
{format_instructions}

- Output must be in JSON format with `json` tags.
</Instructions>
'''

rate_retrieved_context_system_prompt = f'''\
You are a scholarly reviewer with expertise in the topic domain provided by the user. 
Your task is review and rate the retrieved context against provided reference text.

<Instructions>
- Rating must be an integer number within 0 (lowest) and 100 (highest).
- Rating will base on the provided schema.
</Instructions>
'''

rate_retrieved_context_human_prompt = '''
<ReferenceText>
{reference_text}
</ReferenceText>

<Content>
{content}
</Content>

<Instructions>
- The "ReferenceText" text would contain a section header from a document and a summary on the previous content.
- The "Content" text would contain a retrieved context chunk from vector database.
- Rate the provided "Content" against the provided "ReferenceText".
- Provide the output in the following format.
{format_instructions}

- Output must be in JSON format with `json` tags.
</Instructions>
'''

# ---------------------------------------------------------------------------
class ScoreWithReasonSchema(BaseModel):
    '''
    Returns a score within 0 to 100 for a particular criterion and a statement supporting the score
    '''
    score: int = Field(description='Score within 0 to 100')
    reason: str = Field(description='A short statement supporting the score')

# ---------------------------------------------------------------------------
class RateRetrievedContextSchema(BaseModel):
    '''
    Returns scores based on different criteria to rate the retrieved context based on a section of a structured document
    '''

    relevance: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates the Relevance of the content')
    specificity: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates the Specificity of the content')

# ---------------------------------------------------------------------------
class RateKeyphrasesSchema(BaseModel):
    '''
    Returns scores based on different criteria to rate the keyphrases based on a section of a structured document
    '''

    relevance: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates if the provided content is relevant to explain the provided reference')
    completeness: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates if the provided content is enough to explain the provided reference')
    specificity: ScoreWithReasonSchema = Field(description='A score with supporting statement that evaluates if the provided content can precisely explain the provided reference')

# ---------------------------------------------------------------------------
class StateRateContent(TypedDict):

    reference_text: str
    content: str
    rating_info: str

# ---------------------------------------------------------------------------
class RateContent:

    def __init__(self, system_prompt, user_prompt, llm, rating_schema):

        parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=rating_schema), 
                                             llm=llm,
                                             max_retries=Config.RETRY_COUNTER)
        
        self.rate_content_prompt = setPrompt(system_prompt, user_prompt, parser)
        
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
class RateKeyPhrasesArchitecture:
     
    def __init__(self, model_name, temperature):
        llm = getAIModel(model_name=model_name, temperature=temperature)

        # Define a new graph
        workflow = StateGraph(state_schema=StateRateContent)

        # Define the (single) node in the graph
        workflow.add_node("Rate Key Phrases", RateContent(system_prompt=rate_keyphrases_system_prompt, 
                                                          user_prompt=rate_keyphrases_human_prompt, 
                                                          llm=llm, 
                                                          rating_schema=RateKeyphrasesSchema))

        self.agent = workflow.compile()

# -----------------------------------------------------------------------
class RateRetrievedContextArchitecture:

    # -----------------------------------------------------------------------
    def check_if_summary_needed(
            self,
            state: StateRateContent,
        ) -> Literal['Summarize', 'Rate Content']:
            if len(state.get('content').split()) > 500:
                return 'Summarize'
            return 'Rate Content'
     
    def __init__(self, model_name, temperature):
        llm = getAIModel(model_name=model_name, temperature=temperature)

        # Define a new graph
        workflow = StateGraph(state_schema=StateRateContent)

        # Define the (single) node in the graph
        workflow.add_node("Summarize", Summarize(llm=llm, input_field='content'))
        workflow.add_node("Rate Content", RateContent(system_prompt=rate_retrieved_context_system_prompt, 
                                                      user_prompt=rate_retrieved_context_human_prompt, 
                                                      llm=llm, 
                                                      rating_schema=RateRetrievedContextSchema))

        workflow.add_conditional_edges(START, self.check_if_summary_needed)
        workflow.add_edge("Summarize", "Rate Content")

        self.agent = workflow.compile()

# -----------------------------------------------------------------------
def formatRating(rating):
    rating_dict = {}
    for criterion in rating:
        rating_dict[f'{criterion} (score)'] = rating[criterion].score
        rating_dict[f'{criterion} (reason)'] = rating[criterion].reason

    return rating_dict

# -----------------------------------------------------------------------
def evalKeyPhrases(eval_model_name: str, keyphrases: str, section_header: str, content_pre_summary: str) -> dict:
    """
    Evaluate section wise keyphrases with AI based on relevance, completeness, specificity of the content
    Arguments:
        eval_model_name: Base model name used by the AI evaluator
        keyphrases: Keyphrases extracted from the section header
        section_header: Section header from a structured document
        content_pre_summary: Summary of previous content
    Returns: A dictionary of rating responses for each section
    """

    agent = RateKeyPhrasesArchitecture(model_name=eval_model_name, temperature=0).agent

    print(f'Evaluating keyphrases for section "{section_header}"...')

    reference_text = f'''<Previous Content Summary>
        {content_pre_summary}
        </Previous Content Summary>
    
        <Current Section Header>
        {section_header}
        </Current Section Header>'''

    content = f'''<Keyphrases>
        {keyphrases}
        </Keyphrases>'''
    
    rating_response = agent.invoke({'reference_text': reference_text, 'content': content})['rating_info']

    return formatRating(rating_response)

# -----------------------------------------------------------------------
def evalRetrievedDocIds(eval_model_name: str, retrieved_doc_ids: list, section_header: str, content_pre_summary: str, vector_collection_name: str) -> list:

    def get_chroma_chunk_by_id(collection_name: str, doc_ids: list) -> str | None:

        from src.vectordb import ChromaDB

        """
        Fetch a single ChromaDB chunk by its Chroma document/chunk id.
        Returns a document chnunk if found, otherwise returns None.
        """
        db = ChromaDB()
        db.get(collection_name=collection_name)

        result = db.vector_store.get(
            ids=doc_ids,
            include=["documents", "metadatas"],
        )

        if not result.get("ids"):
            return None

        return result["documents"][0]

    """
    Evaluate section wise retrieved context chunks with AI based on relevance, completeness, specificity of the content
    Arguments:
        eval_model_name: Base model name used by the AI evaluator
        retrieved_doc_ids: List of retrieved document IDs
        section_header: Section header from a structured document
        content_pre_summary: Summary of previous content
    Returns: A list of rating responses for each retrieved document
    """

    rating_response_list = []

    agent = RateKeyPhrasesArchitecture(model_name=eval_model_name, temperature=0).agent
    
    print(f'Evaluating retrieved documents for section "{section_header}"...')

    reference_text = f'''<Previous Content Summary>
        {content_pre_summary}
        </Previous Content Summary>
    
        <Current Section Header>
        {section_header}
        </Current Section Header>'''

    chroma_chunks = get_chroma_chunk_by_id(collection_name=vector_collection_name, doc_ids=retrieved_doc_ids)

    for chunk in chroma_chunks:

        rating_response = agent.invoke({'reference_text': reference_text, 'content': chunk})['rating_info']
        rating_response_list.append(formatRating(rating_response))

    return rating_response_list

# -----------------------------------------------------------------------
def evalRAGFramework(eval_model_name: str, gen_file_id: str):

    # Extract outline
    sections = get_generated_file_section_chunks(generated_file_id=gen_file_id)
    vector_collection_record = _active_literature_collection_record(generated_file_id=gen_file_id)
    assert vector_collection_record, f'No active literature collection found for generated file {gen_file_id}'
    vector_collection_name = _vector_collection_name(int(vector_collection_record["id"]))

    for section in sections:
        print(f"Evaluating section {section["heading"]} with {eval_model_name} AI model ...")
    
        # Evaluate keyphrases
        evalKeyPhrases(eval_model_name, section["keyphrases"], section["heading"], section["content_pre_summary"])

        # Evaluate retrieved_doc_ids
        evalRetrievedDocIds(eval_model_name, section["retrieved_doc_ids"], section["heading"], section["content_pre_summary"], vector_collection_name)