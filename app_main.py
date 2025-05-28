from shiny import reactive, ui as core_ui, render as core_render
from shiny.express import ui, render, session, module
import faicons
from pathlib import Path
from db import updateDB, selectFromDB, insertIntoDB
import asyncio
import json
import textwrap
from datetime import datetime

@module
def mod_main(input, output, session, config_app, updateFileNameFlag, state_change_flag):

    print('Email:', config_app.email)
    
    file_change_flag = reactive.value(True)

    stream = ui.MarkdownStream("stream")

    @module
    def getDocListItem(input, output, session, row, setCurrentFile):

        @reactive.effect
        @reactive.event(input.btn_show, ignore_init=True)
        def showFile():
            setCurrentFile(row['session'], row['file_name'])

        @core_render.download(filename='manuscript.md')
        async def downloadDoc():

            file_name_part = row['file_name'].lower().replace(' ', '_')
            doc_path = Path(f'data/manuscript_{row['session']}_{file_name_part}.md')

            if not doc_path.exists(): return
            with open(doc_path) as f:
                for l in f.readlines():
                    yield l

        return core_ui.div(
                    core_ui.div(
                        ui.input_action_link('btn_show', row["file_name"]),
                        core_ui.span(str(row['update_date'])),
                        class_='d-flex flex-column'
                    ),
                    core_ui.div(
                        core_ui.download_button('downloadDoc', '', icon=faicons.icon_svg("download")),
                        class_='icon'
                    ),
                    class_='d-flex gap-2'
                )

    with ui.hold() as content:
        with ui.div(class_='app-body-container'):
            with ui.layout_sidebar():
                with ui.sidebar(id='sidebar_docs', position="left", open='closed' if config_app.email == '' else 'open', bg="#f8f8f8"):
                    with ui.div(class_='side-bar-docs-container'):  
                        @render.ui
                        def showDocuments():
                            records = loadDocuments()
                            if records.empty: return ui.span('No saved documents')
                            ui_elements = []
                            for i, row in records.iterrows():
                                ui_elements.append(
                                    getDocListItem(f'doc_list_item_{i}', row, setCurrentFile)
                                )
                            return ui_elements
                with ui.div(class_='app-body'):
                    with ui.div(class_='row input'):
                        with ui.div(class_='col'):
                            with ui.div(class_='row justify-content-between', style='font-size: 0.8em !important'):
                                with ui.div(class_='col-4'):
                                    ui.input_checkbox('chk_example', 'Use example', value=False)
                                with ui.div(class_='d-flex flex-column col-4 text-center'):
                                    @render.ui
                                    def showLLMandTemp():
                                        llm, temp = getLLMandTemp()
                                        return [ui.span(f'LLM: {llm}, Temperature: {temp}'),
                                                ui.span('(Can be changed in the settings panel in the top-right corner)')]
                                with ui.div(class_='col-4 text-end'):
                                    ui.p("(Drag the text area from the bottom right corner to show more text)")
                            ui.input_text_area('text_outline', '', placeholder='''Write an outline...''', rows=7, width='100%')
                        with ui.div(class_='col-auto d-flex justify-content-around align-items-end p-3'):
                            with ui.div(class_='row flex-column gap-2'):
                                with ui.tooltip(placement="right"):
                                    ui.input_action_button('btn_regenerate', '', icon=faicons.icon_svg("repeat"))
                                    "Write from the start"
                                with ui.tooltip(placement="right"):
                                    ui.input_action_button('btn_resume_pause', '', icon=faicons.icon_svg("play"))
                                    "Resume / Pause"
                                with ui.tooltip(placement="right"):
                                    ui.input_action_button('btn_speed', '', icon=faicons.icon_svg("person-running"))
                                    "Writing Speed"
                                with ui.tooltip(placement="right"):
                                    @render.download(label=faicons.icon_svg("download"), filename='manuscript.md')
                                    async def downloadDoc():

                                        file_name_part = config_app.file_name.lower().replace(' ', '_')
                                        doc_path = Path(f'data/manuscript_{config_app.session_id}_{file_name_part}.md')

                                        if not doc_path.exists(): return
                                        with open(doc_path) as f:
                                            for l in f.readlines():
                                                yield l
                                    "Download"
                                
                    with ui.div(class_='row content'):
                        stream.ui(content=core_ui.p('Content starts here ...', class_='mt-3'), width='100%') 

    def setContent(content):
        loop = asyncio.get_event_loop()
        loop.create_task(stream._send_content_message(content, "replace", []))

    def clearContent():
        setContent('')

    @reactive.calc()
    def getLLMandTemp():
        return config_app.llm, config_app.temperature

    @reactive.calc()
    @reactive.event(state_change_flag)
    def isLoggedIn():
        return config_app.email != ''

    @reactive.calc()
    @reactive.event(state_change_flag)
    def loadDocuments():
        print(f'In loadDocuments: {config_app.email=}')
        if config_app.email != '':
            records = selectFromDB(table_name='sessions', field_names=['email'], field_values=[[config_app.email]])
        else:
            records = selectFromDB(table_name='sessions', field_names=['session'], field_values=[[config_app.session_id]])
        return records

    @reactive.effect
    @reactive.event(input.chk_example)
    def useExample():
        
        example = textwrap.dedent('''\
        # Title: Hypertensive Disorders of Pregnancy: A Comprehensive Review of Pathophysiology, Clinical Management, Long-Term Implications, and Future Directions
        ## I. Introduction
        <content>
        ### A. Historical Perspective and Evolution of Understanding
        <content>
        ### B. Definition and Significance of Hypertensive Disorders of Pregnancy (HDP)
        #### 1. Global Burden of Disease (Maternal and Perinatal Morbidity & Mortality)
        <content>
        #### 2. Economic Impact
        <content>
        ### C. Classification of HDP (Overview based on major international guidelines - e.g., ACOG, ISSHP, WHO)
        #### 1. Chronic Hypertension (Pre-existing)
        <content>
        #### 2. Gestational Hypertension
        <content>
        #### 3. Preeclampsia
        <content>''')
        
        if not input.chk_example(): example = ''

        ui.update_text_area('text_outline', value=example)

    def createRawOutline(d, raw_outline=[], counter=1):

        if not isinstance(d, dict):
            for k, v in d:
                if k == 'content_ai':
                    raw_outline.append('<content>')
                else:
                    raw_outline.append(v)
        else:
            for k in d:
                raw_outline = createRawOutline(d[k], raw_outline + [f'{'#' * counter} {k}'] if k != 'content' else raw_outline, counter+1)

        return raw_outline

    def setCurrentFile(session_id, file_name):

        config_app.session_id = session_id
        config_app.file_name = file_name
        file_change_flag.set(not file_change_flag.get())
        
    @reactive.effect
    @reactive.event(file_change_flag, ignore_init=True)
    def showFile():

        records = selectFromDB('sessions', 
                            field_names=['session', 'file_name'], 
                            field_values=[[config_app.session_id], [config_app.file_name]])

        if records.empty:
            return
        
        file_name_part = config_app.file_name.lower().replace(' ', '_')
        outline_file_path = Path(f'data/outline_{config_app.session_id}_{file_name_part}.json')
        manuscript_file_path = Path(f'data/manuscript_{config_app.session_id}_{file_name_part}.md')

        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        raw_outline = '\n'.join(createRawOutline(d_outline))

        # Read manuscript
        if manuscript_file_path.exists():
            with open(manuscript_file_path) as fp:
                content = fp.read()
        else:
            content = ''
        
        # Change config
        config_app.is_writing = False

        # Show file name, outline and content
        updateFileNameFlag(config_app.file_name)
        ui.update_text(id='text_outline', value=raw_outline)
        setContent(content)

    def saveOutline(regenerate=False):

        def insertOutline(d, outline_items):

            if len(outline_items) == 1:
                d['content'] = d.get('content', []) + outline_items
                return d
            
            if outline_items[0] not in d:
                d[outline_items[0]] = {}
            
            d[outline_items[0]] = insertOutline(d[outline_items[0]].copy(), outline_items[1:])

            return d
        
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

        records = selectFromDB('sessions', 
                            field_names=['session', 'file_name'], 
                            field_values=[[config_app.session_id], [config_app.file_name]])
        
        if not (records.empty or regenerate): return True

        outline = input.text_outline().strip()
        if outline == '': return False

        # outline ='''
        # # Title: Neuroinflammation and Cognitive Function: Interplay of Causes, Mechanisms, and Pathological Outcomes
        # ##  Abstract
        # Neuroinflammation—once considered a secondary epiphenomenon of central nervous system (CNS) injury—is now recognized as an active, multifaceted driver of cognitive dysfunction across a broad spectrum of neurological and psychiatric disorders.
        # ## I. Introduction
        # continue writing
        # ### A. Defining Neuroinflammation: Beyond a simple response – complex cellular and molecular interactions <content>
        # ### B. Defining Cognitive Function: Key domains affected (memory, attention, executive function, processing speed) 
        # continue writing
        # <content>
        # continue writing
        # ### C. Historical Perspective vs. Current Understanding: Evolution of the concept of brain immunity and inflammation 
        # continue writing.
        # <content>
        # continue writing..
        # <content>
        # continue writing...
        # '''
        
        d_outline = processOutline(outline)

        file_name_part = config_app.file_name.lower().replace(' ', '_')

        with open(f'data/outline_{config_app.session_id}_{file_name_part}.json', 'w') as fp:
            json.dump(d_outline, fp)

        with open(f'data/instructions_{config_app.session_id}_{file_name_part}.txt', 'w') as fp:
            fp.write(config_app.instructions)

        current_time = datetime.now()
        
        # File does not exist, first time generation
        if records.empty:
            insertIntoDB('sessions', 
                        field_names=['email', 'session', 'file_name', 'file_status', 'create_date', 'update_date', 'llm', 'temperature'], 
                        field_values=[[config_app.email], [config_app.session_id], [config_app.file_name], 'created', [current_time], [current_time], [config_app.llm], [config_app.temperature]])
        # File exists but regenerating
        else:
            updateDB('sessions', 
                        update_fields=['file_status', 'create_date', 'update_date'], 
                        update_values=['created', current_time, current_time], 
                        select_fields=['email', 'session', 'file_name'], 
                        select_values=[[config_app.email], [config_app.session_id], [config_app.file_name]])

        return True

    async def generateResponse(d_outline, outline_file_path, manuscript_file_path):

        def getHierarchy(d_outline, content_pre=[], current_section_list=[], counter=1):
            '''
            Get all previous content and current section hierarchy up to the point that needs ai generation
            '''

            is_gen_needed = False
            for k in d_outline:

                if k != 'content':
                    content_pre, current_section_list, is_gen_needed = getHierarchy(d_outline[k], 
                                                                content_pre + [f'{'#' * counter} {k}'],
                                                                current_section_list + [k],
                                                                counter + 1)
                    if not is_gen_needed: current_section_list.pop()
                else:
                    content_list = []
                    for v in d_outline[k]:
                        # Record only the first content_ai tag and 
                        # all content_user tags after that
                        if v[0] == 'content_ai':
                            if is_gen_needed: break
                            if v[1] == '': 
                                is_gen_needed = True
                            else:
                                content_pre.append(v[1])
                            content_list.append(v)
                        elif v[0] == 'content_user':
                            content_list.append(v)
                            if is_gen_needed: break
                            content_pre.append(v[1])
                    
                    if is_gen_needed: current_section_list.append(content_list)      
                
                if is_gen_needed: break
                        
            return content_pre, current_section_list, is_gen_needed
        
        def getSectionText(section_list):
            '''
            Get current section hierarchy up to the point that needs ai generation in markdown format 
            '''

            section_text_lines = []
            for i, v in enumerate(section_list):
                if not isinstance(v, list):
                    section_text_lines.append(f'{'#' * (i+1)} {v}')
                else:
                    for content_type, content in v:
                        if content_type == 'content_user' or content != '':
                            section_text_lines.append(content)
                        else:
                            section_text_lines.append('<content>')
            
            return '\n\n'.join(section_text_lines)
        
        def insertContent(d_outline, section_list, response):
            '''
            Inserts the ai response to the appropriate position of the outline
            '''

            if not len(section_list): return
            
            if len(section_list) == 1:
                for i, (content_type, content) in enumerate(section_list[0]):
                    if content_type == 'content_ai' and content == '':
                        d_outline['content'][i][1] = response
                        return
            else:
                insertContent(d_outline[section_list[0]], section_list[1:], response)
            
        len_last_content_pre, section_header = 0, None

        while True:

            content_pre, current_section_list, is_gen_needed = getHierarchy(d_outline)
            
            current_section = getSectionText(current_section_list)

            if section_header is None:
                section_header = content_pre
            else:
                section_header = content_pre[len_last_content_pre + 1:]
            
            section_header = '\n\n'.join(section_header) + '\n\n'

            len_last_content_pre = len(content_pre)
            
            yield section_header

            if not is_gen_needed: break
        
            response = await config_app.agent.ainvoke({'content_pre': '\n\n'.join(content_pre), 'current_section': current_section}, {"configurable": {"thread_id": "abc123"}})
            
            response = response['response']
            #response = 'dummy ai'

            insertContent(d_outline, current_section_list, response)
            
            print(response)
            
            tokens = response.split(' ')

            for i, s in enumerate(tokens):
                await asyncio.sleep(0.1 if not config_app.write_faster else 0.01)
                yield s + ' ' if i < len(tokens)-1 else s + '\n\n'
            
            with open(outline_file_path, 'w') as fp:
                json.dump(d_outline, fp)

            with open(manuscript_file_path, 'w') as fp:
                fp.write('\n\n'.join(content_pre) + '\n\n' + response + '\n\n')
                ui.notification_show("Progress saved", type="message")

            current_time = datetime.now()

            updateDB('sessions', 
                        update_fields=['file_status', 'update_date'], 
                        update_values=['running', current_time], 
                        select_fields=['email', 'session', 'file_name'], 
                        select_values=[[config_app.email], [config_app.session_id], [config_app.file_name]])

    async def generate(regenerate):

        if config_app.file_name == '':
            ui.notification_show("Please save a file name.", type="error")
            return

        if not saveOutline(regenerate=regenerate): 
            ui.notification_show("Please provide an outline.", type="error")
            return

        file_name_part = config_app.file_name.lower().replace(' ', '_')
        outline_file_path = f'data/outline_{config_app.session_id}_{file_name_part}.json'
        manuscript_file_path = f'data/manuscript_{config_app.session_id}_{file_name_part}.md'

        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        await stream.stream(generateResponse(d_outline, outline_file_path, manuscript_file_path), clear=regenerate)

        state_change_flag.set(not state_change_flag.get())

    @reactive.effect
    @reactive.event(input.btn_resume_pause)
    async def resumeOrPause():

        if config_app.is_writing:
            stream.latest_stream.cancel()
            config_app.is_writing = False
            ui.notification_show("Writing stopped", type="warning")
            return
        
        config_app.is_writing = True
        
        await generate(regenerate=False)

    @reactive.effect
    @reactive.event(input.btn_regenerate)
    async def start():

        await generate(regenerate=True)

    @reactive.effect
    def _():
        stream_status = stream.latest_stream.status()

        ui.update_action_button(
            "btn_resume_pause", icon=faicons.icon_svg("play" if not config_app.is_writing else "pause")
        )

        if stream_status in ["success", "error", "cancelled"]:
            current_time = datetime.now()

            updateDB('sessions', 
                        update_fields=['file_status', 'update_date'], 
                        update_values=[stream_status, current_time], 
                        select_fields=['email', 'session', 'file_name'], 
                        select_values=[[config_app.email], [config_app.session_id], [config_app.file_name]])
            
            if stream_status == "success":
                ui.notification_show("Writing finished", type="message")

            ui.update_action_button(
                "btn_resume_pause", icon=faicons.icon_svg("play")
            )

    @reactive.effect
    @reactive.event(input.btn_speed)
    def speed():
        config_app.write_faster = not config_app.write_faster
        ui.update_action_button(
            "btn_speed", icon=faicons.icon_svg("person-walking" if config_app.write_faster else "person-running")
        )

    return content