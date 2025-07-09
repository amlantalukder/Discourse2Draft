from pathlib import Path
import uuid
import functools
import inspect
from rich import print
from src.backend.ai.utils import Config as ai_config

class Config:

    DIR_HOME = Path(__file__).parent
    DIR_DATA = DIR_HOME / 'data'
    APP_NAME = 'AI Word Processor'

    debug_config = {'print': True,
                    'detailed': False,
                    'debug_ai': False}
    
    if debug_config['debug_ai']:
        ai_config.setEnvWithPrefix('LANGCHAIN')


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def getUIID(prefix):

    return f'{prefix}_{str(uuid.uuid4()).replace('-', '_')}'

def print_func_name(func):
    """
    A decorator that prints the name of the decorated function
    before it is executed.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if Config.debug_config['print']:

            if func.__qualname__.split('.')[-1].startswith('render'):
                func_name = f'[bold magenta]{func.__qualname__}[/bold magenta]'
            else:
                func_name = func.__qualname__

            if Config.debug_config['detailed']:
                func_args = inspect.signature(func).bind(*args, **kwargs).arguments
                func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
                print(f"Calling {func.__module__}.{func_name} ( {func_args_str} )")
            else:
                print(f"Calling {func.__module__}.{func_name}")
        return func(*args, **kwargs)
    return wrapper