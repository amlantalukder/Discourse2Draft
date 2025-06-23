from langchain_openai import ChatOpenAI
import requests
from .utils import Config
import truststore
truststore.inject_into_ssl()

# ---------------------------------------------------------------------------
def extractAvailableLLMs(return_embedding_models=False) -> tuple[list, list]:
    """
    Extracts a list of available LLM names from LiteLLM proxy

    :return: list of available LLM names, list of available embedding model names
    """

    available_llms, available_embeddings = [], []
    litellm_api_key = Config.env_config['AI_API_KEY']
    try:
        response = requests.get(url=f'{Config.env_config.get("AI_BASE_URL")}/model/info',
                                headers={'API-Key': litellm_api_key})
        if response.ok:
            response_d = response.json()
            if response_d and ('data' in response_d):
                for item in response.json()['data']: 
                    if 'mode' not in item['model_info']: continue
                    if 'litellm_provider' not in item['model_info'] or item['model_info']['litellm_provider'] == 'ollama': continue
                    if item['model_info']['mode'] == 'chat':
                        available_llms.append(item['model_name'])
                    elif item['model_info']['mode'] == 'embedding':
                        available_embeddings.append(item['model_name'])
                
                available_llms = sorted(available_llms)
                available_embeddings = sorted(available_embeddings)

        else:
            print(response.text)

    except Exception as error:
        print('litellm proxy access error:', error)
    
    llms_filtered = {}
    if Config.llms_selected:
        for category, d in Config.llms_selected.items():
            category_filtered = {k:v for k, v in d.items() if k in available_llms}
            if category_filtered:
                llms_filtered[category] = category_filtered
    available_llms = llms_filtered if llms_filtered else available_llms

    if not return_embedding_models:
        return available_llms
    
    return available_llms, available_embeddings

# ---------------------------------------------------------------------------
def getOpenAIModel(model_name, temperature):

    return ChatOpenAI(
        model=model_name,
        base_url=Config.env_config.get('AI_BASE_URL'),
        api_key=Config.env_config.get('AI_API_KEY'),
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        seed=1000
    )