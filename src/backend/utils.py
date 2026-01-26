
import dotenv
from pathlib import Path
import os
import logging

print = logging.info

# ---------------------------------------------------------------------------
class Config:

    llms_with_structured_output_support = {'azure-gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro'}
    llms_selected = {
        'OpenAI': {
            'azure-o1-mini': 'o1-mini', 
            'azure-o1': 'o1', 
            'azure-o3-mini': 'o3-mini', 
            'azure-o3': 'o3', 
            'azure-gpt-4o': 'GPT-4o',
            'azure-gpt-5': 'GPT-5'
        }, 
        'Anthropic': {
            'claude-3-7-sonnet': 'Claude 3.7 sonnet', 
            'claude-3-5-sonnet': 'Claude 3.5 sonnet'
        }, 
        'Google': {
            'gemini-1.5-flash': 'Gemini 1.5 Flash', 
            'gemini-1.5-pro': 'Gemini 1.5 Pro'
        }, 
        'Meta': {
                  'llama3-3-70b': 'Llama 3.3 70B',
                 'llama3-2-90b': 'Llama 3.2 90B', 
                 'llama3-1-405b': 'Llama 3.1 405B', 
                 'llama3-1-70b': 'Llama 3.1 70B'
        },
        'Mistral': {
            'mistral-large-2': 'Mistral Large 2'
        }
    }
    env_config = dotenv.dotenv_values(Path(".env"))

    # Generation
    NUM_TOKENS_SUMMARY = 500
    RETRY_COUNTER = 2

    # RAG
    MAX_CONTEXT_TOKENS = 2000
    MAX_KEYPHRASES = 10
    MAX_KEYPHRASES_LIT_SEARCH = 5
    NUM_MAX_LITERATURE = 2
    MAX_CONTENT_SIZE_PER_LITERATURE = 20000
    SIMILARITY_METRIC = 'similarity_score_threshold'
    NUM_DOCS_MAX = 5
    SIMILARITY_THRESHOLD = 0.3

    @staticmethod
    def setEnvWithPrefix(prefix):
        for k, v in Config.env_config.items():
            if k.startswith(prefix):
                os.environ[k] = v