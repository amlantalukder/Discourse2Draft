import re
from pydantic import BaseModel, Field
from langchain.output_parsers.fix import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser
import pandas as pd

from .utils import Config
from ..ai.llms import getAIModel
from ..ai.prompts import setPrompt

class StandardizeSectionHeadersSchema(BaseModel):
    '''
    Returns the mapping from the section header to standard section header
    '''
    mapping: dict[str, str] = Field(description='A mapping from the section header to standard section header')

def standardizeHeader(section_headers, section_headers_standard):
    '''
    Standardizes the section headers to a standard set of section headers.
    If a section header cannot be mapped to a standard section header, it is mapped to itself
    Args:
        section_headers: List of section headers to be standardized
        section_headers_standard: List of standard section headers to map to
    Returns:
        A dictionary mapping each section header to a standard section header
    '''

    for section in section_headers:
        if section not in section_headers_standard:
            break
    else:
        return {section: section for section in section_headers}

    llm = getAIModel(model_name='azure-gpt-4o')
    system_prompt = 'You are an AI assist designed to standardize section headers in a document'
    human_prompt = '''
                You will be provided with a list of section headers and a list of standard section headers in JSON format.
                Your task is to map each provided section header to a standard section header.
                If there is no mapping possible, map the section header to itself.

                <Section headers>
                ```json
                {section_headers}
                ```
                </Section headers>

                <Standard section headers>
                ```json
                {section_headers_standard}
                ```
                </Standard section headers>
                '''
    
    parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=StandardizeSectionHeadersSchema), 
                                llm=llm,
                                max_retries=Config.RETRY_COUNTER)
    
    prompt = setPrompt(system_prompt, human_prompt, parser)
        
    response = (prompt | llm | parser).invoke(input={'section_headers': section_headers, 'section_headers_standard': section_headers_standard})
    return dict(response)['mapping']

def extractSectionContent(file_path):
    
    with open(file_path) as fp:
        data = '\n'.join([line.strip() for line in fp.readlines()])
    
    output = re.findall(r'(#+ .+\n?)([^#]+)', data)
    return [(section.strip(), content.strip()) for section, content in output]

def getSectionAndContent(file_path, section_headers_standard):
    doc = extractSectionContent(file_path)
    doc_san = []
    for section, content in doc:
        if section.startswith('# '):
            doc_san.append(['# Title', section[2:]])
        elif section.startswith('## '):
            doc_san.append([section, content])
        else:
            doc_san[-1][1] += section + '\n' + content
    section_headers = [section for section, _ in doc_san if not section.startswith('# ')]
    mapping = standardizeHeader(section_headers, section_headers_standard)
    return [(mapping.get(section, section), content) for section, content in doc_san]
        
def extractSectionsForComparison(file_name):

    section_headers_standard = [item[0] for item in extractSectionContent(Config.dir_eval_with_tools / 'prompts' / file_name) if not item[0].startswith('# ')]
    responses = {}
    for tool in Config.tools:
        if tool != 'discourse2draft':
            responses[tool] = dict(getSectionAndContent(Config.dir_eval_with_tools / tool / file_name, section_headers_standard))
            continue
        for config in Config.gen_eval_model_config:
            for gen_model_name in config['generator']:
                for index_run in range(1, Config.num_runs+1):
                    responses[f'{tool}|{gen_model_name}|run_{index_run}'] = dict(getSectionAndContent(Config.dir_eval_with_tools / tool / gen_model_name / f'run_{index_run}' / file_name, section_headers_standard))

    pd.DataFrame(responses).to_csv(Config.dir_eval_with_tools / 'sections_to_compare' / f'{'.'.join(file_name.split('.')[:-1])}.csv')
