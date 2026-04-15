
import dotenv
from pathlib import Path
import os
import logging

print = logging.info

# ---------------------------------------------------------------------------
class Config:

    llms_selected = {
        'OpenAI': {
            'azure-gpt-5': 'GPT-5', 
            'azure-o3': 'o3',
            'azure-o1-mini': 'o1-mini'
        }, 
        # 'Anthropic': {
        #     'claude-3-7-sonnet': 'Claude 3.7 sonnet', 
        #     'claude-3-5-sonnet': 'Claude 3.5 sonnet'
        # }, 
        'Google': {
            'gemini-3-pro': 'Gemini 3 Pro', 
            'gemini-3-flash': 'Gemini 3 Flash',
        }, 
        'Meta': {
                 'llama4-scout-17b-instruct': 'Llama 4 scout 17B instruct',
                 'llama3-3-70b': 'Llama 3.3 70B'
        },
        'Mistral': {
            'mistral-large-3': 'Mistral Large 3'
        }
    }

    env_config = dotenv.dotenv_values(Path(".env"))

    # Number of attempts to call LLM on failure
    RETRY_COUNTER = 2

    # Content Generation settings
    NUM_TOKENS_SUMMARY = int(env_config.get("NUM_TOKENS_SUMMARY", 500))
    MAX_CONTEXT_TOKENS = int(env_config.get("MAX_CONTEXT_TOKENS", 2000))
    MAX_KEYPHRASES = int(env_config.get("MAX_KEYPHRASES", 10))
    MAX_KEYPHRASES_LIT_SEARCH = int(env_config.get("MAX_KEYPHRASES_LIT_SEARCH", 5))
    NUM_MAX_LITERATURE = int(env_config.get("NUM_MAX_LITERATURE", 2))
    MAX_CONTENT_SIZE_PER_LITERATURE = int(env_config.get("MAX_CONTENT_SIZE_PER_LITERATURE", 20000))
    SIMILARITY_METRIC = env_config.get("SIMILARITY_METRIC", 'similarity_score_threshold')
    NUM_DOCS_MAX = int(env_config.get("NUM_DOCS_MAX", 5))
    SIMILARITY_THRESHOLD = float(env_config.get("SIMILARITY_THRESHOLD", 0.3))

    @staticmethod
    def setEnvWithPrefix(prefix):
        for k, v in Config.env_config.items():
            if k.startswith(prefix):
                os.environ[k] = v