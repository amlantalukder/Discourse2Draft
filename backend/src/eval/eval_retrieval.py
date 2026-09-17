import asyncio

from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers.fix import OutputFixingParser
from pydantic import BaseModel, Field
from langgraph.graph import START, StateGraph
from typing import Literal
from typing_extensions import TypedDict
import pandas as pd
from pathlib import Path
import tqdm
 
from .utils import Config
from ..utils import traceError
from ..ai.architecture import Architecture
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
class RateKeyPhrasesArchitecture(Architecture):
     
    def __init__(self, model_name, temperature):
        llm = getAIModel(model_name=model_name, temperature=temperature)

        # Define a new graph
        workflow = StateGraph(state_schema=StateRateContent)

        # Define the (single) node in the graph
        workflow.add_node("Rate Key Phrases", RateContent(system_prompt=rate_keyphrases_system_prompt, 
                                                          user_prompt=rate_keyphrases_human_prompt, 
                                                          llm=llm, 
                                                          rating_schema=RateKeyphrasesSchema))
        workflow.add_edge(START, "Rate Key Phrases")

        self.agent = workflow.compile()

# -----------------------------------------------------------------------
class RateRetrievedContextArchitecture(Architecture):

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

    def formatRating(rating):
        rating_dict = {}
        for criterion in rating:
            rating_dict[f'{criterion} (score)'] = rating[criterion].score
            rating_dict[f'{criterion} (reason)'] = rating[criterion].reason

        return rating_dict

    agent = RateKeyPhrasesArchitecture(model_name=eval_model_name, temperature=0)

    reference_text = f'''<Previous Content Summary>
        {content_pre_summary}
        </Previous Content Summary>
    
        <Current Section Header>
        {section_header}
        </Current Section Header>'''

    content = f'''<Keyphrases>
        ```json
        {keyphrases}
        ```
        </Keyphrases>'''

    rating_response = agent.invoke({'reference_text': reference_text, 'content': content})['rating_info']

    return formatRating(rating_response)

# -----------------------------------------------------------------------
def getEmptyRating(rating_criteria):

    rating_dict = {}
    for criterion in rating_criteria:
        rating_dict[f'{criterion} (score)'] =  None
        rating_dict[f'{criterion} (reason)'] = None

    return rating_dict

# -----------------------------------------------------------------------
def getEmptyMeanRating(rating_criteria):

    rating_dict = {}
    for criterion in rating_criteria:
        rating_dict[f'{criterion} (mean score)'] =  None
        rating_dict[f'{criterion} (reasons)'] = None

    return rating_dict

# -----------------------------------------------------------------------
def formatMeanRating(rating_list, rating_criteria):
    mean_rating_dict = {}
    for criterion in rating_criteria:
        mean_score = sum([rating[criterion].score for rating in rating_list]) / len(rating_list)
        mean_reason = ' | '.join([rating[criterion].reason for rating in rating_list])
        mean_rating_dict[f'{criterion} (mean score)'] = mean_score
        mean_rating_dict[f'{criterion} (reasons)'] = mean_reason

    return mean_rating_dict

# -----------------------------------------------------------------------
def getDocChunksByIds(collection_name: str, doc_ids: list) -> str | None:

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

    return result["documents"], result['metadatas']

# -----------------------------------------------------------------------
def evalRetrievedContext(eval_model_name: str, retrieved_doc_ids: list, section_header: str, content_pre_summary: str, vector_collection_name: str) -> list:

    """
    Evaluate section wise retrieved context chunks with AI based on relevance, specificity of the content
    Arguments:
        eval_model_name: Base model name used by the AI evaluator
        retrieved_doc_ids: List of retrieved document IDs
        section_header: Section header from a structured document
        content_pre_summary: Summary of previous content
        vector_collection_name: Vector db collection name for the document
    Returns: A list of rating responses for each retrieved document
    """

    async def rateChunk(idx, chunk):
        rating_response = await agent.ainvoke({
            'reference_text': reference_text,
            'content': chunk,
        })
        return idx, rating_response['rating_info']

    async def rateAllChunks(doc_chunks):
        tasks = [
            asyncio.create_task(rateChunk(idx, chunk))
            for idx, chunk in enumerate(doc_chunks)
        ]

        rating_response_list = [None] * len(tasks)

        for task in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            idx, rating_response = await task
            rating_response_list[idx] = rating_response

        return rating_response_list

    agent = RateRetrievedContextArchitecture(model_name=eval_model_name, temperature=0)
    cr_rating_criteria = list(RateRetrievedContextSchema.model_fields.keys())

    reference_text = f'''<Previous Content Summary>
        {content_pre_summary}
        </Previous Content Summary>
    
        <Current Section Header>
        {section_header}
        </Current Section Header>'''

    doc_chunks, _ = getDocChunksByIds(collection_name=vector_collection_name, doc_ids=retrieved_doc_ids)

    rating_response_list = asyncio.run(rateAllChunks(doc_chunks))

    return formatMeanRating(rating_response_list, rating_criteria=cr_rating_criteria)

