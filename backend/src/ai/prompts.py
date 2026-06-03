from langchain_core.prompts import ChatPromptTemplate

from ..utils import print_func_name

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