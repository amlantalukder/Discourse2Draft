from shiny import reactive
from shiny.express import ui, render, module
import faicons
import json
import asyncio
from utils import Config, print_func_name
from .defaults import SpecialSectionTypes, ContentTypes

@module
def mod_concept_map(input, output, session, config_app):

    with ui.hold() as content:
        with ui.div(class_='d-flex p-3', style='background-color: #ececec'):
            ui.div(class_='col-auto')
            with ui.div(class_='col d-flex justify-content-center'):
                ui.h4(f'Concept Map for "{config_app.file_name[:50] + (' ...' if len(config_app.file_name) > 50 else '')}"')
            with ui.div(class_='col-auto d-flex justify-content-end'):
                @render.download(label=faicons.icon_svg("download"), filename=f'{config_app.file_name}.json')
                @print_func_name
                async def renderDownloadConceptMap():
                    yield json.dumps(getConceptMapData())    
        ui.div(id='graph', class_='graph-container')

    @reactive.calc
    def getConceptMapData():

        def extractConceptMapFromAIGeneratedMap(d_map, nodes, current_node, node_counter):

            concept_map = {current_node: []}
            for n in nodes:
                concept_map[current_node].append(f'{n}#{node_counter}')
                concept_map_part, node_counter = extractConceptMapFromAIGeneratedMap(d_map, d_map.get(n, []), f'{n}#{node_counter}', node_counter+1) 
                concept_map |= concept_map_part
            return concept_map, node_counter

        def extractConceptMapFromOutline(d_outline, current_node, node_counter):

            concept_map = {current_node: []}
            for k, v in d_outline.items():
                if k != SpecialSectionTypes.CONTENT.value:
                    concept_map[current_node].append(f'{k}#{node_counter}')
                    concept_map_part, node_counter = extractConceptMapFromOutline(v, f'{k}#{node_counter}', node_counter+1)
                    concept_map |= concept_map_part
                else:
                    for content_type, content_value in d_outline[k]:
                        if content_type == ContentTypes.CONCEPT_MAP.value:
                            # In the content_value dictionary, find the nodes with no incoming, 
                            # as only these nodes would be the children of the current_node
                            nodes_with_in_deg = set()
                            for _, n_nei in content_value.items():
                                nodes_with_in_deg |= set(n_nei)
                            nodes_with_no_in_deg = set(content_value.keys()) - nodes_with_in_deg
                            for n in nodes_with_no_in_deg:
                                concept_map[current_node].append(f'{n}#{node_counter}')
                                concept_map_part, node_counter = extractConceptMapFromAIGeneratedMap(content_value, content_value[n], f'{n}#{node_counter}', node_counter+1) 
                                concept_map |= concept_map_part
            return concept_map, node_counter

        outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'

        if not outline_file_path.exists(): return {}

        with open(outline_file_path, 'r') as fp:
            d_outline = json.load(fp)
            
        concept_map = {}
        node_counter = 0
        for k, v in d_outline.items():
            concept_map_part, node_counter = extractConceptMapFromOutline(v, f'{k}#{node_counter}', node_counter+1)
            concept_map |= concept_map_part
        return concept_map
    
    @reactive.effect
    def loadConceptMap():
        
        loop = asyncio.get_event_loop()
        loop.create_task(session.send_custom_message('concept_map', {'conceptMap': getConceptMapData()}))

    return content