# -----------------------------------------------------------------------
def evalCitations(eval_model_name: str, retrieved_doc_ids: list, content: str, vector_collection_name: str):

    """
    Evaluate content with cited reference with AI based on relevance, specificity of the content
    Arguments:
        eval_model_name: Base model name used by the AI evaluator
        retrieved_doc_ids: List of retrieved document IDs
        content: Generated content with citations
        vector_collection_name: Vector db collection name for the document
    Returns: A list of rating responses for each retrieved document
    """

    def getRefContentMapping(content_with_citation: str):
    
        import re

        splits = re.split(r'CITE\(([\w\W]+?)\)', content_with_citation)
        if len(splits) % 2:
            splits = splits[:-1]

        ref_content_mapping = {}

        for i in range(0, len(splits), 2):
            refs, content = splits[i+1], splits[i]
            for ref in refs.split(','):
                ref = ref.strip()
                ref_content_mapping[ref] = (ref_content_mapping.get(ref, '') + ' ' + content).strip()

        return ref_content_mapping

    def getRefContextMapping(retrieved_doc_ids: list, vector_collection_name: str):

        doc_chunks, doc_metadata = getDocChunksByIds(collection_name=vector_collection_name, doc_ids=retrieved_doc_ids)

        ref_context_mapping = {}

        for chunk, metadata in list(zip(doc_chunks, doc_metadata)):
            ref = metadata['app_file_id']
            ref_context_mapping[ref] = (ref_context_mapping.get(ref, '') + '\n\n' + chunk).strip()

        return ref_context_mapping

    async def rateCitation(idx, ref, content):
        
        if ref not in ref_context_mapping: 
            rating_response = {}
            breakpoint()
            rating_schema = ScoreWithReasonSchema(score=0, reason='Reference not found in the retrieved vector documents for this content')
            rating_response = {criterion:rating_schema for criterion in cr_rating_criteria}
        else:
            rating_response = await agent.ainvoke({
                'reference_text': content,
                'content': ref_context_mapping[ref],
            })
            rating_response = rating_response['rating_info']
        return idx, rating_response

    async def rateAllCitations(ref_content_mapping):
        tasks = [
            asyncio.create_task(rateCitation(idx, ref, content))
            for idx, (ref, content) in enumerate(ref_content_mapping.items())
        ]

        rating_response_list = [None] * len(tasks)

        for task in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            idx, rating_response = await task
            rating_response_list[idx] = rating_response

        return rating_response_list

    agent = RateRetrievedContextArchitecture(model_name=eval_model_name, temperature=0)
    cr_rating_criteria = list(RateRetrievedContextSchema.model_fields.keys())

    ref_content_mapping = getRefContentMapping(content)
    ref_context_mapping = getRefContextMapping(retrieved_doc_ids, vector_collection_name)

    if len(ref_content_mapping) == 0: return getEmptyRating(cr_rating_criteria)

    rating_response_list = asyncio.run(rateAllCitations(ref_content_mapping))
    return formatMeanRating(rating_response_list, rating_criteria=cr_rating_criteria)

