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

def testContentWriterBaseArchitecture():

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
                             'retrieved_doc_ids': [],
                             'rag_context': '',
                             'graphrag_context': {},
                             'literature_list': [],
                             'references': [],
                             'is_abstract': False,
                             'concept_map': {}})

    for item in ['content', 'content_summary', 'concept_map', 'keyphrases', 'retrieved_doc_ids']:
        assert item in response, f'Response does not contain {item}'

    assert isinstance(response['concept_map'], dict) and len(response['concept_map']) > 0, f'Invalid concept map {response['concept_map']=}'
    assert isinstance(response['keyphrases'], list), f'Invalid keyphrases {response['keyphrases']=}'
    assert isinstance(response['retrieved_doc_ids'], list), f'Invalid retrieved document ids {response['retrieved_doc_ids']=}'

def testContentWriterRAGArchitecture():

    from src.vectordb import ChromaDB, getLoader
    from src.utils import Config
    from pathlib import Path

    file_path = Config.DIR_HOME / 'tests' / 'data' / 'test_content_writer.pdf'
    try:
        docs = list(getLoader(file_path))
    except:
        raise Exception("Could not load test_content_writer.pdf to create vector db.")

    collection_name = 'dummy_collection'

    for i in range(len(docs)):
        docs[i].metadata = {**{'app_file_id': Path(file_path).stem, 'app_file_type': 'uploaded_document'}, **{k: str(v) for k, v in docs[i].metadata.items()}}

    db = ChromaDB()
    db.create(collection_name=collection_name, delete_if_exists=True)
    db.add(docs=docs)

    current_section = f'''
    # Title: Quantum Computing and its Applications
    ## Introduction
    {OutlineTAGs.CONTENT.value}
    '''

    agent = ContentWriterArchitecture(collection_name=collection_name, type='rag')
    response = agent.invoke({'content_pre_summary': '',
                             'current_section': current_section,
                             'content_specific_instructions': '',
                             'keyphrases': [],
                             'retrieved_doc_ids': [],
                             'rag_context': '',
                             'graphrag_context': {},
                             'literature_list': [],
                             'references': [],
                             'is_abstract': False,
                             'concept_map': {}})

    for item in ['content', 'content_summary', 'concept_map', 'keyphrases', 'retrieved_doc_ids']:
        assert item in response, f'Response does not contain {item}'

    assert isinstance(response['concept_map'], dict) and len(response['concept_map']) > 0, f'Invalid concept map {response['concept_map']=}'
    assert isinstance(response['keyphrases'], list) and len(response['keyphrases']) > 0, f'Invalid keyphrases {response['keyphrases']=}'
    assert isinstance(response['retrieved_doc_ids'], list) and len(response['retrieved_doc_ids']) > 0, f'Invalid retrieved document ids {response['retrieved_doc_ids']=}'

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
