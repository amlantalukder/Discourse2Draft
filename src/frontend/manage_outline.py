from shiny import reactive, ui as core_ui
from shiny.express import ui, render, module
from shiny.types import FileInfo
from utils import print_func_name, getUIID
from ..backend.ai.llms import extractAvailableLLMs
from ..backend.ai.architecture import ArchitectureOutline
import faicons
import re

@print_func_name
def insertOutline(d, outline_items):

    if len(outline_items) == 1:
        d['content'] = d.get('content', []) + outline_items
        return d
    
    if outline_items[0] not in d:
        d[outline_items[0]] = {}
    
    d[outline_items[0]] = insertOutline(d[outline_items[0]].copy(), outline_items[1:])

    return d

@print_func_name
def processOutline(outline):

    d_outline, outline_items = {}, []
    chunks_leading_to_content = outline.split('<content>')
    for i, x in enumerate(chunks_leading_to_content):
        x = x.strip()
        if not x: continue
        text = ''
        for line_x in x.split('\n'):
    
            line_x = line_x.strip()
            if not line_x: continue
            if not line_x.startswith('#'):
                text += line_x
                continue

            if text: 
                d_outline = insertOutline(d_outline.copy(), outline_items + [['content_user', text]])
                text = ''
            
            hashes = line_x.split()[0]
            header = ' '.join(line_x.split()[1:])
            
            if hashes != '#' * len(hashes):
                ui.notification_show("'#'s must be followed by a space", type="error")
                return False
            
            if len(hashes) > len(outline_items) + 1:
                ui.notification_show(f"Expected no more than {len(outline_items) + 1} '#'s before {text}", type="error")
                return False
            
            if len(hashes) <= len(outline_items):
                outline_items = outline_items[:len(hashes)-1]

            outline_items.append(header)
            
        if text: 
            d_outline = insertOutline(d_outline.copy(), outline_items + [['content_user', text]])
            
        if i < len(chunks_leading_to_content)-1:
            d_outline = insertOutline(d_outline.copy(), outline_items + [['content_ai', '']])

    return d_outline

