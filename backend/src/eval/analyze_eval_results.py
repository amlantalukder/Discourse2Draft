import pandas as pd
import plotly.express as px
from pathlib import Path

from .utils import Config

def plotEvalScores(feature_names, tool_names, color_discrete_map, dir_scores, processScores, color_discrete_order=None):

    base_font_size = 16
    axis_tick_font_size = 14
    facet_font_size = 18
    title_font_size = 24

    generators, evaluators = [], []
    for config in Config.gen_eval_model_config:
        generators += config['generator']
        evaluators += config['evaluator']

    generators = sorted(generators)
    evaluators = sorted(set(evaluators))
    color_discrete_order = color_discrete_order or list(color_discrete_map.keys())

    for i, file_name in enumerate(Config.file_names):
        rating_scores_all = pd.DataFrame()
        for evaluator in evaluators:
            rating_scores = pd.read_csv(dir_scores / evaluator / f'{Path(file_name).stem}.csv', index_col=0)
            rating_scores = processScores(rating_scores, evaluator)
            rating_scores_all = pd.concat([rating_scores_all, rating_scores])

        score_columns = rating_scores_all.select_dtypes(include='number').columns
        rating_score_groups = rating_scores_all.groupby(['Tools', 'Features'])[score_columns]
        rating_scores = rating_score_groups.mean().reset_index().melt(id_vars=['Tools', 'Features'], var_name='Section Name', value_name='Score')
        rating_score_ranges = rating_score_groups.min().reset_index().melt(id_vars=['Tools', 'Features'], var_name='Section Name', value_name='Score Min')
        rating_score_ranges = rating_score_ranges.merge(
            rating_score_groups.max().reset_index().melt(id_vars=['Tools', 'Features'], var_name='Section Name', value_name='Score Max'),
            on=['Tools', 'Features', 'Section Name'],
            how='left',
        )
        rating_scores = rating_scores.merge(rating_score_ranges, on=['Tools', 'Features', 'Section Name'], how='left')
        rating_scores['Score Range Upper'] = rating_scores['Score Max'] - rating_scores['Score']
        rating_scores['Score Range Lower'] = rating_scores['Score'] - rating_scores['Score Min']
        rating_scores = rating_scores.loc[rating_scores['Section Name'] != '# Title']
        rating_scores['Features'] = rating_scores['Features'].map(feature_names)
        rating_scores['Tools'] = rating_scores['Tools'].map(tool_names)
        rating_scores = rating_scores.query('`Section Name` != "## References" or Features != "Continuity"')
        score_min = rating_scores['Score Min'].min()
        score_max = rating_scores['Score Max'].max()
        if pd.isna(score_min) or pd.isna(score_max):
            score_axis_range = [0, 100]
        else:
            score_axis_range = [max(0, score_min - 10), min(score_max + 10, 100)]

        fig = px.bar(
            rating_scores,
            x='Section Name',
            y='Score',
            color='Tools',
            barmode='group',
            facet_col='Features',
            title='Content Evaluation Scores by Section and Tool',
            color_discrete_map=color_discrete_map,
            category_orders={'Tools': color_discrete_order},
            error_y='Score Range Upper',
            error_y_minus='Score Range Lower',
        )
        fig.update_traces(error_y={'thickness': 1.3, 'width': 4})
        xaxis_options = {'title': '', 'tickangle': 45, 'tickfont': {'size': axis_tick_font_size}}
        fig.update_xaxes(**xaxis_options)
        fig.update_yaxes(title_font={'size': base_font_size}, tickfont={'size': axis_tick_font_size}, range=score_axis_range)
        for annot in fig.layout.annotations:
            annot.text = annot.text.split('=')[1]
            annot.font = {'size': facet_font_size}
        layout_options = {
            'title': Path(file_name).stem,
            'template': 'plotly_white',
            'title_x': 0.5,
            'font': {'size': base_font_size},
            'title_font': {'size': title_font_size},
            'width': 1600,
            'height': 700,
        }
        if i == 0:
            fig.update_layout(
                **layout_options,
                legend={'y':1.5, 'x':0, 'orientation':'h', 'font': {'size': base_font_size}},
            )
        else:
            fig.update_layout(**layout_options, showlegend=False)

        saveFigure(fig=fig, output_dir=dir_scores / 'plots', file_name=file_name)

def interpolateHexColor(start_hex, end_hex, step, total_steps):
    if total_steps <= 1:
        return start_hex

    start_rgb = tuple(int(start_hex[index:index+2], 16) for index in (1, 3, 5))
    end_rgb = tuple(int(end_hex[index:index+2], 16) for index in (1, 3, 5))
    ratio = step / (total_steps - 1)
    mixed_rgb = tuple(round(start + (end - start) * ratio) for start, end in zip(start_rgb, end_rgb))
    return '#{:02x}{:02x}{:02x}'.format(*mixed_rgb)

