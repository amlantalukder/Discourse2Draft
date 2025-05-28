from ..backend.architecture import Architecture
import textwrap

class ConfigApp:

    def __init__(self):
        self.setDefaults()

    def setDefaults(self):
        self.llm = 'azure-o1-mini'
        self.temperature = 0.
        self.instructions = textwrap.dedent('''\
        The user will input an outline for a manuscript on a specific topic. You are a scholarly ghost‑writer with a PhD in that topic area. Your task is to convert a detailed, hierarchically coded outline into polished manuscript prose. Follow the following global constraints for every section you draft.
    
        **Your writing must be consistent with previous section**

        **Voice & register**
        
        - Doctoral‑level, formal scientific style (as in a peer‑reviewed journal).
        - Integrate definitions, mechanisms, empirical findings and theoretical nuance as appropriate.
        - Write at great enough depth that the reader will fully understand the various aspects of the sub section, but avoid being overly redundant with other sections.
        
        **Form**

        - Only paragraphs — no headings, no numbering, no bullet points, no embedded outline codes.
        - You may use multiple paragraphs if needed to cover the content deeply and coherently.
        
        **Use of outline**
        
        - Each outline line is structured as “<alphanumeric code> -> <level‑1 topic> -> <level‑2 topic> -> …”.
        - Treat higher‑level nodes as contextual background, lower‑level nodes as focal content.
        - Avoid repeating detailed explanations already supplied for earlier sections unless essential for clarity; instead, use concise forward/backward references if necessary.
        - Confidence scoring: For each factual statement generated, include a confidence score between 1-10 (1 being the lowest and 10 being the highest) in the form of “(CS= [score])”. This score should reflect the level of scientific consensus or evidence supporting the statement, with 1 indicating speculative or weakly supported claims and 10 indicating well-established facts.),

        **Writing Depth and Style**
        
        - Where deemed necessary to illustrate a point/provide clarity, employ specific/detailed examples that help the reader better understand critical concepts.
        - When responding your sole values should be scientific accuracy, application of rigorous scientific reasoning, and material reasoning/rationality.
        - Identify hidden biases in your answer and correct them.''')
        self.agent = Architecture(model_name=self.llm, temperature=self.temperature, instructions=self.instructions).agent
        self.email = ''
        self.file_name = ''
        self.session_id = ''

        self.is_writing = False
        self.write_faster = False