@print_func_name
def getOutlineHierarchyList(d, outline_hierarchy=[], current_hierarchy=[], counter=1):

    if not isinstance(d, dict):
        for k, v in d:
            if k == 'content_ai':
                outline_hierarchy.append(current_hierarchy)
                return outline_hierarchy
            else:
                current_hierarchy.append(v)
    else:
        for k in d:
            if k == 'References':
                continue
            outline_hierarchy = getOutlineHierarchyList(d[k], outline_hierarchy, current_hierarchy + [f'{'#' * counter} {k}'] if k != 'content' else current_hierarchy, counter+1)

    return outline_hierarchy 

@print_func_name
def getRawOutline(d, raw_outline=[], counter=1):

    if not isinstance(d, dict):
        for k, v in d:
            if k == 'content_ai':
                raw_outline.append('<content>')
            else:
                raw_outline.append(v)
    else:
        for k in d:
            if k == 'References':
                continue
            raw_outline = getRawOutline(d[k], raw_outline + [f'{'#' * counter} {k}'] if k != 'content' else raw_outline, counter+1)

    return raw_outline                                         

@module
def mod_outline_manager(input, output, session, outline, saved_outline, close_fn):

    @module
    def mod_outline_tools(input, output, session, id_suffix, text, show_insert_above=True, show_insert_within=True, show_remove=True):

        show_text = reactive.value(False)
        is_edit_mode = reactive.value(False)

        with ui.hold() as content:
            with ui.div(class_='d-flex justify-content-between gap-2'):
                @render.express
                @print_func_name
                def renderText():
                    if show_text.get():
                        ui.input_text_area('text_text', '', resize='vertical')
                    elif text == '[Reserved for AI content]':
                        ui.p(text, class_='reserved-for-ai')
                    else:
                        ui.markdown(text)
                    
                    with ui.div(class_='d-flex gap-2 align-items-center'):                                                                       
                        if show_insert_above:
                            if 'content' not in id_suffix:
                                with ui.tooltip():
                                    ui.input_action_link('btn_insert_header_above', '', icon=faicons.icon_svg("plus"))
                                    'Insert "Header" above'
                            else:
                                with ui.tooltip():
                                    with ui.div():
                                        with ui.popover(placement='bottom', options={'trigger': 'click'}):
                                            ui.input_action_link('btn_insert_text_above_options', '', icon=faicons.icon_svg("plus"))
                                            with ui.div(class_='d-flex flex-column gap-2'):
                                                ui.strong('Insert following content type above this text')
                                                ui.input_radio_buttons('radio_text_type_insert_above', 'Content type', choices=['Text', 'AI'], inline=True)
                                                ui.input_action_button('btn_insert_above', 'Insert above')
                                    'Insert above'
                        if show_insert_within:
                            with ui.tooltip():
                                with ui.div():
                                    with ui.popover(placement='bottom', options={'trigger': 'click'}):
                                        ui.input_action_link('btn_insert_within_options', '', icon=faicons.icon_svg("arrow-right-to-bracket"))
                                        with ui.div(class_='d-flex flex-column gap-2'):
                                            ui.strong('Insert following content type within this header')
                                            ui.input_radio_buttons('radio_text_type_insert_within', 'Content type', choices=['Header', 'Text', 'AI'], inline=True)
                                            ui.input_action_button('btn_insert_within', 'Insert within')
                                'Insert within'
                        if show_remove:
                            with ui.tooltip():
                                ui.input_action_link('btn_remove', '', icon=faicons.icon_svg("xmark"))
                                'Remove'                 
                        if not show_text.get():
                            with ui.tooltip():
                                ui.input_action_link('btn_edit', '', icon=faicons.icon_svg("pen"))
                                'Edit'
                        else:
                            if is_edit_mode.get():
                                with ui.tooltip():
                                    ui.input_action_link('btn_undo', '', icon=faicons.icon_svg("rotate-left"))
                                    'Undo'                             
                            with ui.tooltip():
                                ui.input_action_link('btn_save', '', icon=faicons.icon_svg("floppy-disk"))
                                'Save'                            

        @print_func_name
        def manageOutline(action, d, id_suffix_prev=''):
            d_new = []
            i_new = 0
            
            for i, k in enumerate(list(d.keys())):
                if k == 'References':
                    continue
                if k.startswith('content'):
                    if 'content' not in id_suffix:
                        d_new.append((k, d[k]))
                        continue
                    values = []
                    for i_content, (v1, v2) in enumerate(d[k]):
                        id_suffix_current = f'{id_suffix_prev}_{i}_content{i_content}' if id_suffix_prev else f'{i}_content{i_content}'
                        match action['type']:
                            case 'insert_above':
                                if id_suffix_current == id_suffix:
                                    match action['text_type']:
                                        case 'Text':
                                            values.append(('content_user', '<new>'))
                                        case 'AI':
                                            values.append(('content_ai', ''))
                                values.append((v1, v2))
                            case 'remove':
                                if id_suffix_current != id_suffix:
                                    values.append((v1, v2))
                            case 'edit':
                                if id_suffix_current == id_suffix:
                                    values.append((v1, action['text_new']))
                                else:
                                    values.append((v1, v2))
                    d_new.append((k, values))
                    continue

                id_suffix_current = f'{id_suffix_prev}_{i}' if id_suffix_prev else f'{i}'
                match action['type']:
                    case 'insert_above':
                        if id_suffix_current == id_suffix:
                            d_new.append((f'<new>_{i_new}', {}))
                            i_new += 1
                        if k.startswith('<new>'):
                            d_new.append((f'<new>_{i_new}', d[k])) 
                            i_new += 1
                        else:
                            d_new.append((k, manageOutline(action, d[k], id_suffix_prev=id_suffix_current)))
                    case 'insert_within':
                        if id_suffix_current == id_suffix:
                            if action['text_type'] == 'Header':
                                d_new.append((k, dict([(f'<new>_{i_new}', {})] + list(d[k].items()))))        
                            else:
                                if action['text_type'] == 'Text':
                                    contents = [(f'content_user', '<new>')] + d[k].get('content', [])
                                else:
                                    contents = [(f'content_ai', '')] + d[k].get('content', [])
                                d_new.append((k, {**d[k], **{'content': contents}}))
                            i_new += 1
                        else:
                            d_new.append((k, manageOutline(action, d[k], id_suffix_prev=id_suffix_current)))
                    case 'remove':
                        if id_suffix_current != id_suffix:
                            d_new.append((k, d[k] if k.startswith('<new>') else manageOutline(action, d[k], id_suffix_prev=id_suffix_current)))
                    case 'edit':
                        if id_suffix_current == id_suffix:
                            d_new.append((action['text_new'], manageOutline(action, d[k], id_suffix_prev=id_suffix_current)))
                        else:
                            d_new.append((k, d[k] if k.startswith('<new>') else manageOutline(action, d[k], id_suffix_prev=id_suffix_current))) 
                
            return dict(d_new) 

        @reactive.effect
        @print_func_name
        def isText():
            show_text.set(text.startswith('<new>'))

        @reactive.effect
        @reactive.event(input.btn_insert_header_above, ignore_init=True)
        @print_func_name
        def insert_header_above():
            action = {'type': 'insert_above'}
            d_outline.set(manageOutline(action, d_outline.get()))

        @reactive.effect
        @reactive.event(input.btn_insert_above, ignore_init=True)
        @print_func_name
        def insert_text_above():
            text_type = input.radio_text_type_insert_above()
            if text_type not in ['Text', 'AI']: return
            action = {'type': 'insert_above', 'text_type': text_type}
            d_outline.set(manageOutline(action, d_outline.get()))

        @reactive.effect
        @reactive.event(input.btn_insert_within, ignore_init=True)
        @print_func_name
        def insert_within():
            text_type = input.radio_text_type_insert_within()
            if text_type not in ['Header', 'Text', 'AI']: return
            action = {'type': 'insert_within', 'text_type': text_type}
            d_outline.set(manageOutline(action, d_outline.get()))

        @reactive.effect
        @reactive.event(input.btn_remove, ignore_init=True)
        @print_func_name
        def remove():
            action = {'type': 'remove'}
            d_outline.set(manageOutline(action, d_outline.get()))

        @reactive.effect
        @reactive.event(input.btn_edit)
        @print_func_name
        def edit():
            show_text.set(True)
            is_edit_mode.set(True)
            ui.update_text_area(id='text_text', value=re.sub('^#+ ', '', text))

        @reactive.effect
        @reactive.event(input.btn_undo)
        @print_func_name
        def undo():
            show_text.set(text.startswith('<new>'))
            is_edit_mode.set(False)

        @reactive.effect
        @reactive.event(input.btn_save)
        @print_func_name
        def save():
            text_new = input.text_text().strip()
            if text_new == '': return

            action = {'type': 'edit', 'text_new': text_new}
            d_outline.set(manageOutline(action, d_outline.get()))

        return content

    d_outline = reactive.value({})

    with ui.hold() as content:
        with ui.div(class_='outline-manager-container'):
            with ui.div(class_='d-flex justify-content-between'):
                ui.h4('Outline')
                with ui.div(class_='d-flex gap-2'):
                    with ui.tooltip():
                        ui.input_action_button('btn_undo', '', icon=faicons.icon_svg("rotate-left"))
                        'Undo changes'
                    with ui.tooltip():
                        ui.input_action_button('btn_save', '', icon=faicons.icon_svg("floppy-disk"))
                        'Save changes'
                    with ui.tooltip():
                        ui.input_action_button('btn_close', '', icon=faicons.icon_svg("xmark"))
                        'Close'
            with ui.div(class_='outline-manager outline'):
                @render.ui
                @print_func_name
                def renderOutlineHierarchy():

                    print_func_name
                    def loadHierarchy(d, level=0, id_suffix_prev=''):

                        outline_ui_elements = []
                        
                        for index, k in enumerate(list(d.keys())):
                            if k == 'References':
                                continue
                                
                            if k.startswith('content'):
                                show_insert_within = False
                                for index_content, (v1, v2) in enumerate(d[k]):
                                    id_suffix_current = f'{id_suffix_prev}_{index}_content{index_content}' if id_suffix_prev else f'{index}_content{index_content}'
                                    text = v2 if v2.startswith('<new>') else '[Reserved for AI content]' if v1 == 'content_ai' else v2
                                    outline_ui_elements.append(
                                        core_ui.div(
                                            mod_outline_tools(id=getUIID(id_suffix_current), id_suffix=id_suffix_current, text=text, show_insert_within=show_insert_within),    
                                            class_='ps-4'
                                        )
                                    )
                                continue

                            id_suffix_current = f'{id_suffix_prev}_{index}' if id_suffix_prev else f'{index}'
                            text = f'{'#' * (level+1)} {k}' if not k.startswith('<new>') else k
                            outline_ui_elements.append(
                                core_ui.div(
                                    mod_outline_tools(id=getUIID(id_suffix_current), 
                                                        id_suffix=id_suffix_current, 
                                                        text=text, 
                                                        show_insert_above=(level > 0),
                                                        show_insert_within=(not k.startswith('<new>')),
                                                        show_remove=(level > 0)),
                                    loadHierarchy(d[k], level=level+1, id_suffix_prev = id_suffix_current) if not k.startswith('<new>') else '',
                                    class_='ps-4' if level > 0 else ''
                                )   
                            )

                        return outline_ui_elements
                    
                    return loadHierarchy(d_outline.get())
                        
    @reactive.calc
    @print_func_name
    def reset():
        if outline == '': return {}
        return processOutline(outline=outline)

    @reactive.effect
    @print_func_name
    def load():
        d_outline.set(reset())

    @reactive.effect
    @reactive.event(input.btn_close)
    @print_func_name
    def close():
        close_fn()

    @reactive.effect
    @reactive.event(input.btn_undo)
    @print_func_name
    def undo():
        d_outline.set(reset())

    @reactive.effect
    @reactive.event(input.btn_save)
    @print_func_name
    def save():
        saved_outline.set('\n'.join(getRawOutline(d_outline.get())))
        ui.modal_remove()
                        
    return content

@module
def mod_ai_outline_creator(input, output, session, outline_creator_options, saved_outline, show_init_view=True):

    show_create_outline_view = reactive.value(not show_init_view)
    outline_from_outline_manager = reactive.value('')
    outline_content = reactive.value('Outline will appear here')
    topic_desc = reactive.value('')
    
    with ui.div(class_='outline-creator-container'):
        @render.express
        @print_func_name
        def renderView():
            if not show_create_outline_view.get():
                with ui.div(class_='outline-creator-init-view'):
                    ui.input_action_button('btn_show_create_outline_ai', 'Create outline with AI')
                    ui.span('OR')
                    ui.input_action_button('btn_use_custom_outline', 'Use custom outline')
                    return
            
            with ui.div(class_='outline-creator'):
                with ui.div(class_='outline-creator-controls'):
                    with ui.accordion(open=False, multiple=False):
                        with ui.accordion_panel('AI settings'):
                            with ui.div(class_='row justify-content-between'):
                                ui.input_selectize('select_llm', 'LLM', choices=extractAvailableLLMs())
                                ui.input_slider('slide_temp', 'Temperature', min=0, max=1, step=0.1, value=0)
                            ui.input_text_area('text_instructions', 'Instructions', value='Create a outline for literature writing on the given topic', rows=8, width='100%', resize='vertical')
                    with ui.div(): 
                        ui.input_radio_buttons('radio_topic_selection', label='', choices=['Write topic', 'Upload topic'], inline=True, selected='Write topic')
                    with ui.div(class_='d-flex gap-4 align-items-end'):
                        @render.express
                        def renderTopicInputType():
                            topic_sel_type = input.radio_topic_selection()
                            if topic_sel_type == 'Write topic':
                                with ui.div(class_='col'):
                                    ui.input_text_area('text_topic', 'Topic', placeholder='Write a topic [with an optional primer]', rows=4, width='100%', resize='vertical')
                                with ui.div(class_='col-auto'):
                                    ui.input_task_button('btn_create_outline', 'Create outline')
                            else:
                                with ui.div(class_='d-flex gap-4 align-items-end'):
                                    ui.input_file("btn_upload_topic", "Choose a document (in text format) on a topic", accept=[".txt"])
                                with ui.div(class_='col-auto pb-3'):
                                    ui.input_task_button('btn_create_outline', 'Create outline')
                        
                with ui.div(class_='outline-creator-content'):
                    @render.express
                    @print_func_name
                    def renderOutline():
                        outline_content.get()
                                
    @reactive.effect
    @reactive.event(input.btn_upload_topic)
    @print_func_name
    def uploadTopic():

        files: list[FileInfo] | None = input.btn_upload_topic()
        text = ''
        for file in files:
            with open(file['datapath'], 'r') as fp:
                text += fp.read() + '\n\n'

        topic_desc.set(text)

    @reactive.effect
    @reactive.event(input.text_topic)
    @print_func_name
    def writeTopic():
        topic_desc.set(input.text_topic())
    
    @reactive.effect
    @reactive.event(input.btn_use_custom_outline)
    @print_func_name
    def useCustomOutline():
        outline_creator_options.set({'show': False, 'show_init_view': False})

    @reactive.effect
    @reactive.event(input.btn_show_create_outline_ai)
    @print_func_name
    def showCreateOutlineView():
        show_create_outline_view.set(True)

    @ui.bind_task_button(button_id="btn_create_outline")
    @reactive.extended_task
    @print_func_name
    async def generateOutline(agent, topic):
        response = await agent.ainvoke({'topic': topic}, {"configurable": {"thread_id": "abc123"}})
        response = response['content']
        print(response)
        return response
    
    @reactive.effect
    @reactive.event(input.btn_create_outline)
    @print_func_name
    def createOutline():
        if not topic_desc.get():
            if input.radio_topic_selection() == 'Write topic':
                ui.notification_show('Please provide a topic', type='error')
            else:
                ui.notification_show('Please provide a topic document', type='error')
            return
        
        llm = input.select_llm()
        temperature = input.slide_temp()
        instructions = input.text_instructions()

        agent = ArchitectureOutline(llm, temperature=temperature, instructions=instructions).agent

        generateOutline(agent, topic_desc.get())

    @reactive.effect
    @print_func_name
    def setContent():
        match generateOutline.status():
            case 'running':
                outline_content.set("Creating outline...")
            case 'error':
                outline_content.set("Error in creating outline.")
                print(generateOutline.result())
            case 'success':
                response = generateOutline.result()
                content = core_ui.div(
                        mod_outline_manager(getUIID('outline_manager'), outline=response, saved_outline=outline_from_outline_manager, close_fn=clearContent),
                        class_='border rounded flex-rest'
                    )
                outline_content.set(content)

    @print_func_name
    def clearContent():
        outline_content.set('Outline will appear here')

    @reactive.effect
    @reactive.event(outline_from_outline_manager, ignore_init=True)
    @print_func_name
    def saveOutlineForContentGeneration():
        saved_outline.set(outline_from_outline_manager.get())
        outline_creator_options.set({'show': False, 'show_init_view': False})