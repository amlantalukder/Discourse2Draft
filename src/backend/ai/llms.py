from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

import requests
from pathlib import Path
from ..utils import Config
from utils import Config as config_base, print_func_name, Versions
import logging

import httpx
import truststore
import ssl
truststore.inject_into_ssl()
cert_path = str(Path(config_base.DIR_HOME / 'certs/NIH-FULL.pem'))
ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context = ssl.create_default_context()
client = httpx.Client(verify=cert_path)

# ---------------------------------------------------------------------------
@print_func_name
def extractAvailableLLMs() -> tuple[list, list]:
    """
    Extracts a list of available LLM names from LiteLLM proxy

    :return: list of available LLM names, list of available embedding model names
    """

    if config_base.current_version == Versions.PRODUCTION.value:
        return [Config.env_config['DEFAULT_AI_MODEL']]

    available_llms = []
    litellm_api_key = Config.env_config['AI_API_KEY']
    try:
        response = requests.get(url=f'{Config.env_config.get("AI_BASE_URL")}/model/info',
                                headers={'API-Key': litellm_api_key},
                                verify=cert_path)
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
        logging.error('litellm proxy access error:', error)
    
    llms_filtered = {}
    if Config.llms_selected:
        for category, d in Config.llms_selected.items():
            category_filtered = {k:v for k, v in d.items() if k in available_llms}
            if category_filtered:
                llms_filtered[category] = category_filtered
    available_llms = llms_filtered if llms_filtered else available_llms
    
    return available_llms

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
            http_client=client
        )
    
    return OpenAIEmbeddings(
        model=model_name, 
        base_url=Config.env_config['AI_BASE_URL'], 
        api_key=Config.env_config['AI_API_KEY'],
        request_timeout=None,
        max_retries=2,
        http_client=client,
    )