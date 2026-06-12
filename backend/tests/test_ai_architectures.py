from src.ai.architecture import ContentWriterArchitecture, OutlineCreatorArchitecture, AbstractSectionDetectorArchitecture, AbstractWriterArchitecture, OutlineFormatterArchitecture
from src.common import OutlineTAGs

def testOutlineCreatorArchitecture():

    query = 'Write me something about quantum computing.'
    details = ''

    agent = OutlineCreatorArchitecture()
    response = agent.invoke({'query': query, 'details': details})
    assert response['content'], f'Invalid output {response}'

def testAbstractSectionDetectorArchitecture():

    current_section = ''

    agent = AbstractSectionDetectorArchitecture()

    for current_section in ['Abstract', 'Executive summary', 'Summary']:
        response = agent.invoke({'current_section': current_section})
        assert response['is_abstract'] == True, f'Invalid output {response['is_abstract']} for abstract like section: {current_section}'

    for current_section in ['Introduction', 'Conclusion', 'Methods']:
        response = agent.invoke({'current_section': current_section})
        assert response['is_abstract'] == False, f'Invalid output {response['is_abstract']} for non-abstract like section: {current_section}'

def testContentWriterArchitecture():

    current_section = f'''
    # Title: Quantum Computing and its Applications
    ## Introduction
    {OutlineTAGs.CONTENT.value}
    '''

    agent = ContentWriterArchitecture()
    response = agent.invoke({'content_pre_summary': '',
                             'current_section': current_section,
                             'content_specific_instructions': '',
                             'keyphrases': [],
                             'rag_context': '',
                             'graphrag_context': {},
                             'literature_list': [],
                             'references': [],
                             'is_abstract': False,
                             'concept_map': {}})

    assert response['content'], f'Invalid output {response}'
    assert response['content_summary'], f'Invalid content summary {response}'
    assert isinstance(response['concept_map'], dict), f'Invalid concept map {response}'

def testAbstractWriterArchitecture():

    content_pre_summary = 'Quantum computing uses quantum bits and quantum phenomena to solve selected computational problems.'
    current_section = f'''
    # Title: Quantum Computing and its Applications
    ## Abstract
    {OutlineTAGs.CONTENT.value}
    '''

    agent = AbstractWriterArchitecture()
    response = agent.invoke({'content_pre_summary': content_pre_summary,
                             'current_section': current_section,
                             'content_specific_instructions': '',
                             'keyphrases': [],
                             'rag_context': '',
                             'graphrag_context': {},
                             'literature_list': [],
                             'references': [],
                             'is_abstract': True,
                             'concept_map': {}})

    assert response['content'], f'Invalid output {response}'

def testOutlineFormatterArchitecture():

    outline_unstructured = '''
    Title: Quantum Computing and its Applications
    Introduction
    Quantum algorithms
    Applications in chemistry and optimization
    '''

    agent = OutlineFormatterArchitecture()
    response = agent.invoke({'outline_unstructured': outline_unstructured})

    assert response['content'], f'Invalid output {response}'
    assert OutlineTAGs.CONTENT.value in response['content'], f'Invalid output {response}'
