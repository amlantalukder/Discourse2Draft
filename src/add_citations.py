from langchain_core.prompts import ChatPromptTemplate
from .utils import State

class AddCitations():

    add_citations_system_prompt = '''
    <Instructions>
    You are given a paragraph that represents discussion on a certain topic. You are an expert on that topic. You will tag the particular portion of the text that needs reference.

    1. You will find the line(s) that needs reference. A line needs reference if it contains information that was result of previous studies.
    2. You will wrap those line(s) with curly braces "CITE()". Example: CITE(This line needs reference).
    4. Do not add anything else to the input except the "CITE()".
    3. You will output the original input with the added curly braces.

    </Instructions>
    '''

    add_citations_human_prompt = '''
    <Input Paragraph>
    {input_paragraph}
    </Input Paragraph>
    
    Tag the text from the above input paragraph that need references.
    '''

    # -----------------------------------------------------------------------
    add_citations_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    add_citations_system_prompt
                ),
            ),
            (
                "human",
                (
                    add_citations_human_prompt
                ),
            ),
        ]
    )

    def __init__(self, llm):
        self.add_citations_chain = self.add_citations_prompt | llm

    def __call__(self, state: State):
        '''LLM generates reports from a given outline'''
        response = self.add_citations_chain.invoke(input={'input_paragraph': list(state['response'].values())[0]}).content
        return {'response': response, 'steps': ['Add Citations']}