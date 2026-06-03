from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

import requests
import logging
import json

from ..utils import Config, traceError, formatErrorString, SetupException, print_func_name, Versions

# ---------------------------------------------------------------------------
@print_func_name
def extractAvailableLLMs() -> dict | list:
    """
    Extracts a list of available LLM names from LiteLLM proxy

    :return: list of available LLM names, list of available embedding model names
    """

    if Config.current_version == Versions.PRODUCTION.value:
        return [Config.env_config['DEFAULT_AI_MODEL']]

    available_llms = []
    litellm_api_key = Config.env_config['AI_API_KEY']
    try:
        response = requests.get(url=f'{Config.env_config.get("AI_BASE_URL")}/model/info',
                                headers={'API-Key': litellm_api_key},
                                verify=Config.cert_path)
        if response.ok:
            response_d = response.json()
            if response_d and ('data' in response_d):
                for item in response.json()['data']: 
                    if 'mode' not in item['model_info']: continue
                    if 'litellm_provider' not in item['model_info'] or item['model_info']['litellm_provider'] == 'ollama': continue
                    if item['model_info']['mode'] == 'chat':
                        available_llms.append(item['model_name'])
                available_llms = sorted(available_llms)
        else:
            logging.info(response.text)

    except Exception as error:
        logging.error('Error during litellm model info access:', error)
    

    try:
        with open(Config.DIR_HOME / 'config' / 'llms.json', 'r') as f:
            llm_options = json.load(f)
        
        llms_filtered = {}
        has_default = False
        for category, d in llm_options.items():
            category_filtered = {k: v for k, v in d.items() if k in available_llms}
            if category_filtered: 
                llms_filtered[category] = category_filtered
                if Config.env_config['DEFAULT_AI_MODEL'] in category_filtered:
                    has_default = True

        if not has_default:
            llms_filtered['Default'] = {'Uncategorized': Config.env_config['DEFAULT_AI_MODEL']}
        return llms_filtered
    
    except FileNotFoundError:
        logging.warning("LLM options file not found.")
    
    except Exception as exp:
        logging.error(traceError(exp))    
    
    return [Config.env_config['DEFAULT_AI_MODEL']]

# ---------------------------------------------------------------------------
@print_func_name
def getAIModel(model_name: str, temperature: int = 0, is_embedding=False) -> ChatOpenAI | OpenAIEmbeddings:
    """
    Initializes either an OpenAI Chat LLM object based on the LLM name and temperature
    or an OpenAI embedding model

    :param model_name: Name of the LLM
    :param temperature: Temperature
    :param is_embedding: For embedding model
    :return: OpenAI Chat LLM
    """
    try:
        if not is_embedding:
        
            return ChatOpenAI(
                model=model_name,
                base_url=Config.env_config.get('AI_BASE_URL'),
                api_key=Config.env_config.get('AI_API_KEY'),
                temperature=temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                seed=1000,
                http_client=Config.httpx_client
            )
        
        return OpenAIEmbeddings(
            model=model_name, 
            base_url=Config.env_config['AI_BASE_URL'], 
            api_key=Config.env_config['AI_API_KEY'],
            request_timeout=None,
            max_retries=2,
            http_client=Config.httpx_client,
        )
    except Exception as exp:
        logging.error(traceError(exp))
        raise SetupException(formatErrorString('during AI model set up'))