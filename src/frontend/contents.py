from shiny import reactive
from shiny.express import ui, render, module
from shiny.types import FileInfo
import faicons
from utils import Config, getUIID, print_func_name
from ..backend.db import insertIntoDB, updateDB, selectFromDB, \
                generated_files_status, \
                generated_files_ai_architecture, \
                vector_db_collections_type, \
                vector_db_collections_status
from .manage_outline import resetOutline, processOutline, generateOutlineByAI, processOutlineByAI, getRawOutline, mod_outline_manager
from .common import getFileType, getFileTypeIcon, getVectorDBFiles, detachDocs, getDocContent, createVectorDBCollection, getLiteraturesFromDB, formatCitations, loadFilesToVectorDBCollection
from .defaults import ContentGenerationScope, SpecialSectionTypes, ContentTypes
from .concept_map import mod_concept_map
import asyncio
import json
import textwrap
import re
from datetime import datetime
import io
import logging
from pathlib import Path

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

    regen_instructions = reactive.value('')
    
    stream = ui.MarkdownStream("stream")

    
    with ui.div(class_='d-flex name-bar'):
        with ui.div(class_='col file-name'):
            ui.input_text('text_file_name', 'File Name', value=config_app.file_name),
            ui.input_action_button('btn_save_file_name', 'Save')
            with ui.tooltip(placement="top"):
                ui.input_action_button('btn_new_file', '', icon=faicons.icon_svg("plus"))
                "New File"
    with ui.div(class_='input ps-3 pe-3'):
        with ui.div(class_='d-flex justify-content-between align-items-center pt-2 pb-2', style='font-size: 0.8em !important'):            
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
                    if not input.text_outline().strip(): return
                    with ui.tooltip(placement="top"):
                        ui.input_action_button('btn_edit_outline', label='', icon=faicons.icon_svg("pen-to-square"))
                        "Edit outline"
        @render.express
        @print_func_name
        def renderInputBar():
            class_name_outline, class_name_controls = ('col', 'd-flex flex-column gap-2 align-items-center') if show_outline.get() else ('col d-none', 'd-flex flex-row gap-2')
            with ui.div(class_='d-flex gap-3'):
                with ui.div(class_=class_name_outline):            
                    with ui.navset_underline(id="user_input_panel", selected="Query"):
                        with ui.nav_panel("Query"):
                            ui.input_text_area(id='text_query', label='', placeholder='''Write an query...''', rows=8, width='100%')
                            ui.input_file("btn_upload_topic_desc", "Choose a reference document (optional)", accept=[".txt", ".pdf", ".docx"], multiple=False)
                        with ui.nav_panel("Structured Outline"):
                            with ui.div(class_='col mt-2'):
                                ui.input_checkbox('chk_use_example', 'Use example', value=False)
                            ui.input_text_area(id='text_outline', label='', placeholder='''Write an outline...''', rows=8, width='100%')
                with ui.div(class_='col-auto d-flex justify-content-around align-items-start', style="padding-top: 40px"):
                    with ui.div(class_=class_name_controls):
                        @render.express
                        @print_func_name
                        def renderControlButtons():
                            text, ico = ('Hide outline', 'eye-slash') if show_outline.get() else ('Show outline', 'eye')
                            with ui.tooltip(placement="top"):
                                ui.input_action_button('btn_show_hide_outline', '', icon=faicons.icon_svg(ico))
                                text
                            if input.user_input_panel() == "Query":
                                with ui.tooltip(placement="top"):
                                    ui.input_action_button('btn_create_outline', '', icon=faicons.icon_svg("list-ol"))
                                    "Create outline"
                            if input.text_outline().strip() != '':
                                with ui.tooltip(placement="top"):
                                    ui.input_action_button('btn_regenerate', '', icon=faicons.icon_svg("repeat"))
                                    "Write from the start"
                                with ui.tooltip(placement="top"):
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
                with ui.div(id='regenerate_text_controls', class_='border border-dark rounded p-2', style='display: None'):
                    with ui.div(class_='d-flex gap-2 align-items-center'):
                        ui.input_radio_buttons(id='radio_regeneration_type', label='', choices=['Expand', 'Rephrase', 'Remove'], inline=True)
                        with ui.panel_conditional('input.radio_regeneration_type != "Remove"'):
                            with ui.tooltip(placement='top'):
                                with ui.div():
                                    with ui.popover(id='popover_regen_instructions', placement='bottom'):
                                        with ui.div():
                                            @render.express
                                            @print_func_name
                                            def renderRegenInstuctionsButton():
                                                ui.input_action_button(id='btn_regen_instructions', label='', icon=faicons.icon_svg('clipboard', style='solid' if regen_instructions.get() else 'regular'))
                        
                                        with ui.div(class_='d-flex flex-column align-items-end'):
                                            @render.express
                                            @print_func_name
                                            def renderRegenInstuctionsText():
                                                ui.input_text_area(id='txt_regen_instructions', label='', value=regen_instructions.get(), rows=10, cols=8)
                                            with ui.div():
                                                ui.input_action_button(id='btn_add_regen_instructions', label='Submit')
                                "Instructions"
                        ui.div(class_='vertical-divider')
                        with ui.tooltip(placement="top"):
                            ui.input_action_button(id='btn_regenerate_text', label='', icon=faicons.icon_svg("play"))
                            "Regenerate"
                    
                @render.express
                @print_func_name
                def renderShowLitResearch():
                    if input.text_outline().strip():
                        ui.input_switch('switch_show_lit_research', 'Literature Search', value=(config_app.vector_db_collections_id_lit_search is not None))

                @render.express
                @print_func_name
                def renderAttachedFiles():

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

                @render.express
                @print_func_name
                def renderConceptMapGeneration():
                    _ = reload_view_flag.get()
                    if config_app.generated_files_id is None: return
                    ui.input_action_button(id='btn_show_concept_map', label="Concept map")

                        
        with ui.div(class_='content outline'):
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
    ui.include_js(Config.DIR_HOME / "www" / "js" / "concept_map_graph.js")
    
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

    def showOutlineEditor(outline):

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
    @reactive.event(input.btn_edit_outline)
    @print_func_name
    def editOutline():
        outline = input.text_outline().strip()
        if outline == '': return
        showOutlineEditor(outline)

    @reactive.effect
    @reactive.event(outline_from_outline_manager, ignore_init=True)
    @print_func_name
    def setOutlineFromOutlineManager():
        ui.update_text_area(id='text_outline', value=outline_from_outline_manager.get())
        ui.update_navs(id='user_input_panel', selected='Structured Outline')
        
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

        # --------------------------------------
        # Load query
        # --------------------------------------
        query_file_path = Config.DIR_CONTENTS / f'query_{config_app.generated_files_id}.txt'

        if query_file_path.exists():
            # Read query
            with open(query_file_path) as fp:
                query = fp.read()
        else:
            query = ''

        ui.update_text_area(id='text_query', value=query)
        
        # --------------------------------------
        # Load outline
        # --------------------------------------
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
        query_file_path = Config.DIR_CONTENTS / f'query_{config_app.generated_files_id}.txt'
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

    @reactive.effect
    @reactive.event(input.btn_upload_topic_desc)
    @print_func_name
    def uploadTopicDesc():

        if config_app.file_name == '':
            ui.notification_show("Please save a file name.", type="error")
            return

        files: list[FileInfo] | None = input.btn_upload_topic_desc()
        
        dir_temp_files = Config.DIR_CONTENTS / 'temp' / f'{config_app.generated_files_id}'
        
        # Remove previously uploaded files in temp if exist
        if dir_temp_files.exists() and dir_temp_files.is_dir():
            for f in dir_temp_files.iterdir():
                f.unlink()
        else:
            dir_temp_files.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            with open(dir_temp_files / Path(file['datapath']).name, 'wb') as fp:
                with open(file['datapath'], 'rb') as fp_r:
                    fp.write(fp_r.read())

    @reactive.effect
    @reactive.event(input.btn_create_outline)
    @print_func_name
    def createOutlineByAI():
        
        if config_app.file_name == '':
            ui.notification_show("Please save a file name.", type="error")
            return
        
        query = input.text_query().strip()

        if not query:
            ui.notification_show("Please enter a query to create an outline.", type="error")
            return
        
        with open(Config.DIR_CONTENTS / f'query_{config_app.generated_files_id}.txt', 'w') as fp:
            fp.write(query)

        dir_temp_files = Config.DIR_CONTENTS / 'temp' / f'{config_app.generated_files_id}'

        ui.notification_show("Creating outline", type="message")

        outline = generateOutlineByAI(query, dir_path_ref_files=dir_temp_files if dir_temp_files.exists() else None)

        showOutlineEditor(outline)

    @print_func_name
    def saveOutline(regenerate=False):
        
        # Check if regeneration is needed
        records = selectFromDB('generated_files', 
                            field_names=['id', 'file_name'], 
                            field_values=[[config_app.generated_files_id], [config_app.file_name]])
        
        if not (records.empty or regenerate): return True

        outline = input.text_outline().strip()
        
        if outline == '': return
            
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
    def changeContentParaOutline(d_outline, section_list, index_paragraph, regeneration_type):
        '''
        Resets specified paragraph for regeneration within a section hierarchy
        '''
    
        is_abstract = False
        if len(section_list) == 1:
            
            assert SpecialSectionTypes.CONTENT.value in d_outline[section_list[0]], 'Hierarchy does not contain content'

            current_section_content = d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value]

            count_par, index_current_content_block = 0, -1

            for i, (content_type, content) in enumerate(current_section_content):

                if content_type == ContentTypes.IS_ABSTRACT.value: is_abstract = True

                if content_type not in [ContentTypes.CONTENT_AI.value, ContentTypes.CONTENT_USER.value]:
                    continue
                
                # Detect the specified paragraph 
                count_par += content.count('\n\n') + 1

                # The index_paragraph indicates the index based on the overall paragraph count.
                # But internally, a paragraph can belong to either content_ai or content_user content block.
                # Here we are finding the index of the paragraph within the current content block.
                if index_current_content_block < 0 and index_paragraph < count_par: 
                    pars = content.split('\n\n')
                    index_current_content_block = i
                    index_current_par = len(pars)-(count_par - index_paragraph)

            assert index_current_content_block >= 0, "Intended paragraph was not found for regeneration"
            
            # Get previous and next paragraphs
            previous_para, next_para = [], []
            if index_current_par > 0:
                prev_para_content = '\n\n'.join(pars[:index_current_par])
                previous_para = [[current_section_content[index_current_content_block][0], prev_para_content]] if prev_para_content != '' else []
            else:
                prev_para_content = ''
            if index_current_par < len(pars)-1:
                next_para_content = '\n\n'.join(pars[index_current_par+1:])
                next_para = [[current_section_content[index_current_content_block][0], next_para_content]] if next_para_content != '' else []
                
            # If current para needs to be expanded on, keep the current content and add an empty ContentTypes.CONTENT_AI.value block to be written inside.
            # If current para needs to be rephrased, remove the current paragraph and insert an empty ContentTypes.CONTENT_AI.value block to indicate the paragraph to be regenerated.
            # If current para needs to be removed, do not add the new content tag
            match regeneration_type:
                case 'Expand':
                    d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value] = (current_section_content[:index_current_content_block]
                                                                                    + [[current_section_content[index_current_content_block][0], prev_para_content + pars[index_current_par]]]
                                                                                    + [[ContentTypes.CONTENT_AI.value, '']]
                                                                                    + next_para
                                                                                    + current_section_content[index_current_content_block+1:])
                case 'Rephrase':
                    d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value] = (current_section_content[:index_current_content_block]
                                                                                    + previous_para
                                                                                    + [[ContentTypes.CONTENT_AI.value, '']]
                                                                                    + next_para
                                                                                    + current_section_content[index_current_content_block+1:])
                case 'Remove':
                    if count_par > 1:
                        d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value] = (current_section_content[:index_current_content_block]
                                                                                        + previous_para
                                                                                        + next_para
                                                                                        + current_section_content[index_current_content_block+1:])
                    else:
                        d_outline[section_list[0]][SpecialSectionTypes.CONTENT.value] = (current_section_content[:index_current_content_block]
                                                                                        + previous_para
                                                                                        + [[ContentTypes.CONTENT_AI.value, '']]
                                                                                        + next_para
                                                                                        + current_section_content[index_current_content_block+1:])
                    
            return is_abstract
        
        return changeContentParaOutline(d_outline[section_list[0]], section_list[1:], index_paragraph, regeneration_type)

    @reactive.effect
    @reactive.event(input.btn_add_regen_instructions)
    @print_func_name
    def addRegenerationInstructions():
        regen_instructions.set(input.txt_regen_instructions())
        ui.update_popover(id='popover_regen_instructions', show=False)

    @reactive.effect
    @reactive.event(input.btn_regenerate_text)
    @print_func_name
    def regenerateParagraph():

        hierarchy = input.selected_para_hierarchy()
        if not hierarchy: return
        
        outline_file_path = Config.DIR_CONTENTS / f'outline_{config_app.generated_files_id}.json'
        
        # Change outline
        with open(outline_file_path) as fp:
            d_outline = json.load(fp)
        
        *section_list, paragraph_index = hierarchy
        regeneration_type = input.radio_regeneration_type()
        
        is_abstract = changeContentParaOutline(d_outline, section_list, paragraph_index, regeneration_type)

        raw_outline = '\n'.join(getRawOutline(d_outline))
        ui.update_text_area(id='text_outline', value=raw_outline)

        with open(outline_file_path, 'w') as fp:
            json.dump(d_outline, fp)

        # Generate content
        references.set([])
        attached_references, _ = applyGetVectorDBFiles()
        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, 
                                                        outline_file_path,
                                                        content_gen_scope=ContentGenerationScope.GENERATE_IF_NEEDED.value if regeneration_type != 'Remove' else ContentGenerationScope.DO_NOT_GENERATE.value,
                                                        attached_references=attached_references,
                                                        write_abstract=is_abstract,
                                                        write_abstract_flag_value=not write_abstract_flag.get(),
                                                        instructions_additional=regen_instructions.get(),
                                                        num_blocks_to_generate = 1), 
                                        clear=True))
        
        regen_instructions.set('')

    @print_func_name
    async def generateResponse(d_outline, 
                               outline_file_path,
                               content_gen_scope=ContentGenerationScope.GENERATE_IF_NEEDED.value, 
                               attached_references=[], 
                               attached_files_reload_flag_val=True,
                               write_abstract=False,
                               write_abstract_flag_value=None,
                               instructions_additional='',
                               num_blocks_to_generate=None):

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
        def insertContent(d_outline, section_list, content_ai, content_pre_summary, concept_map):
            '''
            Inserts the ai generated content to the appropriate position of the outline
            '''

            def combineSimilarContentBlocks(content_block):

                content_block_new = []
                last_content_type, last_content = '', ''
                for i, (content_type, content) in enumerate(content_block):
                    if last_content_type == content_type:
                        if content_type != ContentTypes.IS_ABSTRACT.value:
                            last_content += ('\n\n' + content)
                    else:
                        if i != 0:
                            content_block_new.append((last_content_type, last_content))
                        last_content_type, last_content = content_type, content
                    
                    if i == len(content_block)-1:
                        content_block_new.append((last_content_type, last_content))

                return content_block_new

            if not len(section_list): return
            
            if len(section_list) == 1:
                is_summary_found, is_concept_map_found = False, False
                for i, (content_type, content) in enumerate(d_outline[SpecialSectionTypes.CONTENT.value]):
                    if content_type == ContentTypes.CONTENT_AI.value and content == '':
                        d_outline[SpecialSectionTypes.CONTENT.value][i][1] = content_ai
                    elif content_type == ContentTypes.CONTENT_PRE_SUMMARY.value:
                        d_outline[SpecialSectionTypes.CONTENT.value][i][1] = content_pre_summary
                        is_summary_found = True
                    elif content_type == ContentTypes.CONCEPT_MAP.value:
                        d_outline[SpecialSectionTypes.CONTENT.value][i][1] = concept_map
                        is_concept_map_found = True
                                
                if not is_summary_found:
                    d_outline[SpecialSectionTypes.CONTENT.value].append([ContentTypes.CONTENT_PRE_SUMMARY.value, content_pre_summary])

                if not is_concept_map_found:
                    d_outline[SpecialSectionTypes.CONTENT.value].append([ContentTypes.CONCEPT_MAP.value, concept_map])

                #d_outline[SpecialSectionTypes.CONTENT.value] = combineSimilarContentBlocks(d_outline[SpecialSectionTypes.CONTENT.value])
            else:
                insertContent(d_outline[section_list[0]], section_list[1:], content_ai, content_pre_summary, concept_map)
            
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
                return {'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse id erat lectus. Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis, lobortis justo sit amet, blandit libero. Suspendisse hendrerit sapien sit amet augue aliquam, at auctor purus mattis. In sed volutpat elit, et vehicula urna. Mauris libero lectus, dignissim quis facilisis aliquam, facilisis et tortor. Proin finibus lacus lectus, nec sodales ex vulputate in. Integer congue condimentum tempus. Ut ut elit in tellus viverra ornare at at nisl. Nam tincidunt vulputate pretium. Morbi purus purus, convallis in fringilla in, rhoncus a nisi. Curabitur eu pretium ligula. Vestibulum ullamcorper elit sit amet feugiat rutrum. Aenean tempor massa risus, non pulvinar justo scelerisque et. Maecenas non aliquet risus. Maecenas ac sem ut lorem commodo tempus.\nDonec eleifend tristique erat, sit amet sodales arcu ullamcorper eu. Aliquam non dapibus mi. Donec pretium risus ipsum, eu porttitor lectus porta in. Nulla facilisi. Proin rhoncus lectus nulla, non egestas sapien suscipit non. Maecenas bibendum semper cursus. Praesent in velit ut tellus tincidunt cursus laoreet et dolor. Morbi maximus maximus nunc nec luctus. Aenean ut sapien euismod, lacinia justo id, vestibulum ipsum.',
                        'content_pre': 'Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis'}
            if i % 2:
                return {'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse id erat lectus [CITE(27)].',
                        'content_pre': 'Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis'}
            return {'content': 'Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis, lobortis justo sit amet, blandit libero. Suspendisse hendrerit sapien sit amet augue aliquam, at auctor purus mattis [CITE(28)].',
                    'content_pre': 'Fusce gravida iaculis diam eget tincidunt. Donec vitae nisl iaculis'}
        
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

        if not d_outline: return

        title = next(iter(d_outline))
        abstract_section_header = findAbstractSection(d_outline)

        attached_references = {str(k): v for k, v, _ in attached_references}
        
        len_last_content_pre, content_pre_new = 0, None
        ref_list = []

        if write_abstract:
            ui.notification_show(f"Writing {abstract_section_header}", type="message")

        is_first_section_to_generate = True
        
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

            if instructions_additional and is_first_section_to_generate:
                instructions += f'\n- {instructions_additional}'
                is_first_section_to_generate = False

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
     
            # During regeneration, we need only a specified number blocks to regenerate. num_blocks_to_generate is needed for that.
            if not (is_gen_needed and (num_blocks_to_generate is None or num_blocks_to_generate > 0)): break
        
            # if attached_references:
            #     response = await dummy(len(ref_list))  
            # else:
            #     response = await dummy()

            if not content_pre_summary: content_pre_summary = '\n\n'.join(content_pre)
            current_section = getSectionText(current_section_list)
            
            response = await agent.ainvoke({'content_pre': content_pre_summary, 
                                            'current_section': current_section,
                                            'content_specific_instructions': instructions})
            
            content, content_pre_summary, concept_map = response['content'], response['content_pre'], response.get('concept_map', {})
            
            attached_references_ai = response.get('references', {})
            attached_references, attached_files_reload_flag_val = getSanitizedReferences(attached_references_ai, attached_references, not attached_files_reload_flag_val)

            insertContent(d_outline, current_section_list, content, content_pre_summary, concept_map)

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

            if num_blocks_to_generate is not None: num_blocks_to_generate -= 1

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
                                             write_abstract=True), 
                            clear=True)
            
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
    
    @reactive.effect
    @reactive.event(input.btn_show_concept_map)
    def showConceptMap():

        m = ui.modal(
            mod_concept_map(id=getUIID('concept_map'), config_app=config_app),
            title="",
            easy_close=True,
            footer=None,
            size='xl'
        )

        ui.modal_show(m)