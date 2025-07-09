from shiny import reactive
from shiny.express import ui, render, module
import faicons
from utils import Config, getUIID, print_func_name
from ..backend.db import insertIntoDB, updateDB, selectFromDB, \
                generated_files_status, \
                generated_files_ai_architecture
from .manage_outline import processOutline, createRawOutline, mod_outline_manager, mod_ai_outline_creator
from .sidebar_modules.sidebar import mod_sidebar
from .common import initProfile, getFileType, getFileTypeIcon, getVectorDBFiles, detachDocs, getDocContent
import asyncio
import json
import textwrap
import re
from datetime import datetime
from rich import print

@module
def mod_main(input, output, session, config_app, reload_main_view_flag, reload_generated_docs_view_flag, settings_changed_flag):
    
    file_change_flag = reactive.value(True)
    show_outline = reactive.value(True)
    reload_content_view_flag = reactive.value(True)
    reload_rag_and_ref_flag = reactive.value(True)
    references = reactive.value([])

    outline_from_outline_manager = reactive.value('')
    outline_creator_options = reactive.value({'show': False,
                                              'show_init_view': True
                                              })

    stream = ui.MarkdownStream("stream")

    with ui.div(class_='app-body-container'):
        with ui.card(id='ctx_menu', style='display: none; position: absolute; z-index: 10; width: 250px; height: 75px'):
            ui.input_action_button(id='btn_regenerate_text', label='Regenerate paragraph')
        with ui.layout_sidebar():
            with ui.sidebar(id='sidebar_docs', position="left", open='closed' if config_app.email == '' else 'open', bg="#f8f8f8", width=400):
                @render.express
                @print_func_name
                def renderSideBar():
                    mod_sidebar(id=getUIID('sidebar'), 
                                config_app=config_app, 
                                reload_rag_and_ref_flag=reload_rag_and_ref_flag, 
                                reload_content_view_flag=reload_content_view_flag, 
                                reload_generated_docs_view_flag=reload_generated_docs_view_flag)

            with ui.div(class_='app-body'):
                @render.express
                @print_func_name
                def renderView():
                    options = outline_creator_options.get()
                    if options['show']:
                        mod_ai_outline_creator(getUIID('ai_outline_creator'), outline_creator_options, saved_outline=outline_from_outline_manager, show_init_view=options['show_init_view'])
                        return
                    with ui.div(class_='row name-bar'):
                        with ui.div(class_='col file-name'):
                            ui.input_text('text_file_name', 'File Name', value=config_app.file_name),
                            ui.input_action_button('btn_save_file_name', 'Save')
                            with ui.tooltip(placement="top"):
                                ui.input_action_button('btn_new_file', '', icon=faicons.icon_svg("plus"))
                                "New File"
                    with ui.div(class_='row input'):
                        class_name_outline, class_name_controls = ('col', 'row flex-column gap-2') if show_outline.get() else ('col d-none', 'row flex-row gap-2')
                        with ui.div(class_=class_name_outline):
                            with ui.div(class_='row justify-content-between', style='font-size: 0.8em !important'):
                                with ui.div(class_='col-2'):
                                    ui.input_checkbox('chk_use_example', 'Use example', value=False)
                                with ui.div(class_='col'):
                                    @render.express
                                    @print_func_name
                                    def renderManageOutline():
                                        if not input.text_outline().strip():
                                            ui.input_action_button('btn_open_outline_creator', 'Create outline with AI')
                                            return
                    
                                        with ui.popover(placement='bottom', options={'trigger': 'focus'}):
                                            ui.input_action_button('btn_manage_outline', 'Manage outline')
                                            with ui.div(class_='d-flex flex-column gap-2'):
                                                ui.input_action_button('btn_open_outline_manager', 'Manage outline in outline manager')
                                                ui.input_action_button('btn_open_outline_creator', 'Create outline with AI')
                                            
                                with ui.div(class_='d-flex flex-column col text-center'):
                                    @render.ui
                                    @print_func_name
                                    def renderLLMandTemp():
                                        _ = reload_content_view_flag(), settings_changed_flag()
                                        return [ui.span(f'LLM: {config_app.llm}, Temperature: {config_app.temperature}'),
                                                ui.span('(Can be changed in the settings panel in the top-right corner)')]
                                with ui.div(class_='col text-end'):
                                    ui.p("(Drag the text area from the bottom right corner to show more text)")
                            ui.input_text_area(id='text_outline', label='', placeholder='''Write an outline...''', rows=8, width='100%')
                        with ui.div(class_='col-auto d-flex justify-content-around align-items-end p-3'):
                            with ui.div(class_=class_name_controls):
                                @render.express
                                @print_func_name
                                def renderOutlineControl():
                                    text, ico = ('Hide outline', 'eye-slash') if show_outline.get() else ('Show outline', 'eye')
                                    with ui.tooltip(placement="right"):
                                        ui.input_action_button('btn_show_hide_outline', '', icon=faicons.icon_svg(ico))
                                        text 
                                with ui.tooltip(placement="right"):
                                    ui.input_action_button('btn_regenerate', '', icon=faicons.icon_svg("repeat"))
                                    "Write from the start"
                                with ui.tooltip(placement="right"):
                                    ui.input_action_button('btn_resume_pause', '', icon=faicons.icon_svg("play"))
                                    "Resume / Pause"
                                with ui.tooltip(placement="right"):
                                    ui.input_action_button('btn_speed', '', icon=faicons.icon_svg("person-running"))
                                    "Writing Speed"

                                @render.express
                                def renderDownloadOption():
                                    _ = reload_content_view_flag()
                                    outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'
                                    if not outline_file_path.exists(): return
                                    with ui.tooltip(placement="right"):
                                        @render.download(label=faicons.icon_svg("download"), filename='manuscript.md')
                                        @print_func_name
                                        async def renderDownloadDoc():
                                            attached_files = applyGetVectorDBFiles()
                                            content = getDocContent(file_id=config_app.generated_files_id, attached_files=attached_files)
                                            if content is None: return
                                            yield content
                                        "Download"
                                
                    with ui.div(class_='content-container'):
                        with ui.div(class_='content-header'):
                            ui.span('Content starts below ...')

                            @render.express
                            @print_func_name
                            def renderRAGAndRefInfo():
                                files = applyGetVectorDBFiles()
                                
                                if not files: return
                
                                with ui.popover(placement='bottom', options={'trigger': 'focus'}):
                                    ui.input_action_link('dummy', 'Using context from attached documents', class_='text-link')
                                    with ui.div(class_='d-flex flex-column gap-2'):
                                        with ui.div():
                                            for i, (_, file_name) in enumerate(files):
                                                with ui.div(class_='d-flex gap-1'):
                                                    with ui.div(class_='col-2 d-flex align-items-center'):
                                                        getFileTypeIcon(f'icon_{i}', file_type=getFileType(file_name))
                                                    with ui.div(class_='col d-flex align-items-center'):
                                                        with ui.tooltip():
                                                            ui.span(file_name, class_='cut-text')
                                                            file_name
                                        with ui.div(class_='text-end'):
                                            with ui.tooltip():
                                                ui.input_action_link(f'btn_delete_rag', '', icon=faicons.icon_svg('trash'))
                                                "De-attach documents"
                                        
                        
                        with ui.div(class_='content outline', id='content'):
                            stream.ui(width='100%')
                            @render.express
                            @print_func_name
                            def renderReferences():
                                refs = references.get()
                                if not refs: return
                                with ui.div(class_='mt-4'):
                                    ui.h2('References')
                                    with ui.div(class_='d-flex flex-column gap-1 ms-3'):
                                        for i, ref in enumerate(refs):
                                            ui.span(f'{i+1}. {ref}')

    ui.include_js(Config.DIR_HOME / "www" / "js" / "addon.js")

    @reactive.effect
    @reactive.event(input.btn_new_file)
    @print_func_name
    def showNewFile():
        config_app.file_name = ''
        config_app.generated_files_id = None
        config_app.vector_db_collections_id = None
        initProfile(config_app)

        reload_main_view_flag.set(not reload_main_view_flag.get())

    @reactive.effect
    @reactive.event(input.btn_save_file_name)
    @print_func_name
    def saveFileName():
        file_name = input.text_file_name()

        if config_app.file_name == file_name: return

        valid_file_statuses = list({e.value for e in generated_files_status} - {generated_files_status.DELETED.value})
        if config_app.email != '':
            records = selectFromDB('generated_files', 
                                field_names=['email', 'file_name', 'status'], 
                                field_values=[[config_app.email], [file_name], valid_file_statuses])
        else:
            records = selectFromDB('generated_files', 
                                field_names=['session', 'file_name', 'status'], 
                                field_values=[[config_app.session], [file_name], valid_file_statuses])
        
        if not records.empty:
            ui.notification_show('File name already exists.', type='error')
            return 
        
        current_time = datetime.now()

        if config_app.generated_files_id:
            
            updateDB(table_name='generated_files',
                    update_fields=['file_name', 'update_date'],
                    update_values=[file_name, current_time],
                    select_fields=['id'],
                    select_values=[[config_app.generated_files_id]])
            
            config_app.file_name = file_name

        else:
            ids = insertIntoDB(table_name='generated_files', 
                        field_names=['email', 'session', 'settings_id', 'ai_architecture', 'file_name', 'status', 'create_date', 'update_date'], 
                        field_values=[[config_app.email], [config_app.session_id], [config_app.settings_id], [generated_files_ai_architecture.BASE.value], [file_name], 
                                    'created', [current_time], [current_time]])
            
            config_app.generated_files_id = ids[0]
            config_app.file_name = file_name

            outline_file_path = f'data/outline_{config_app.generated_files_id}.json'

            with open(outline_file_path, 'w') as fp:
                json.dump({}, fp)
            
            settings_changed_flag.set(not settings_changed_flag.get())

        reload_generated_docs_view_flag.set(not reload_generated_docs_view_flag.get())
        
        ui.notification_show('File name saved.', type='message')

    @reactive.effect
    @reactive.event(input.btn_open_outline_manager)
    @print_func_name
    def openOutlineManager():

        outline = input.text_outline().strip()
        if outline == '': return False

        outline_manager_view = mod_outline_manager(getUIID('outline_manager'), 
                                                   outline=outline, 
                                                   saved_outline=outline_from_outline_manager,
                                                   close_fn=ui.modal_remove)

        m = ui.modal(
            outline_manager_view,
            title="",
            easy_close=False,
            footer=None,
            size='xl',
            style='height: 90vh'
        )

        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.btn_open_outline_creator)
    @print_func_name
    def openOutlineCreator():
        outline_creator_options.set({'show': True, 'show_init_view': False})

    @print_func_name
    def setContent(content):
        loop = asyncio.get_event_loop()
        loop.create_task(stream._send_content_message(content, "replace", []))

    @reactive.effect
    @reactive.event(settings_changed_flag)
    @print_func_name
    def initContentView():
        # Reset content
        setContent('')
        references.set([])
        config_app.vector_db_collections_id = None
        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())
        
    @reactive.calc
    @reactive.event(reload_rag_and_ref_flag)
    @print_func_name
    def applyGetVectorDBFiles():
        
        return getVectorDBFiles(config_app.vector_db_collections_id)
    
    @reactive.effect
    @reactive.event(input.btn_delete_rag)
    @print_func_name
    def applyDetachDocs():

        detachDocs(config_app.generated_files_id, config_app.vector_db_collections_id)

        config_app.vector_db_collections_id = None

        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())

    @reactive.effect
    @reactive.event(reload_main_view_flag)
    @print_func_name
    def reloadMainView():

        outline_creator_options.set({'show': True, 'show_init_view': True})
        file_change_flag.set(not file_change_flag.get())
        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())
        
    @reactive.effect
    @reactive.event(reload_content_view_flag, ignore_init=True)
    @print_func_name
    def reloadContentView():

        outline_creator_options.set({'show': False, 'show_init_view': False})
        file_change_flag.set(not file_change_flag.get())
        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())
        
    @reactive.effect
    @reactive.event(file_change_flag, ignore_init=True)
    @print_func_name
    def showContent():

        if not config_app.file_name: 
            # Reset file name, outline and content
            ui.update_checkbox(id='chk_use_example', value=False)
            ui.update_text(id='text_file_name', value='')
            ui.update_text_area(id='text_outline', value='')
            setContent('')
            references.set([])
            return
        
        outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'
        
        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        raw_outline = '\n'.join(createRawOutline(d_outline))
        
        # Cancel writing
        stream.latest_stream.cancel()

        # Show file name, outline and content
        ui.update_text(id='text_file_name', value=config_app.file_name)
        ui.update_text_area(id='text_outline', value=raw_outline)

        attached_files = applyGetVectorDBFiles()
        references.set([])
        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, 
                                                        outline_file_path, 
                                                        write_n_contents=0, 
                                                        attached_files=attached_files), 
                                        clear=True))
        
    @reactive.effect
    @reactive.event(input.btn_show_hide_outline)
    @print_func_name
    def showOrHideOutline():
        show_outline.set(not show_outline.get())

        if not config_app.file_name: return
        
        outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'

        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        raw_outline = '\n'.join(createRawOutline(d_outline))
        ui.update_text_area(id='text_outline', value=raw_outline)

    @print_func_name
    def resetContentPara(d_outline, section_list, paragraph_index):
        '''
        Resets specified paragraph for regeneration within a section hierarchy
        '''
        
        if len(section_list) == 1:
            
            assert 'content' in d_outline[section_list[0]], 'Hierarchy does not contain content'

            count_par = 0

            for i, (_, content) in enumerate(d_outline[section_list[0]]['content']):
                
                # Detect the specified paragraph 
                count_par += content.count('\n\n') + 1
                if paragraph_index < count_par:
                    break
            
            assert i < len(d_outline[section_list[0]]['content']), 'Intended paragraph was not found for regeneration'
        
            # Reset the specified paragraph in the outline
            pars = content.split('\n\n')
            index_current_par = len(pars)-(count_par - paragraph_index)
            previous_para_current_content, next_para_current_content = [], []
            if index_current_par > 0:
                previous_para_current_content = [[d_outline[section_list[0]]['content'][i][0], '\n\n'.join(pars[:index_current_par])]]
            if index_current_par < len(pars)-1:
                next_para_current_content = [[d_outline[section_list[0]]['content'][i][0], '\n\n'.join(pars[index_current_par+1:])]]

            d_outline[section_list[0]]['content'] = (d_outline[section_list[0]]['content'][:i]
                                                    + previous_para_current_content
                                                    + [['content_ai', '']]
                                                    + next_para_current_content
                                                    + d_outline[section_list[0]]['content'][i+1:])
        else:
            resetContentPara(d_outline[section_list[0]], section_list[1:], paragraph_index)

    @reactive.effect
    @reactive.event(input.btn_regenerate_text)
    @print_func_name
    def regenerateParagraph():

        hierarchy = input.selected_para_hierarchy()
        if not hierarchy: return
        
        outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'
        
        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)
        
        *section_list, paragraph_index = hierarchy
        
        resetContentPara(d_outline, section_list, paragraph_index)

        attached_files = applyGetVectorDBFiles()
        references.set([])
        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, 
                                                        outline_file_path,
                                                        write_n_contents=1,
                                                        attached_files=attached_files), 
                                        clear=True))

    @reactive.effect
    @reactive.event(input.chk_use_example, ignore_init=True)
    @print_func_name
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
        
        if not input.chk_use_example(): example = ''

        ui.update_text_area('text_outline', value=example)

    @reactive.effect
    @reactive.event(outline_from_outline_manager, ignore_init=True)
    @print_func_name
    def saveOutlineFromOutlineManager():
        ui.update_text('text_outline', value=outline_from_outline_manager.get())

    @print_func_name
    def saveOutline(regenerate=False):

        records = selectFromDB('generated_files', 
                            field_names=['id', 'file_name'], 
                            field_values=[[config_app.generated_files_id], [config_app.file_name]])
        
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

        with open(f'data/outline_{config_app.generated_files_id}.json', 'w') as fp:
            json.dump(d_outline, fp)

        current_time = datetime.now()
        
        updateDB('generated_files', 
                    update_fields=['status', 'create_date', 'update_date'], 
                    update_values=[generated_files_status.CREATED.value, current_time, current_time], 
                    select_fields=['id'], 
                    select_values=[[config_app.generated_files_id]])

        return True

    @print_func_name
    async def generateResponse(d_outline, outline_file_path, write_n_contents=-1, attached_files=[]):

        @print_func_name
        def getHierarchy(d_outline, content_pre=[], current_section_list=[], counter=1):
            '''
            Get all previous content and current section hierarchy up to the point that needs ai generation
            '''

            is_gen_needed = False
            for k in d_outline:
                if k == 'References': continue
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
        
        @print_func_name
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
        
        @print_func_name
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

        @print_func_name
        def insertReferences(d_outline, ref_list):

            top_level_key = list(d_outline.keys())[0]
            d_outline[top_level_key]['References'] = [('ref', f'{i+1}. {v}') for i, v in enumerate(ref_list)]

        @print_func_name
        def processCitation(content, ref_list):

            d_files = {str(k): v for k, v in attached_files}

            refs = re.findall(r'\[CITE\((\d+?)\)\]', content)
            
            d_ref = {}
            for ref in refs:
                if ref not in d_files: continue
                try:
                    d_ref[ref] = ref_list.index(d_files[ref]) + 1
                except ValueError:
                    ref_list.append(d_files[ref])
                    d_ref[ref] = len(ref_list)
            
            for ref, ref_index in d_ref.items():
                content = content.replace(f'CITE({ref})', f'<a href="#:~:text=References">{ref_index}</a>')

            return content, ref_list
        
        @print_func_name
        async def dummy(i=None):
            await asyncio.sleep(3)
            if i is None:
                return 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse id erat lectus. Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis, lobortis justo sit amet, blandit libero. Suspendisse hendrerit sapien sit amet augue aliquam, at auctor purus mattis. In sed volutpat elit, et vehicula urna. Mauris libero lectus, dignissim quis facilisis aliquam, facilisis et tortor. Proin finibus lacus lectus, nec sodales ex vulputate in. Integer congue condimentum tempus. Ut ut elit in tellus viverra ornare at at nisl. Nam tincidunt vulputate pretium. Morbi purus purus, convallis in fringilla in, rhoncus a nisi. Curabitur eu pretium ligula. Vestibulum ullamcorper elit sit amet feugiat rutrum. Aenean tempor massa risus, non pulvinar justo scelerisque et. Maecenas non aliquet risus. Maecenas ac sem ut lorem commodo tempus.\nDonec eleifend tristique erat, sit amet sodales arcu ullamcorper eu. Aliquam non dapibus mi. Donec pretium risus ipsum, eu porttitor lectus porta in. Nulla facilisi. Proin rhoncus lectus nulla, non egestas sapien suscipit non. Maecenas bibendum semper cursus. Praesent in velit ut tellus tincidunt cursus laoreet et dolor. Morbi maximus maximus nunc nec luctus. Aenean ut sapien euismod, lacinia justo id, vestibulum ipsum.'
            if i % 2:
                return 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse id erat lectus [CITE(27)].'
            else:
                return 'Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis, lobortis justo sit amet, blandit libero. Suspendisse hendrerit sapien sit amet augue aliquam, at auctor purus mattis [CITE(28)].'

        len_last_content_pre, content_pre_new = 0, None

        ref_list = []

        while True:

            content_pre, current_section_list, is_gen_needed = getHierarchy(d_outline)
            
            current_section = getSectionText(current_section_list)

            if content_pre_new is None:
                content_pre_new = content_pre
            else:
                content_pre_new = content_pre[len_last_content_pre + 1:]

            content_pre_new = '\n\n'.join(content_pre_new) + '\n\n'
            
            if attached_files:
                content_pre_new, ref_list = processCitation(content_pre_new, ref_list)
                references.set(ref_list.copy())
                await reactive.flush()

            len_last_content_pre = len(content_pre)
            
            yield content_pre_new

            if write_n_contents == 0 or not is_gen_needed: break
        
            # if attached_files:
            #     response = await dummy(len(ref_list))  
            # else:
            #     response = await dummy()
            response = await config_app.agent.ainvoke({'content_pre': '\n\n'.join(content_pre), 'current_section': current_section}, {"configurable": {"thread_id": "abc123"}})
            response = response['response']

            print(response)

            insertContent(d_outline, current_section_list, response)

            if attached_files:
                response_with_citations, ref_list = processCitation(response, ref_list)
                references.set(ref_list.copy())
                await reactive.flush()
                insertReferences(d_outline, ref_list)
                tokens = response_with_citations.split(' ')
            else:
                tokens = response.split(' ')

            for i, s in enumerate(tokens):
                await asyncio.sleep(0.1 if not config_app.write_faster else 0.01)
                yield s + ' ' if i < len(tokens)-1 else s + '\n\n'
            
            with open(outline_file_path, 'w') as fp:
                json.dump(d_outline, fp)

            ui.notification_show("Progress saved", type="message")

            current_time = datetime.now()

            updateDB('generated_files', 
                        update_fields=['status', 'update_date'], 
                        update_values=[generated_files_status.RUNNING.value, current_time], 
                        select_fields=['id'], 
                        select_values=[[config_app.generated_files_id]])
            
            if write_n_contents > 0: write_n_contents -= 1

    @print_func_name
    async def generate(regenerate):

        if config_app.file_name == '':
            ui.notification_show("Please save a file name.", type="error")
            return

        if not saveOutline(regenerate=regenerate): 
            ui.notification_show("Please provide an outline.", type="error")
            return

        outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'
        
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        references.set([])

        attached_files = applyGetVectorDBFiles()
        await stream.stream(generateResponse(d_outline, 
                                             outline_file_path,
                                             attached_files=attached_files), 
                            clear=True)

        config_app.is_writing = True

    @reactive.effect
    @reactive.event(input.btn_resume_pause)
    @print_func_name
    async def resumeOrPause():

        if config_app.is_writing: 
            stream.latest_stream.cancel()
            return
        
        await generate(regenerate=False)

    @reactive.effect
    @reactive.event(input.btn_regenerate)
    @print_func_name
    async def startFromBeginning():
        await generate(regenerate=True)

    @reactive.effect
    @print_func_name
    def checkWritingStatus():

        stream_status = stream.latest_stream.status()

        if stream_status in ["success", "error", "cancelled"]:

            if config_app.is_writing:

                current_time = datetime.now()
                updateDB('generated_files', 
                            update_fields=['status', 'update_date'], 
                            update_values=[stream_status, current_time], 
                            select_fields=['id'], 
                            select_values=[[config_app.generated_files_id]])
                
                reload_generated_docs_view_flag.set(not reload_generated_docs_view_flag.get())
                
                if stream_status == "success":
                    ui.notification_show("Writing finished", type="message")
                else:
                    ui.notification_show("Writing stopped", type="warning")


            config_app.is_writing = False

            ui.update_action_button("btn_resume_pause", icon=faicons.icon_svg("play"))
        else:
            ui.update_action_button("btn_resume_pause", icon=faicons.icon_svg("pause"))


    @reactive.effect
    @reactive.event(input.btn_speed)
    @print_func_name
    def speed():
        config_app.write_faster = not config_app.write_faster
        ui.update_action_button(
            "btn_speed", icon=faicons.icon_svg("person-walking" if config_app.write_faster else "person-running")
        )