def saveFigure(fig, output_dir, file_name):
    output_dir.mkdir(exist_ok=True, parents=True)
    output_path = output_dir / f'{Path(file_name).stem}.html'
    fig.write_html(output_path, include_plotlyjs=True, auto_open=False)
    print(f'Plot saved to {output_path}')

def plotContentGenerationEvalScores():    

    feature_names = {'relevance': 'Relevance', 'continuity': 'Continuity', 'non_repetitiveness': 'Non-Repetitiveness', 'specificity': 'Specificity'}
    tool_names = {'chatgpt_deepresearch': 'ChatGPT DeepResearch', 'manus_ai': 'Manus AI'}
    tool_names.update({f'discourse2draft|run_{index}': f'Discourse2Draft (Run {index})' for index in range(1, Config.num_runs+1)})

    discourse2draft_reds = [
        interpolateHexColor('#fb6a4a', '#a50f15', index, Config.num_runs)
        for index in range(Config.num_runs)
    ]
    color_discrete_order = [
        'ChatGPT DeepResearch',
        'Manus AI',
    ] + [
        f'Discourse2Draft (Run {index})'
        for index in range(1, Config.num_runs+1)
    ]
    color_discrete_map = {
        'ChatGPT DeepResearch': '#1f77b4',
        'Manus AI': '#2ca02c',
    }
    color_discrete_map.update({
        f'Discourse2Draft (Run {index})': discourse2draft_reds[index-1]
        for index in range(1, Config.num_runs+1)
    })

    def processScores(rating_scores, evaluator):
        def extractGeneratorModel(x):
            tool, feature = x.split(' ')
            if not x.startswith('discourse2draft'):
                return tool, feature, None
            tool, generator, run = tool.split('|')
            return f'{tool}|{run}', feature, generator

        rating_scores['Tools'], rating_scores['Features'], rating_scores['Generators'] = zip(*rating_scores.index.to_series().apply(extractGeneratorModel))
        rating_scores['Evaluator'] = evaluator
        return rating_scores

    dir_scores = Config.dir_eval_with_tools / 'results' / 'content_generation' / 'scores'

    plotEvalScores(feature_names, tool_names, color_discrete_map, dir_scores, processScores, color_discrete_order=color_discrete_order)

def plotKeyphrasesGenerationEvalScores():

    feature_names = {'relevance': 'Relevance', 'completeness': 'Completeness', 'specificity': 'Specificity'}
    tool_names = {f'discourse2draft|run_{index}': f'Discourse2Draft (Run {index})' for index in range(1, Config.num_runs+1)}

    discourse2draft_reds = [
        interpolateHexColor('#fb6a4a', '#a50f15', index, Config.num_runs)
        for index in range(Config.num_runs)
    ]
    color_discrete_map = {
        f'Discourse2Draft (Run {index})': discourse2draft_reds[index-1]
        for index in range(1, Config.num_runs+1)
    }

    def processScores(rating_scores, evaluator):
        def extractGeneratorModel(x):
            tool, feature = x.split(' ')
            if not x.startswith('discourse2draft'):
                return tool, feature, None
            tool, generator, run = tool.split('|')
            return f'{tool}|{run}', feature, generator

        rating_scores['Tools'], rating_scores['Features'], rating_scores['Generators'] = zip(*rating_scores.index.to_series().apply(extractGeneratorModel))
        rating_scores['Evaluator'] = evaluator
        return rating_scores

    dir_scores = Config.dir_eval_with_tools / 'results' / 'keyphrases_generation' / 'scores'

    plotEvalScores(feature_names, tool_names, color_discrete_map, dir_scores, processScores)


def plotContextRetrievalEvalScores(is_eval_citations=False):

    feature_names = {'relevance': 'Relevance', 'specificity': 'Specificity'}
    tool_names = {f'discourse2draft|run_{index}': f'Discourse2Draft (Run {index})' for index in range(1, Config.num_runs+1)}

    discourse2draft_reds = [
        interpolateHexColor('#fb6a4a', '#a50f15', index, Config.num_runs)
        for index in range(Config.num_runs)
    ]
    color_discrete_map = {
        f'Discourse2Draft (Run {index})': discourse2draft_reds[index-1]
        for index in range(1, Config.num_runs+1)
    }

    def processScores(rating_scores, evaluator):
        def extractGeneratorModel(x):
            tool, feature = x.split(' ')
            if not x.startswith('discourse2draft'):
                return tool, feature, None
            tool, generator, run = tool.split('|')
            return f'{tool}|{run}', feature, generator

        rating_scores['Tools'], rating_scores['Features'], rating_scores['Generators'] = zip(*rating_scores.index.to_series().apply(extractGeneratorModel))
        rating_scores['Evaluator'] = evaluator
        return rating_scores

    if not is_eval_citations:
        dir_scores = Config.dir_eval_with_tools / 'results' / 'context_retrieval' / 'scores'
    else:
        dir_scores = Config.dir_eval_with_tools / 'results' / 'citations' / 'scores'

    plotEvalScores(feature_names, tool_names, color_discrete_map, dir_scores, processScores)
    
