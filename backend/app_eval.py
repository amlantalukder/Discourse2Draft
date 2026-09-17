import asyncio
import pandas as pd
from pathlib import Path
import json

from src.common import getDocContent
from src.eval.utils import Config
from src.eval.gen_content import generateContentByLitSearchAsync
from src.eval.extract_sections import extractSectionsForComparison
from src.eval.eval_content import evalAndCompareTools
from src.eval.eval_retrieval import evalRAGFramework
from src.eval.analyze_eval_results import plotContentGenerationEvalScores, plotKeyphrasesGenerationEvalScores, plotContextRetrievalEvalScores

def runGeneration() -> None:

    file_map_path = Config.dir_eval_with_tools / 'discourse2draft' / 'file_id_map.json'
    if file_map_path.exists():
        with open(file_map_path) as fp:
            file_id_map = json.load(fp)
    else:
        file_id_map = {}

    for file_name in Config.file_names:
    
        gen_outline_file_path = Config.dir_eval_with_tools / 'discourse2draft' / 'outline' / file_name

        # Generate
        for config in Config.gen_eval_model_config:
            for gen_model_name in config['generator']:
                for index_run in range(1, Config.num_runs+1):
                    print(f'Generating content with {gen_model_name} AI model, run index: {index_run}...')

                    file_id = file_id_map.get(f'{Path(file_name).stem}|{gen_model_name}|run_{index_run}', None)

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

                    file_id_map[f'{Path(file_name).stem}|{gen_model_name}|run_{index_run}'] = file_id

                    with open(file_map_path, 'w') as fp:
                        json.dump(file_id_map, fp, indent=4)

        # Extract sections from the generated content markdown and 
        # create a table of sections and toolwise content for comparison
        extractSectionsForComparison(file_name=file_name)

def runEvaluation() -> None:

    with open(Config.dir_eval_with_tools / 'discourse2draft' / 'file_id_map.json') as fp:
        file_id_map = json.load(fp)

    for file_name in Config.file_names:

        #if not file_name.startswith('Health Impacts'): continue

        section_sets = pd.read_csv(Config.dir_eval_with_tools / 'sections_to_compare' / f'{Path(file_name).stem}.csv', index_col=0)

        external_tools = [tool for tool in Config.tools if tool != 'discourse2draft']

        # Eval and compare content
        evaluator_generator_map = {}
        for config in Config.gen_eval_model_config:
            for eval_model_name in config['evaluator']:
                evaluator_generator_map[eval_model_name] = evaluator_generator_map.get(eval_model_name, []) + config['generator']
        
        for eval_model_name, gen_models in evaluator_generator_map.items():

            #if eval_model_name == 'gemini-3.5-flash': continue

            gen_list, tool_list = [], []
            for gen_model_name in gen_models:
                for index_run in range(1, Config.num_runs+1):
                    tool_name = f'discourse2draft|{gen_model_name}|run_{index_run}'
                    tool_list.append(tool_name)
                    gen_file_index = f'{Path(file_name).stem}|{gen_model_name}|run_{index_run}'
                    gen_list.append((tool_name, file_id_map[gen_file_index]))

            relevant_columns = external_tools + tool_list
            print('='*70, f'{f'Evaluating and comparing content for {file_name} with {eval_model_name} AI model...':20}', '='*70, sep='\n\n')

            evalAndCompareTools(section_sets=section_sets[relevant_columns], gen_content_file_name=file_name, eval_model_name=eval_model_name)
            evalRAGFramework(gen_content_file_name=file_name, gen_list=gen_list, eval_model_name=eval_model_name)


if __name__ == "__main__":
    #runGeneration()
    #runEvaluation()
    plotContentGenerationEvalScores()
    plotKeyphrasesGenerationEvalScores()
    plotContextRetrievalEvalScores()
    plotContextRetrievalEvalScores(is_eval_citations=True)