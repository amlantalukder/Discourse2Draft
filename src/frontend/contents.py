from shiny import reactive
from shiny.express import ui, render, module
import faicons
from utils import Config, getUIID, print_func_name
from ..backend.db import insertIntoDB, updateDB, selectFromDB, \
                generated_files_status, \
                generated_files_ai_architecture, \
                vector_db_collections_type, \
                vector_db_collections_status
from .manage_outline import resetOutline, processOutline, generateOutlineByAI, processOutlineByAI, getRawOutline, mod_outline_manager, mod_ai_outline_creator
from .common import getFileType, getFileTypeIcon, getVectorDBFiles, detachDocs, getDocContent, createVectorDBCollection, getLiteraturesFromDB, formatCitations
from .defaults import ContentGenerationScope, SpecialSectionTypes, ContentTypes
import asyncio
import json
import textwrap
import re
from datetime import datetime
import io
import logging

@module
def mod_contents(input, output, session, 
                 config_app,
                 reload_view_flag,
                 reload_attached_files_view_flag,
                 reload_generated_docs_view_flag,
                 reload_uploaded_docs_view_flag,
                 ui_id):

    show_outline = reactive.value(True)
    references = reactive.value([])

    outline_from_outline_manager = reactive.value('')
    write_abstract_flag = reactive.value(True)
    
    stream = ui.MarkdownStream("stream")

    with ui.hold() as content:
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
                with ui.div(class_='row justify-content-between align-items-center pt-2 pb-2', style='font-size: 0.8em !important'):            
                    with ui.div(class_='col'):
                        ''
                    with ui.div(class_='d-flex flex-column col text-center'):
                        @render.express
                        @print_func_name
                        def renderLLMandTemp():
                            _ = reload_view_flag.get()
                            ui.span(f'LLM: {config_app.llm}, Temperature: {config_app.temperature}')
                            ui.span('(Can be changed in the settings panel in the top-right corner)')
                    with ui.div(class_='col text-end'):
                        @render.express
                        @print_func_name
                        def renderManageOutline():
                            btn_label = ('Create' if not input.text_outline().strip() else 'Manage') + ' outline with AI'
                            ui.input_action_button('btn_open_outline_manager', btn_label)
                            
                with ui.navset_underline(id="user_input_panel", selected="Query"):
                    with ui.nav_panel("Query"):
                        ui.input_text_area(id='text_query', label='', placeholder='''Write an query...''', rows=8, width='100%')
                    with ui.nav_panel("Structured Outline"):
                        with ui.div(class_='col mt-2'):
                            ui.input_checkbox('chk_use_example', 'Use example', value=False)
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
                    @render.express
                    @print_func_name
                    def renderDownloadButton():
                        _ = reload_view_flag.get()
                        if not config_app.file_name: return
                        with ui.tooltip(placement="right"):
                            with ui.div():
                                with ui.popover(placement='bottom', options={'trigger': 'focus'}):
                                    ui.input_action_button('btn_download', '', icon=faicons.icon_svg("download"))
                                    with ui.div(class_='d-flex flex-column gap-2'):
                                        @render.express
                                        @print_func_name
                                        def renderDownloadOptions():
                                            attached_files, file_info = applyGetVectorDBFiles()
                                            outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'
                                            if not outline_file_path.exists(): return
                                            content_md, content_docx, content_tex, bibs = getDocContent(file_id=config_app.generated_files_id, attached_files=attached_files, file_info=file_info)

                                            @render.download(label=ui.div('Content (.md)', faicons.icon_svg("download"), class_='d-flex justify-content-between align-items-center gap-1'), filename=f'{config_app.file_name}.md')
                                            @print_func_name
                                            async def renderDownloadContentMD():
                                                yield content_md

                                            @render.download(label=ui.div('Content (.docx)', faicons.icon_svg("download"), class_='d-flex justify-content-between align-items-center gap-1'), filename=f'{config_app.file_name}.docx')
                                            @print_func_name
                                            async def renderDownloadContentDocx():
                                                docx_buffer = io.BytesIO()
                                                content_docx.save(docx_buffer)
                                                docx_buffer.seek(0)

                                                yield docx_buffer.read()

                                            @render.download(label=ui.div('Content (.tex)', faicons.icon_svg("download"), class_='d-flex justify-content-between align-items-center gap-1'), filename=f'{config_app.file_name}.tex')
                                            @print_func_name
                                            async def renderDownloadContentTex():
                                                yield content_tex
                                                    
                                            if bibs:
                                                @render.download(label=ui.div('Bibliography', faicons.icon_svg("download"), class_='d-flex justify-content-between align-items-center gap-1'), filename=f'{config_app.file_name}.bib')
                                                @print_func_name
                                                async def renderDownloadBib():
                                                    yield bibs
                            "Download"
                    
        with ui.div(class_='content-container'):
            with ui.div(class_='content-header'):
                ui.span('Content starts below ...')

                with ui.div(class_='d-flex gap-5 align-items-center'):
                    @render.express
                    @print_func_name
                    def renderShowLitResearch():
                        if input.text_outline().strip():
                            ui.input_switch('switch_show_lit_research', 'Literature Search', value=(config_app.vector_db_collections_id_lit_search is not None))

                    @render.express
                    @print_func_name
                    def renderRAGAndRefInfo():
                        files, _ = getAttachedFiles()
                        if not files: return
                    
                        with ui.popover(placement='bottom', options={'trigger': 'focus'}):
                            ui.input_action_link('dummy', 'Using context from attached documents', class_='text-link')
                            with ui.div(class_='d-flex flex-column gap-2'):
                                with ui.div():
                                    for i, (_, file_name, file_type) in enumerate(files):
                                        if file_type != vector_db_collections_type.UPLOADED_FILES.value: continue
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
                            
            with ui.div(class_='content outline'):
                with ui.card(id='ctx_menu', style='display: none; position: absolute; z-index: 10; width: 250px; height: 75px'):
                    ui.input_action_button(id='btn_regenerate_text', label='Regenerate paragraph')
                with ui.div(id='content'):
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
                                if 'http://' in ref:
                                    with ui.div(class_='d-flex gap-1 flex-wrap'):
                                        ui.HTML(re.sub(r'( https?://\S+)', r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', f'{i+1}. {ref}'))
                                else:
                                    ui.span(f'{i+1}. {ref}')

    ui.include_js(Config.DIR_HOME / "www" / "js" / "addon.js")
    
    @reactive.effect
    @reactive.event(input.btn_new_file, ignore_init=True)
    @print_func_name
    def showNewFile():
        config_app.resetContentVars()
        reload_view_flag.set(not reload_view_flag.get())

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
                                field_values=[[config_app.session_id], [file_name], valid_file_statuses])
        
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

            outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'

            with open(outline_file_path, 'w') as fp:
                json.dump({}, fp)

        reload_view_flag.set(not reload_view_flag.get())
        reload_generated_docs_view_flag.set(not reload_generated_docs_view_flag.get())
        
        ui.notification_show('File name saved.', type='message')

    @reactive.effect
    @reactive.event(input.btn_open_outline_manager)
    @print_func_name
    def openOutlineManager():
        outline = input.text_outline().strip()
        if outline == '':
            outline_manager_view = mod_ai_outline_creator(getUIID('ai_outline_creator'),
                                                          saved_outline=outline_from_outline_manager,
                                                          config_app=config_app,
                                                          reload_uploaded_docs_view_flag=reload_uploaded_docs_view_flag,
                                                          close_fn=ui.modal_remove)
        else:

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
    @reactive.event(outline_from_outline_manager, ignore_init=True)
    @print_func_name
    def setOutlineFromOutlineManager():
        ui.update_text_area(id='text_outline', value=outline_from_outline_manager.get())
        
    @print_func_name
    def setContent(content):
        loop = asyncio.get_event_loop()
        loop.create_task(stream._send_content_message(content, "replace", []))
        
    @reactive.effect
    @reactive.event(input.btn_show_hide_outline)
    @print_func_name
    def showOrHideOutline():
        show_outline.set(not show_outline.get())

        if not config_app.file_name: return
        
        outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'

        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        raw_outline = '\n'.join(getRawOutline(d_outline))
        ui.update_text_area(id='text_outline', value=raw_outline)

    @print_func_name
    def clearContent():

        if not config_app.generated_files_id: return

        # -------------------------------------------------------------
        # Remove all ai generated content from the outline
        # -------------------------------------------------------------
        outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'
        
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        d_outline = resetOutline(d_outline)

        with open(outline_file_path, mode='w') as fp:
            json.dump(d_outline, fp)

        reload_view_flag.set(not reload_view_flag.get())

    @reactive.effect
    @reactive.event(input.switch_show_lit_research, ignore_init=True)
    @print_func_name
    def enableLitResearch():
        
        if not config_app.generated_files_id:
            ui.notification_show("Please create a new file or select an existing file.", type="error")
            return
        
        if ((input.switch_show_lit_research() and config_app.vector_db_collections_id_lit_search) or
        (not input.switch_show_lit_research() and not config_app.vector_db_collections_id_lit_search)):
            return
        
        clearContent()
        
        if not input.switch_show_lit_research():
            detachDocs(config_app.generated_files_id, config_app.vector_db_collections_id_lit_search)
            config_app.vector_db_collections_id_lit_search = None
            config_app.setAgent()
            return
        
        if config_app.vector_db_collections_id_lit_search: return

        current_time = datetime.now()

        ids = insertIntoDB(table_name='vector_db_collections', 
                        field_names=['email', 'session', 'generated_files_id', 'type', 'status', 'create_date', 'update_date'],
                        field_values=[[config_app.email], [config_app.session_id], [config_app.generated_files_id],
                                    [vector_db_collections_type.LITERATURE.value], 
                                    [vector_db_collections_status.ACTIVE.value], 
                                    [current_time], [current_time]])
        vector_db_collections_id = int(ids[0])
        
        vector_db_collection_name_lit_search = f'{Config.APP_NAME_AS_PREFIX}_collection_{vector_db_collections_id}'
        createVectorDBCollection(collection_name=vector_db_collection_name_lit_search)

        ai_architecture = generated_files_ai_architecture.RAG.value

        updateDB(table_name='generated_files', 
                update_fields=['ai_architecture', 'update_date'], 
                update_values=[ai_architecture, current_time], 
                select_fields=['id'], 
                select_values=[[config_app.generated_files_id]])

        config_app.vector_db_collections_id_lit_search = vector_db_collections_id
        config_app.setAgent()
        
    @reactive.calc
    @reactive.event(reload_view_flag, reload_attached_files_view_flag)
    @print_func_name
    def getAttachedFiles():
        files, file_info = [], {}
        if config_app.vector_db_collections_id is not None:
            refs, uploaded_file_info = getVectorDBFiles(config_app.vector_db_collections_id)
            files += refs
            file_info |= uploaded_file_info

        return files, file_info
    
    @reactive.calc
    @reactive.event(reload_view_flag, reload_attached_files_view_flag)
    @print_func_name
    def getAttachedLiterature():
        files, file_info = [], {}
        if config_app.vector_db_collections_id_lit_search is not None:
            refs, literature_info = getVectorDBFiles(config_app.vector_db_collections_id_lit_search)
            files += refs
            file_info |= literature_info

        return files, file_info

    @reactive.calc
    @reactive.event(reload_view_flag, reload_attached_files_view_flag)
    @print_func_name
    def applyGetVectorDBFiles():

        files_attached, file_info_attached = getAttachedFiles()
        files_lit, file_info_lit = getAttachedLiterature()
        
        return files_attached + files_lit, file_info_attached | file_info_lit
    
    @reactive.effect
    @reactive.event(input.btn_delete_rag)
    @print_func_name
    def applyDetachDocs():

        clearContent()
        detachDocs(config_app.generated_files_id, config_app.vector_db_collections_id)
        config_app.vector_db_collections_id = None
        config_app.setAgent()
        reload_attached_files_view_flag.set(not reload_attached_files_view_flag.get())

    @reactive.effect()
    @reactive.event(reload_view_flag)
    @print_func_name
    def showContent():
        if not config_app.file_name: 
            # Reset file name, outline and content
            ui.update_checkbox(id='chk_use_example', value=False)
            ui.update_text(id='text_file_name', value=config_app.outline)
            ui.update_text_area(id='text_outline', value='')
            setContent('')
            references.set([])
            return
        
        # Cancel writing
        stream.latest_stream.cancel()
        
        if not config_app.agent: config_app.setAgent()
        
        # Load outline
        outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'
        
        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)
        
        raw_outline = '\n'.join(getRawOutline(d_outline))

        # Load query
        query_file_path = Config.DIR_CONTENTS / f'query_{config_app.generated_files_id}.json'
        if query_file_path.exists():
            with open(query_file_path) as fp:
                query = fp.read()
        else:
            query = ''

        if query:
            ui.update_navs(id='user_input_panel', selected='Query')
        else:
            ui.update_navs(id='user_input_panel', selected='Structured Outline')

        # Show file name, query, outline and content
        ui.update_text(id='text_file_name', value=config_app.file_name)
        ui.update_text_area(id='text_query', value=query)
        ui.update_text_area(id='text_outline', value=raw_outline)
        
        references.set([])
        attached_references, _ = applyGetVectorDBFiles()
        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, 
                                                        outline_file_path, 
                                                        content_gen_scope=ContentGenerationScope.DO_NOT_GENERATE.value, 
                                                        attached_references=attached_references), 
                                        clear=True))

    @reactive.effect
    @reactive.event(input.chk_use_example, ignore_init=True)
    @print_func_name
    def useExample():
        
        example = textwrap.dedent('''\
        # Title: Quantam Computing and its Applications
        ## Introduction
        <instructions>
        - High-level overview of quantum computing
        - Importance and potential applications
        </instructions>
        <content>
        ## 1. History of Quantum Computing
        Quantum computing has its roots in the early 1980s when physicist Richard Feynman proposed the idea of a quantum computer that could simulate physical systems more efficiently than classical computers. Over the years, significant milestones have been achieved, including the development of quantum algorithms like Shor's algorithm for factoring large numbers and Grover's algorithm for database searching.
        <content>
        ## 2. Quantum Information Processing
        ### Quantum Bits (Qubits)
        <instructions>
        - Definition of qubits
        - Comparison with classical bits
        - Types of qubits (e.g., superconducting, trapped ions)
        </instructions>
        <content>
        ### Unary Operators
        <content>''')
        
        if not input.chk_use_example(): example = ''

        ui.update_text_area('text_outline', value=example)

    @print_func_name
    def saveOutline(regenerate=False):
        
        # Check if regeneration is needed
        records = selectFromDB('generated_files', 
                            field_names=['id', 'file_name'], 
                            field_values=[[config_app.generated_files_id], [config_app.file_name]])
        
        if not (records.empty or regenerate): return True

        outline = input.text_outline().strip()
        query = input.text_query().strip()
        active_input_panel = input.user_input_panel()

        if ((active_input_panel == 'Query' and query == '') or 
            (active_input_panel == 'Structured Outline' and outline == '')): return False

        if active_input_panel == 'Query' and query != '':
            ui.notification_show("Creating outline", type="message")
            outline = generateOutlineByAI(query)
            ui.update_text_area(id='text_outline', value=outline)
            ui.notification_show("Outline created successfully.", type="message")
            d_outline = processOutline(outline)
        else:
            invalid_formatting = False
            if '<content>' in outline and '# ' in outline:
                try:
                    d_outline = processOutline(outline)
                except Exception as exp:
                    logging.error(f'Outline formatting is invalid: {exp}') 
                    invalid_formatting = True
            else:
                invalid_formatting = True 
                
            if invalid_formatting:
                try:
                    outline = processOutlineByAI(outline)
                    ui.update_text_area(id='text_outline', value=outline)
                    ui.notification_show("The provided outline was reformatted to find the proper positions for AI to write in.", type="warning")
                    d_outline = processOutline(outline)
                except Exception as exp:
                    logging.error(f'Failed to generate outline with AI: {exp}') 
                    ui.notification_show("Outline formatting is invalid. Failed to fix it with AI. Please follow the outline format mentioned in docs.", type="error")
                    return False
            
        with open(Config.DIR_CONTENTS / f'query_{config_app.generated_files_id}.json', 'w') as fp:
            fp.write(query)

        with open(Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json', 'w') as fp:
            json.dump(d_outline, fp)

        current_time = datetime.now()
        
        updateDB('generated_files', 
                    update_fields=['status', 'create_date', 'update_date'], 
                    update_values=[generated_files_status.CREATED.value, current_time, current_time], 
                    select_fields=['id'], 
                    select_values=[[config_app.generated_files_id]])

        return True
    
    @print_func_name
    def resetContentPara(d_outline, section_list, paragraph_index):
        '''
        Resets specified paragraph for regeneration within a section hierarchy
        '''
    
        if len(section_list) == 1:
            
            assert SpecialSectionTypes.CONTENT.value in d_outline[section_list[0]], 'Hierarchy does not contain content'

            count_par = 0
            for i, (content_type, content) in enumerate(d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value]):

                if content_type not in [ContentTypes.CONTENT_AI.value, ContentTypes.CONTENT_USER.value]:
                    continue
                
                # Detect the specified paragraph 
                count_par += content.count('\n\n') + 1
                if paragraph_index < count_par:
                    break
            
            assert i < len(d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value]), 'Intended paragraph was not found for regeneration'
            
            # Reset the specified paragraph in the outline
            pars = content.split('\n\n')

            # The paragraph_index indicates the index based on the overall paragraph count.
            # But internally, a paragraph can belong to either content_ai or content_user content block.
            # Here we are finding the index of the paragraph within the current content block.
            index_current_par = len(pars)-(count_par - paragraph_index)
            
            # A new ContentTypes.CONTENT_AI.value block is inserted to indicate the paragraph to be regenerated
            previous_para_current_content, next_para_current_content = [], []
            if index_current_par > 0:
                previous_para_current_content = [[d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value][i][0], '\n\n'.join(pars[:index_current_par])]]
            if index_current_par < len(pars)-1:
                next_para_current_content = [[d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value][i][0], '\n\n'.join(pars[index_current_par+1:])]]

            d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value] = (d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value][:i]
                                                    + previous_para_current_content
                                                    + [[ContentTypes.CONTENT_AI.value, '']]
                                                    + next_para_current_content
                                                    + d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value][i+1:])
        else:
            resetContentPara(d_outline[section_list[0]], section_list[1:], paragraph_index)

    @reactive.effect
    @reactive.event(input.btn_regenerate_text)
    @print_func_name
    def regenerateParagraph():

        hierarchy = input.selected_para_hierarchy()
        if not hierarchy: return
        
        outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'
        
        # Read outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)
        
        *section_list, paragraph_index = hierarchy
        
        resetContentPara(d_outline, section_list, paragraph_index)

        # Reset outline
        with open(outline_file_path, 'w') as fp:
            json.dump(d_outline, fp)

        references.set([])
        attached_references, _ = applyGetVectorDBFiles()
        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, 
                                                        outline_file_path,
                                                        attached_references=attached_references,
                                                        write_abstract_flag_value=not write_abstract_flag.get()), 
                                        clear=True))

    @print_func_name
    async def generateResponse(d_outline, 
                               outline_file_path,
                               content_gen_scope=ContentGenerationScope.GENERATE_IF_NEEDED.value, 
                               attached_references=[], 
                               attached_files_reload_flag_val=True,
                               write_abstract=False,
                               write_abstract_flag_value=None):

        @print_func_name
        def getHierarchy(d_outline, 
                         content_pre=[], 
                         current_section_list=[],
                         content_pre_summary='', 
                         counter=1, 
                         specific_section_header_chain=[],
                         skip_section_chain=[],
                         skip_gen=False):
            '''
            Get all previous content and current section hierarchy up to the point that needs ai generation
            '''
            instructions = ''
            is_gen_needed = False
            for k in d_outline:
                skip_current_section = skip_gen
                if len(skip_section_chain) > 0 and skip_section_chain == current_section_list: skip_current_section = True
                if len(specific_section_header_chain) > 0 and specific_section_header_chain[0] != k: continue
                if k != SpecialSectionTypes.CONTENT.value:
                    content_pre, current_section_list, content_pre_summary, instructions, is_gen_needed = getHierarchy(d_outline[k], 
                                                                content_pre + [f'{'#' * counter} {k}'],
                                                                current_section_list + [k],
                                                                content_pre_summary,
                                                                counter + 1,
                                                                specific_section_header_chain=specific_section_header_chain[1:],
                                                                skip_section_chain=skip_section_chain,
                                                                skip_gen=skip_current_section)
                    if not is_gen_needed: current_section_list.pop()
                else:
                    content_list = []
                    for v in d_outline[k]:
                        if v[0] == ContentTypes.CONTENT_AI.value:
                            content_list.append(v)
                            if v[1] != '' or skip_current_section:
                                content_pre.append(v[1])
                            else:
                                is_gen_needed = True 
                                break
                        elif v[0] == ContentTypes.CONTENT_USER.value:
                            content_list.append(v)
                            content_pre.append(v[1])
                        elif v[0] == ContentTypes.CONTENT_PRE_SUMMARY.value:
                            content_pre_summary = v[1] + '\n\n' + '\n\n'.join([c for _, c in content_list])
                        elif v[0] == ContentTypes.INSTRUCTIONS.value:
                            instructions = v[1]

                    if is_gen_needed: current_section_list.append(content_list)      
                
                if is_gen_needed: break
                        
            return content_pre, current_section_list, content_pre_summary, instructions, is_gen_needed
        
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
                        if content_type == ContentTypes.CONTENT_USER.value or content != '':
                            section_text_lines.append(content)
                        else:
                            section_text_lines.append('<content>')
            
            return '\n\n'.join(section_text_lines)
        
        @print_func_name
        def insertContent(d_outline, section_list, content_ai, content_pre_summary):
            '''
            Inserts the ai generated content to the appropriate position of the outline
            '''

            if not len(section_list): return
            
            if len(section_list) == 1:
                for i, (content_type, content) in enumerate(d_outline[SpecialSectionTypes.CONTENT.value]):
                    if content_type == ContentTypes.CONTENT_AI.value and content == '':
                        d_outline[SpecialSectionTypes.CONTENT.value][i][1] = content_ai
                        for j, (content_type, _) in enumerate(d_outline[SpecialSectionTypes.CONTENT.value]):
                            if content_type == ContentTypes.CONTENT_PRE_SUMMARY.value:
                                d_outline[SpecialSectionTypes.CONTENT.value][j][1] = content_pre_summary
                                break
                        else:
                            d_outline[SpecialSectionTypes.CONTENT.value].append([ContentTypes.CONTENT_PRE_SUMMARY.value, content_pre_summary])
                        return
            else:
                insertContent(d_outline[section_list[0]], section_list[1:], content_ai, content_pre_summary)
            
        @print_func_name
        def getSanitizedReferences(references_ai, attached_references, attached_files_reload_flag_val):

            lit_ids = []
            for ref_id, _ in references_ai.items():
                if ref_id not in attached_references:
                    lit_ids.append(ref_id)

            if lit_ids: 
                refs, _ = getLiteraturesFromDB(lit_ids)
                attached_references |= {str(k): v for k, v, _ in refs}
                reload_attached_files_view_flag.set(attached_files_reload_flag_val)

            return attached_references, attached_files_reload_flag_val

        @print_func_name
        def processCitation(content, ref_list, attached_references):

            content = formatCitations(content)

            ref_groups = re.findall(r'CITE\(([\w\W]+?)\)', content)
    
            refs_seen = set()
            d_ref = {}
            for refs in ref_groups:
                refs = re.sub(r'\),\ *CITE\(', ', ', refs)
                if refs in refs_seen: continue
                refs_seen.add(refs)
                ref_links = []
                for ref in refs.split(','):
                    ref = ref.strip()
                    if ref not in attached_references: 
                        logging.warning(f'{ref} not found in reference list, skipping...')
                        continue
                    if ref in d_ref:
                        ref_links.append(d_ref[ref])
                        continue
                    try:
                        d_ref[ref] = ref_list.index(attached_references[ref]) + 1
                    except ValueError:
                        ref_list.append(attached_references[ref])
                        d_ref[ref] = len(ref_list)
                    
                    ref_links.append(d_ref[ref])
                
                ref_links = sorted(ref_links)
        
                if len(ref_links) > 2 and len(ref_links) == (ref_links[-1]-ref_links[0]+1):
                    new_citation = f'<a href="#:~:text=References">{ref_links[0]}-{ref_links[-1]}</a>'
                else:
                    new_citation = f'{', '.join([f'<a href="#:~:text=References">{ref_cite}</a>' for ref_cite in sorted(ref_links)])}'
                content = content.replace(f'CITE({refs})', new_citation)

            if 'CITE' in content: breakpoint()

            return content, ref_list
        
        @print_func_name
        async def dummy(i=None):
            await asyncio.sleep(3)
            if i is None:
                return {'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse id erat lectus. Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis, lobortis justo sit amet, blandit libero. Suspendisse hendrerit sapien sit amet augue aliquam, at auctor purus mattis. In sed volutpat elit, et vehicula urna. Mauris libero lectus, dignissim quis facilisis aliquam, facilisis et tortor. Proin finibus lacus lectus, nec sodales ex vulputate in. Integer congue condimentum tempus. Ut ut elit in tellus viverra ornare at at nisl. Nam tincidunt vulputate pretium. Morbi purus purus, convallis in fringilla in, rhoncus a nisi. Curabitur eu pretium ligula. Vestibulum ullamcorper elit sit amet feugiat rutrum. Aenean tempor massa risus, non pulvinar justo scelerisque et. Maecenas non aliquet risus. Maecenas ac sem ut lorem commodo tempus.\nDonec eleifend tristique erat, sit amet sodales arcu ullamcorper eu. Aliquam non dapibus mi. Donec pretium risus ipsum, eu porttitor lectus porta in. Nulla facilisi. Proin rhoncus lectus nulla, non egestas sapien suscipit non. Maecenas bibendum semper cursus. Praesent in velit ut tellus tincidunt cursus laoreet et dolor. Morbi maximus maximus nunc nec luctus. Aenean ut sapien euismod, lacinia justo id, vestibulum ipsum.'}
            if i % 2:
                return {'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse id erat lectus [CITE(27)].'}
            return {'content': 'Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis, lobortis justo sit amet, blandit libero. Suspendisse hendrerit sapien sit amet augue aliquam, at auctor purus mattis [CITE(28)].'}
        
        @print_func_name
        def findAbstractSection(d_outline: dict) -> str:
            '''
            Returns the header of an abstract section (if the outline has abstract) 
            or an empty string (if the outline does not have abstract)
            '''

            @print_func_name
            def isThisAbstract(section_header):
                response = config_app.agent_abstract_detector.invoke({'current_section': section_header})
                return response[ContentTypes.IS_ABSTRACT.value]
            
            if not d_outline: return ''

            title = next(iter(d_outline))
            first_section_header = next(iter(d_outline[title]))
            
            content = d_outline[title][first_section_header][SpecialSectionTypes.CONTENT.value]
            if len(content) > 0 and content[0][0] == ContentTypes.IS_ABSTRACT.value:
                return first_section_header
            
            if isThisAbstract(first_section_header): 
                d_outline[title][first_section_header][SpecialSectionTypes.CONTENT.value].insert(0, (ContentTypes.IS_ABSTRACT.value, True))
                return first_section_header
            
            return ''
        
        @print_func_name
        def sanitizeContent(content):
            return re.sub(r' \~([^\~])', r' \\~\1', content)
        
        @print_func_name
        def isContentFullyWritten(content_list):
            for content_type, content in content_list:
                if content_type == ContentTypes.CONTENT_AI.value and content == '':
                    return False
            return True

        title = next(iter(d_outline))
        abstract_section_header = findAbstractSection(d_outline)

        attached_references = {str(k): v for k, v, _ in attached_references}
        
        len_last_content_pre, content_pre_new = 0, None
        ref_list = []

        if write_abstract:
            ui.notification_show(f"Writing {abstract_section_header}", type="message")
        
        while True:

            if write_abstract:

                content_pre, current_section_list, _, instructions, is_gen_needed = getHierarchy(d_outline)
                _, _, content_pre_summary, *_ = getHierarchy(d_outline, skip_section_chain=[title, abstract_section_header])

                agent = config_app.agent_abstract_writer

            else:

                match content_gen_scope:
                    case ContentGenerationScope.DO_NOT_GENERATE.value:
                        content_pre, current_section_list, content_pre_summary, instructions, is_gen_needed = getHierarchy(d_outline, skip_gen=True)
                    case ContentGenerationScope.GENERATE_IF_NEEDED.value:
                        content_pre, current_section_list, content_pre_summary, instructions, is_gen_needed = getHierarchy(d_outline, skip_section_chain=[title, abstract_section_header])

                agent = config_app.agent

            if content_pre_new is None:
                content_pre_new = content_pre
            else:
                content_pre_new = content_pre[len_last_content_pre + 1:]

            content_pre_new = '\n\n'.join(content_pre_new) + '\n\n'
            
            if attached_references:
                content_pre_new, ref_list = processCitation(content_pre_new, ref_list, attached_references)
                references.set(ref_list.copy())
                await reactive.flush()
            
            len_last_content_pre = len(content_pre)
        
            yield sanitizeContent(content_pre_new)
            
            if not is_gen_needed: break
        
            # if attached_references:
            #     response = await dummy(len(ref_list))  
            # else:
            #     response = await dummy()

            if not content_pre_summary: content_pre_summary = '\n\n'.join(content_pre)
            current_section = getSectionText(current_section_list)
            
            response = await agent.ainvoke({'content_pre': content_pre_summary, 
                                            'current_section': current_section,
                                            'content_specific_instructions': instructions})
            
            content, content_pre_summary = response['content'], response['content_pre']
            
            attached_references_ai = response.get('references', {})
            attached_references, attached_files_reload_flag_val = getSanitizedReferences(attached_references_ai, attached_references, not attached_files_reload_flag_val)

            insertContent(d_outline, current_section_list, content, content_pre_summary)

            if attached_references:
                response_with_citations, ref_list = processCitation(content, ref_list, attached_references)
                references.set(ref_list.copy())
                await reactive.flush()
            
            with open(outline_file_path, 'w') as fp:
                json.dump(d_outline, fp)

            current_time = datetime.now()

            updateDB('generated_files', 
                        update_fields=['status', 'update_date'], 
                        update_values=[generated_files_status.RUNNING.value, current_time], 
                        select_fields=['id'], 
                        select_values=[[config_app.generated_files_id]])
            
            content = sanitizeContent(content)

            tokens = response_with_citations.split(' ') if attached_references else content.split(' ')
            for i, s in enumerate(tokens):
                await asyncio.sleep(0.05)
                yield s + ' ' if i < len(tokens)-1 else s + '\n\n'

            ui.notification_show("Progress saved", type="message")

        # Add abstract section if needed
        if (content_gen_scope == ContentGenerationScope.GENERATE_IF_NEEDED.value and
            abstract_section_header != '' and
            write_abstract_flag_value is not None):

            *_, is_gen_needed = getHierarchy(d_outline, specific_section_header_chain=[title, abstract_section_header])
            if is_gen_needed:
                write_abstract_flag.set(write_abstract_flag_value)

    @reactive.effect
    @reactive.event(write_abstract_flag, ignore_init=True)
    @print_func_name
    async def writeAbstract():

        outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'
        
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)
        
        attached_references, _ = applyGetVectorDBFiles()
        await stream.stream(generateResponse(d_outline, 
                                             outline_file_path,
                                             attached_references=attached_references,
                                             write_abstract=True), clear=True)
            
    @print_func_name
    async def generate(regenerate):

        if config_app.file_name == '':
            ui.notification_show("Please save a file name.", type="error")
            return

        if not saveOutline(regenerate=regenerate): 
            ui.notification_show("Please provide an outline.", type="error")
            return

        outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'
        
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)

        references.set([])
        attached_references, _ = applyGetVectorDBFiles()
        await stream.stream(generateResponse(d_outline, 
                                             outline_file_path,
                                             attached_references=attached_references,
                                             attached_files_reload_flag_val=reload_attached_files_view_flag.get(),
                                             write_abstract_flag_value=not write_abstract_flag.get()), clear=True)
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
    async def startFromScratch():
        
        if config_app.is_writing:
            ui.notification_show('Writing is in progress. Please click "Pause" button first.', type='message')
            return
        
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
            
            loop = asyncio.get_event_loop()
            loop.create_task(session.send_custom_message('reload_content', {'ui_id': ui_id}))

        ui.update_action_button("btn_resume_pause", icon=faicons.icon_svg("pause" if stream_status == "running" else "play"))

    return content