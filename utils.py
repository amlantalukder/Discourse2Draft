from pathlib import Path
import uuid
import functools
import inspect
from rich import print
import logging
from logging.handlers import RotatingFileHandler
from src.backend.utils import Config as backend_config

class Config:

    DIR_HOME = Path(__file__).parent
    DIR_DATA = DIR_HOME / 'data'
    APP_NAME = 'Discourse2Draft'
    APP_NAME_AS_PREFIX = 'discourse2draft'

    debug_config = {'print': True,
                    'print_func_call': True,
                    'detailed': False,
                    'debug_ai': False}
    
    if debug_config['debug_ai']:
        backend_config.setEnvWithPrefix('LANGFUSE')

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
        ] if debug_config['print'] else [
            logging.FileHandler(log_file_path)
        ],
    )

    # ----------------------------------------------------------
    # Ensure data directory exists
    # ----------------------------------------------------------
    DIR_CONTENTS = DIR_DATA / backend_config.env_config['HOST'] / backend_config.env_config['DATABASE']
    DIR_CONTENTS.mkdir(parents=True, exist_ok=True)

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

@print_func_name
def getUIID(prefix):
    return f'{prefix}_{str(uuid.uuid4()).replace('-', '_')}'