from utils import print_func_name
from langchain_core.prompts import ChatPromptTemplate

@print_func_name
def setPrompt(system_prompt, human_prompt, parser):

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    system_prompt
                ),
            ),
            (
                "human",
                (
                    human_prompt
                ),
            ),
        ]
    ).partial(format_instructions=parser.get_format_instructions())