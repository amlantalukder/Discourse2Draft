import asyncio
import pandas as pd
from pathlib import Path
import json

from src.common import getDocContent
from src.eval.utils import Config
from src.eval.gen_content import generateContentByLitSearchAsync
from src.eval.extract_sections import extractSectionsForComparison
from src.eval.eval_content import evalRAGFramework, evalAndCompareTools

def runGeneration() -> None:

    with open(Config.dir_eval_with_tools / 'discourse2draft' / 'file_id_map.json') as fp:
        file_id_map = json.load(fp)

    for file_name in Config.file_names:
    
        gen_outline_file_path = Config.dir_eval_with_tools / 'discourse2draft' / 'outline' / file_name

        # Generate
        for config in Config.gen_eval_model_config:
            for gen_model_name in config['generator']:
                for index_run in range(1, Config.num_runs+1):
                    print(f'Generating content with {gen_model_name}, run index: {index_run}...')

                    file_id = file_id_map.get(f'{Path(file_name).stem}|{gen_model_name}|{index_run}', None)

                    gen_output_file_dir = Config.dir_eval_with_tools / 'discourse2draft' / gen_model_name / f'run_{index_run}'
                    gen_output_file_dir.mkdir(exist_ok=True, parents=True)
                    gen_output_file_path = gen_output_file_dir / f'{Path(file_name).stem}.json'
                    file_id, vector_db_collections_id_uploaded_files, vector_db_collections_id_literature = asyncio.run(generateContentByLitSearchAsync(gen_model_name=gen_model_name, 
                                                                                                                                                    gen_outline_file_path=gen_outline_file_path,
                                                                                                                                                    gen_file_id=file_id))

                    content_md, *_ = getDocContent(file_id, vector_db_collections_id_uploaded_files, vector_db_collections_id_literature)
                    gen_output_md_file_path = gen_output_file_path.parent / f'{Path(file_name).stem}.md'
                    with open(gen_output_md_file_path, 'w') as fp:
                        fp.write(content_md)

                    file_id_map[f'{Path(file_name).stem}|{gen_model_name}|{index_run}'] = file_id

                    with open(Config.dir_eval_with_tools / 'discourse2draft' / 'file_id_map.json', 'w') as fp:
                        json.dump(file_id_map, fp, indent=4)

        # Extract sections from the generated content markdown and 
        # create a table of sections and toolwise content for comparison
        extractSectionsForComparison(file_name=file_name)

def runEvaluation() -> None:

    for file_name in Config.file_names:

        section_sets = pd.read_csv(Config.dir_eval_with_tools / 'sections_to_compare' / f'{Path(file_name).stem}.csv', index_col=0)

        external_tools = [tool for tool in Config.tools if tool != 'discourse2draft'] 

        # Eval and compare content
        for config in Config.gen_eval_model_config:
            for gen_model_name in config['generator']:
                for index_run in range(1, Config.num_runs+1):
                    for eval_model_name in config['evaluator']:
                        print(f'Evaluating content for {gen_model_name}, run index: {index_run} with {eval_model_name}...')
                        evalAndCompareTools(section_sets=section_sets[external_tools + [f'discourse2draft|{gen_model_name}|run_{index_run}']], gen_content_file_name=file_name, eval_model_name=eval_model_name)

        # Eval rag
        # for config in Config.gen_eval_model_config:
        #     for gen_model_name in config['generator']:
        #         gen_output_file_path = Config.dir_eval_with_tools / 'discourse2draft' / 'output' / gen_model_name / f'{file_name.stem}.json'
        #         for eval_model_name in config['evaluator']:
        #             evalRAGFramework(eval_model_name=eval_model_name, gen_output_file_path=gen_output_file_path)


if __name__ == "__main__":
    runGeneration()
    runEvaluation()
