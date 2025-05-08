from langchain_core.prompts import ChatPromptTemplate

def setPrompt(system_prompt, human_prompt):

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
    )