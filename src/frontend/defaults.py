from ..backend.ai.architecture import Architecture
import textwrap

class ConfigApp:

    def __init__(self):
        self.setDefaults()

    def setDefaults(self):
        self.settings_id = None
        self.generated_files_id = None
        self.vector_db_collections_id = None
        self.vector_db_collections_id_lit_search = None
        self.llm = 'azure-o1-mini'
        self.temperature = 0.
        self.instructions = ''
        self.agent = Architecture(model_name=self.llm, temperature=self.temperature, instructions=self.instructions).agent
        self.email = ''
        self.file_name = ''
        self.session_id = ''

        self.is_writing = False
        self.write_faster = False