# -----------------------------------------------------------------------
def evalKeyphrasesOnGenFile(eval_model_name: str, gen_file_id: int, rating_keyphrases: dict = {}) -> dict:

    def checkDataExists(rating_keyphrases, section, kp_rating_criteria):
        if section['heading'] not in rating_keyphrases: return False
        for criterion in kp_rating_criteria:
            for result_type in ['score', 'reason']:
                index_name = f'{criterion} ({result_type})'
                if index_name not in rating_keyphrases[section["heading"]] or pd.isna(rating_keyphrases[section["heading"]][index_name]):
                    return False
        return True 

    # Extract outline
    sections = get_generated_file_section_chunks(generated_files_id=gen_file_id)
    kp_rating_criteria = list(RateKeyphrasesSchema.model_fields.keys())

    for section in sections:

        if checkDataExists(rating_keyphrases, section, kp_rating_criteria):
            print(f"Skipping keyphrases evaluation for section {section['heading']} as it has already been evaluated.")
            continue
        
        print(f"Evaluating used keyphrases for context retrieval on section {section['heading']} with {eval_model_name} AI model ...")
    
        # Evaluate keyphrases
        if section["keyphrases"]:
            try:
                rating_keyphrases[section["heading"]] = evalKeyPhrases(eval_model_name, section["keyphrases"], section["heading"], section["content_pre_summary"])
            except Exception as exp:
                print(str(exp))
                rating_keyphrases[section["heading"]] = getEmptyRating(kp_rating_criteria)
        else:
            print(f"No keyphrases found for section {section['heading']}, skipping keyphrase evaluation.")
            rating_keyphrases[section["heading"]] = getEmptyRating(kp_rating_criteria)

    return rating_keyphrases

# -----------------------------------------------------------------------
def evalRetrievedContextOnGenFile(eval_model_name: str, gen_file_id: int, rating_retrieved_context: dict = {}, is_eval_citations = False) -> dict:

    def checkDataExists(rating_retrieved_context, section, cr_rating_criteria):
        if section['heading'] not in rating_retrieved_context: return False
        for criterion in cr_rating_criteria:
            for result_type in ['mean score', 'reasons']:
                index_name = f'{criterion} ({result_type})'
                if index_name not in rating_retrieved_context[section["heading"]] or pd.isna(rating_retrieved_context[section["heading"]][index_name]):
                    return False
        return True

    # Extract outline
    sections = get_generated_file_section_chunks(generated_files_id=gen_file_id)
    vector_collection_record = _active_literature_collection_record(generated_file_id=gen_file_id)
    assert vector_collection_record, f'No active literature collection found for generated file {gen_file_id}'
    vector_collection_name = _vector_collection_name(vector_db_collections_id=int(vector_collection_record["id"]))

    cr_rating_criteria = list(RateRetrievedContextSchema.model_fields.keys())

    for section in sections:

        if checkDataExists(rating_retrieved_context, section, cr_rating_criteria):
            if not is_eval_citations:
                print(f"Skipping retrieved context evaluation for section {section['heading']} as it has already been evaluated.")
            else:
                print(f"Skipping citation evaluation for section {section['heading']} as it has already been evaluated.")
            #if not (is_eval_citations and section['heading'].startswith('Clinical Landscape: Hemo')):
            continue

        if not is_eval_citations:
            print(f"Evaluating retrieved context for section {section['heading']} with {eval_model_name} AI model ...")
        else:
            print(f"Evaluating citations for section {section['heading']} with {eval_model_name} AI model ...")

        # Evaluate retrieved_doc_ids
        if section["retrieved_doc_ids"]:
            try:
                if not is_eval_citations:
                    rating_retrieved_context[section["heading"]] = evalRetrievedContext(eval_model_name, section["retrieved_doc_ids"], section["heading"], section["content_pre_summary"], vector_collection_name)
                else:
                    rating_retrieved_context[section["heading"]] = evalCitations(eval_model_name, section["retrieved_doc_ids"], section['content'], vector_collection_name)
            except Exception as exp:
                print(traceError(exp, verbose=False))
                rating_retrieved_context[section["heading"]] = getEmptyMeanRating(cr_rating_criteria)
        else:
            print(f"No retrieved documents found for section {section["heading"]}, skipping context evaluation.")
            rating_retrieved_context[section["heading"]] = getEmptyMeanRating(cr_rating_criteria)

    return rating_retrieved_context

