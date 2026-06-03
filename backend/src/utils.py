import dotenv
from pathlib import Path
from enum import Enum
from langfuse.langchain import CallbackHandler
from langfuse import Langfuse
import httpx
import truststore
import ssl
import os
import logging
import traceback
import functools
import inspect

# ---------------------------------------------------------------------------
class Versions(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

# ---------------------------------------------------------------------------
class Config:

    # ----------------------------------------------------------
    # Application configuration
    # ----------------------------------------------------------    
    current_version = Versions.DEVELOPMENT.value

    DIR_HOME = Path(__file__).parent.parent
    DIR_DATA = DIR_HOME / 'data'
    APP_NAME = 'Discourse2Draft'
    APP_NAME_AS_PREFIX = 'discourse2draft'
    DB_NAME = f'{APP_NAME_AS_PREFIX}-db'

    # ----------------------------------------------------------
    # Environment variables
    # ----------------------------------------------------------
    env_config = dotenv.dotenv_values(Path(".env"))

    # ----------------------------------------------------------
    # LLM and content generation settings
    # ----------------------------------------------------------

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

    # ----------------------------------------------------------
    # Debug configuration
    # ----------------------------------------------------------
    debug_config = {'print_log_messages': True,
                    'print_func_call': False,
                    'detailed': False}
    
    # ----------------------------------------------------------
    # Certificates configuration for secure connections
    # ----------------------------------------------------------
    truststore.inject_into_ssl()
    cert_path = DIR_HOME / 'certs/NIH-FULL.pem'
    if cert_path.exists():
        httpx_client = httpx.Client(verify=ssl.create_default_context(cafile=cert_path))
    else:
        httpx_client = None

    # ----------------------------------------------------------
    # Langfuse Tracing configuration
    # ----------------------------------------------------------
    langfuse_handler = None
    
    if bool(env_config.get("LANGFUSE_TRACING", False)):
        try:
            langfuse = Langfuse(
                public_key=env_config["LANGFUSE_PUBLIC_KEY"],
                secret_key=env_config["LANGFUSE_SECRET_KEY"],
                host=env_config["LANGFUSE_BASE_URL"],
                httpx_client=httpx_client
            )
            langfuse_handler = CallbackHandler()    
        except Exception as exp:
            logging.error(exp)

    # ----------------------------------------------------------
    # Set up logging
    # ----------------------------------------------------------
    log_file_path = DIR_HOME / 'logs' / 'app.log'
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path)
        ] if debug_config['print_log_messages'] else [
            logging.FileHandler(log_file_path)
        ],
    )

    # ----------------------------------------------------------
    # Ensure data directory exists
    # ----------------------------------------------------------
    DIR_CONTENTS = DIR_DATA / env_config['DB_HOST'] / DB_NAME
    DIR_CONTENTS.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def setEnvWithPrefix(prefix):
        for k, v in Config.env_config.items():
            if k.startswith(prefix):
                os.environ[k] = v

# ---------------------------------------------------------------------------
def traceError(exp):
    return f'Line number: {exp.__traceback__.tb_lineno}, Description: {exp}\n\n{traceback.format_exc()}'

# ---------------------------------------------------------------------------
def formatErrorString(error_action):
    return f'An error occurred {error_action}'

# ---------------------------------------------------------------------------
class SetupException(Exception):
    ...

# ---------------------------------------------------------------------------
def print_func_name(func):
    """
    A decorator that prints the name of the decorated function
    before it is executed.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if Config.debug_config['print_func_call']:

            if func.__qualname__.split('.')[-1].startswith('render'):
                func_name = f'[bold magenta]{func.__qualname__}[/bold magenta]'
            else:
                func_name = func.__qualname__

            if Config.debug_config['detailed']:
                func_args = inspect.signature(func).bind(*args, **kwargs).arguments
                func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
                print(f"Calling {func.__module__}.{func_name} ( {func_args_str} )")
                logging.info(f"Calling {func.__module__}.{func_name} ( {func_args_str} )")
            else:
                print(f"Calling {func.__module__}.{func_name}")
                logging.info(f"Calling {func.__module__}.{func_name}")
        return func(*args, **kwargs)
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        if Config.debug_config['print_func_call']:

            if func.__qualname__.split('.')[-1].startswith('render'):
                func_name = f'[bold magenta]{func.__qualname__}[/bold magenta]'
            else:
                func_name = func.__qualname__

            if Config.debug_config['detailed']:
                func_args = inspect.signature(func).bind(*args, **kwargs).arguments
                func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
                print(f"Calling {func.__module__}.{func_name} ( {func_args_str} )")
                logging.info(f"Calling {func.__module__}.{func_name} ( {func_args_str} )")
            else:
                print(f"Calling {func.__module__}.{func_name}")
                logging.info(f"Calling {func.__module__}.{func_name}")
        return await func(*args, **kwargs)

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return wrapper
