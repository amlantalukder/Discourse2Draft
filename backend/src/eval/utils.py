from ..utils import Config as set_up_config

class Config:

    dir_evals = set_up_config.DIR_DATA / 'evals'
    dir_eval_with_tools = dir_evals / 'comparison_with_other_tools'
    if not dir_evals.exists(): print(f"Directory {dir_evals} does not exist.")

    tools = ['chatgpt_deepresearch', 'manus_ai', 'discourse2draft']

    num_runs = 3
    
    file_names = ['CRISPR-based editing for inherited blood disorders.md', 'Phthalates Toxicity.md', 'PFAS.md']

    gen_eval_model_config = [
        {
            'generator': ['azure-gpt-5.6-terra'],
            'evaluator': ['gemini-3.5-flash', 'claude-haiku-4.5']
        },
        {
            'generator': ['gemini-3.1-pro'],
            'evaluator': ['azure-gpt-5.6-luna', 'claude-haiku-4.5']
        },
        {
            'generator': ['claude-sonnet-4.6'],
            'evaluator': ['azure-gpt-5.6-luna', 'gemini-3.5-flash']
        }
    ]
    num_runs = 3

    RETRY_COUNTER = 2