# -----------------------------------------------------------------------
def evalRAGFramework(gen_content_file_name: str, gen_list: list, eval_model_name: str, resume: bool = True) -> None:

    kp_gen_scores_file = Config.dir_eval_with_tools / 'results' / 'keyphrases_generation' / 'scores' / eval_model_name / f'{Path(gen_content_file_name).stem}.csv'
    kp_gen_reasons_file = Config.dir_eval_with_tools / 'results' / 'keyphrases_generation' / 'reasons' / eval_model_name / f'{Path(gen_content_file_name).stem}.csv'
    cr_scores_file = Config.dir_eval_with_tools / 'results' / 'context_retrieval' / 'scores' / eval_model_name / f'{Path(gen_content_file_name).stem}.csv'
    cr_reasons_file = Config.dir_eval_with_tools / 'results' / 'context_retrieval' / 'reasons' / eval_model_name / f'{Path(gen_content_file_name).stem}.csv'
    ci_scores_file = Config.dir_eval_with_tools / 'results' / 'citations' / 'scores' / eval_model_name / f'{Path(gen_content_file_name).stem}.csv'
    ci_reasons_file = Config.dir_eval_with_tools / 'results' / 'citations' / 'reasons' / eval_model_name / f'{Path(gen_content_file_name).stem}.csv'

    (kp_gen_scores_file.parent).mkdir(parents=True, exist_ok=True)
    (kp_gen_reasons_file.parent).mkdir(parents=True, exist_ok=True)
    (cr_scores_file.parent).mkdir(parents=True, exist_ok=True)
    (cr_reasons_file.parent).mkdir(parents=True, exist_ok=True)
    (ci_scores_file.parent).mkdir(parents=True, exist_ok=True)
    (ci_reasons_file.parent).mkdir(parents=True, exist_ok=True)

    if resume and kp_gen_scores_file.exists():
        rating_kp_score = pd.read_csv(kp_gen_scores_file, index_col=0)
    else:
        rating_kp_score = pd.DataFrame()

    if resume and kp_gen_reasons_file.exists():
        rating_kp_reason = pd.read_csv(kp_gen_reasons_file, index_col=0)
    else:
        rating_kp_reason = pd.DataFrame()

    if resume and cr_scores_file.exists():
        rating_cr_score = pd.read_csv(cr_scores_file, index_col=0)
    else:
        rating_cr_score = pd.DataFrame()

    if resume and cr_reasons_file.exists():
        rating_cr_reason = pd.read_csv(cr_reasons_file, index_col=0)
    else:
        rating_cr_reason = pd.DataFrame()

    if resume and ci_scores_file.exists():
        rating_ci_score = pd.read_csv(ci_scores_file, index_col=0)
    else:
        rating_ci_score = pd.DataFrame()

    if resume and ci_reasons_file.exists():
        rating_ci_reason = pd.read_csv(ci_reasons_file, index_col=0)
    else:
        rating_ci_reason = pd.DataFrame()

    for tool_name, gen_file_id in gen_list:

        print('='*70, f'Evaluating RAG with tool {tool_name}...', '='*70, sep='\n')

        # -----------------------------------------------------------------------
        # Evaluation of keyphrases generation
        # -----------------------------------------------------------------------
        if not (rating_kp_score.empty or rating_kp_reason.empty):
            rating_kp_score_df = rating_kp_score[rating_kp_score.index.str.startswith(f'{tool_name} ')]
            rating_kp_reason_df = rating_kp_reason[rating_kp_reason.index.str.startswith(f'{tool_name} ')]

            rating_kp_score_df.index = rating_kp_score_df.index.str.removeprefix(f'{tool_name} ')
            rating_kp_reason_df.index = rating_kp_reason_df.index.str.removeprefix(f'{tool_name} ')

            rating_kp_score_df = rating_kp_score_df.add_suffix(' (score)', axis=0)
            rating_kp_reason_df = rating_kp_reason_df.add_suffix(' (reason)', axis=0)

            rating_kp_dict = pd.concat([rating_kp_score_df, rating_kp_reason_df]).to_dict()
        else:
            rating_kp_dict = {}

        rating_kp_tool_wise = evalKeyphrasesOnGenFile(eval_model_name, gen_file_id, rating_keyphrases=rating_kp_dict)
        rating_kp_tool_wise = pd.DataFrame(rating_kp_tool_wise).add_prefix(f'{tool_name} ', axis=0)

        rating_kp_score_tool_wise = rating_kp_tool_wise.loc[rating_kp_tool_wise.index.str.endswith('(score)')]
        rating_kp_reason_tool_wise = rating_kp_tool_wise.loc[rating_kp_tool_wise.index.str.endswith('(reason)')]
        
        rating_kp_score = rating_kp_score_tool_wise.rename(index=lambda x:x.replace(' (score)', '')).combine_first(rating_kp_score)
        rating_kp_reason = rating_kp_reason_tool_wise.rename(index=lambda x:x.replace(' (reason)', '')).combine_first(rating_kp_reason)
    
        rating_kp_score.to_csv(kp_gen_scores_file, index=True)
        rating_kp_reason.to_csv(kp_gen_reasons_file, index=True)

        # -----------------------------------------------------------------------
        # Evaluation of context retrieval
        # -----------------------------------------------------------------------
        if not (rating_cr_score.empty or rating_cr_reason.empty):
            rating_cr_score_df = rating_cr_score[rating_cr_score.index.str.startswith(f'{tool_name} ')]
            rating_cr_reason_df = rating_cr_reason[rating_cr_reason.index.str.startswith(f'{tool_name} ')]

            rating_cr_score_df.index = rating_cr_score_df.index.str.removeprefix(f'{tool_name} ')
            rating_cr_reason_df.index = rating_cr_reason_df.index.str.removeprefix(f'{tool_name} ')

            rating_cr_score_df = rating_cr_score_df.add_suffix(' (mean score)', axis=0)
            rating_cr_reason_df = rating_cr_reason_df.add_suffix(' (reasons)', axis=0)

            rating_cr_dict = pd.concat([rating_cr_score_df, rating_cr_reason_df]).to_dict()
        else:
            rating_cr_dict = {}

        rating_cr_tool_wise = evalRetrievedContextOnGenFile(eval_model_name, gen_file_id, rating_retrieved_context=rating_cr_dict)
        rating_cr_tool_wise = pd.DataFrame(rating_cr_tool_wise).add_prefix(f'{tool_name} ', axis=0)

        rating_cr_score_tool_wise = rating_cr_tool_wise.loc[rating_cr_tool_wise.index.str.endswith('(mean score)')]
        rating_cr_reason_tool_wise = rating_cr_tool_wise.loc[rating_cr_tool_wise.index.str.endswith('(reasons)')]
        
        rating_cr_score = rating_cr_score_tool_wise.rename(index=lambda x:x.replace(' (mean score)', '')).combine_first(rating_cr_score)
        rating_cr_reason = rating_cr_reason_tool_wise.rename(index=lambda x:x.replace(' (reasons)', '')).combine_first(rating_cr_reason)
    
        rating_cr_score.to_csv(cr_scores_file, index=True)
        rating_cr_reason.to_csv(cr_reasons_file, index=True)

        # -----------------------------------------------------------------------
        # Evaluation of citations
        # -----------------------------------------------------------------------
        if not (rating_ci_score.empty or rating_ci_reason.empty):
            rating_ci_score_df = rating_ci_score[rating_ci_score.index.str.startswith(f'{tool_name} ')]
            rating_ci_reason_df = rating_ci_reason[rating_ci_reason.index.str.startswith(f'{tool_name} ')]

            rating_ci_score_df.index = rating_ci_score_df.index.str.removeprefix(f'{tool_name} ')
            rating_ci_reason_df.index = rating_ci_reason_df.index.str.removeprefix(f'{tool_name} ')

            rating_ci_score_df = rating_ci_score_df.add_suffix(' (mean score)', axis=0)
            rating_ci_reason_df = rating_ci_reason_df.add_suffix(' (reasons)', axis=0)

            rating_ci_dict = pd.concat([rating_ci_score_df, rating_ci_reason_df]).to_dict()
        else:
            rating_ci_dict = {}

        rating_ci_tool_wise = evalRetrievedContextOnGenFile(eval_model_name, gen_file_id, rating_retrieved_context=rating_ci_dict, is_eval_citations=True)
        rating_ci_tool_wise = pd.DataFrame(rating_ci_tool_wise).add_prefix(f'{tool_name} ', axis=0)

        rating_ci_score_tool_wise = rating_ci_tool_wise.loc[rating_ci_tool_wise.index.str.endswith('(mean score)')]
        rating_ci_reason_tool_wise = rating_ci_tool_wise.loc[rating_ci_tool_wise.index.str.endswith('(reasons)')]
        
        rating_ci_score = rating_ci_score_tool_wise.rename(index=lambda x:x.replace(' (mean score)', '')).combine_first(rating_ci_score)
        rating_ci_reason = rating_ci_reason_tool_wise.rename(index=lambda x:x.replace(' (reasons)', '')).combine_first(rating_ci_reason)
    
        rating_ci_score.to_csv(ci_scores_file, index=True)
        rating_ci_reason.to_csv(ci_reasons_file, index=True)
    