from shiny import reactive
from shiny.express import ui, render, module
import faicons
from utils import Config, getUIID, print_func_name
from ..backend.ai.architecture import Architecture
from ..backend.db import insertIntoDB, updateDB, selectFromDB, \
                generated_files_status, \
                generated_files_ai_architecture, \
                vector_db_collections_type, \
                vector_db_collections_status
from .manage_outline import processOutline, getRawOutline, getOutlineHierarchyList, mod_outline_manager, mod_ai_outline_creator
from .sidebar_modules.sidebar import mod_sidebar
from .common import initProfile, getFileType, getFileTypeIcon, getVectorDBFiles, detachDocs, getDocContent, createVectorDBCollection
import asyncio
import json
import textwrap
import re
from datetime import datetime
from rich import print
import io

@module
def mod_contents(input, output, session, config_app, 
                 outline_from_outline_manager,
                 reload_content_view_flag, 
                 reload_rag_and_ref_flag, 
                 reload_generated_docs_view_flag, 
                 file_change_flag,
                 settings_changed_flag):

    show_outline = reactive.value(True)
    references = reactive.value([])

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
                        ui.input_checkbox('chk_use_example', 'Use example', value=False)            
                    with ui.div(class_='d-flex flex-column col text-center'):
                        @render.ui
                        @print_func_name
                        def renderLLMandTemp():
                            _ = reload_content_view_flag(), settings_changed_flag()
                            return [ui.span(f'LLM: {config_app.llm}, Temperature: {config_app.temperature}'),
                                    ui.span('(Can be changed in the settings panel in the top-right corner)')]
                    with ui.div(class_='col text-end'):
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
                    def showDownloadOptions():
                        _ = reload_content_view_flag()
                        if not config_app.file_name: return
                        with ui.tooltip(placement="right"):
                            with ui.div():
                                with ui.popover(placement='bottom', options={'trigger': 'focus'}):
                                    ui.input_action_button('btn_download', '', icon=faicons.icon_svg("download"))
                                    with ui.div(class_='d-flex flex-column gap-2'):
                                        @render.express
                                        def renderDownloadOption():
                                            attached_files, file_info = applyGetVectorDBFiles()
                                            _ = reload_content_view_flag()
                                            outline_file_path = Config.DIR_DATA / f'outline_{config_app.generated_files_id}.json'
                                            if not outline_file_path.exists(): return
                                            content_md, content_docx, content_tex, bibs = getDocContent(file_id=config_app.generated_files_id, attached_files=attached_files, file_info=file_info)

                                            @render.download(label=ui.div('Content (.md)', faicons.icon_svg("download"), class_='d-flex justify-content-between align-items-center gap-1'), filename='content.md')
                                            @print_func_name
                                            async def renderDownloadContentMD():
                                                yield content_md

                                            @render.download(label=ui.div('Content (.docx)', faicons.icon_svg("download"), class_='d-flex justify-content-between align-items-center gap-1'), filename='content.docx')
                                            @print_func_name
                                            async def renderDownloadContentDocx():
                                                docx_buffer = io.BytesIO()
                                                content_docx.save(docx_buffer)
                                                docx_buffer.seek(0)

                                                yield docx_buffer.read()

                                            @render.download(label=ui.div('Content (.tex)', faicons.icon_svg("download"), class_='d-flex justify-content-between align-items-center gap-1'), filename='content.tex')
                                            @print_func_name
                                            async def renderDownloadContentTex():
                                                yield content_tex
                                                    
                                            if bibs:
                                                @render.download(label=ui.div('Bibliography', faicons.icon_svg("download"), class_='d-flex justify-content-between align-items-center gap-1'), filename='bibliography.bib')
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
                        files, _ = applyGetVectorDBFiles()
                        
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

    @reactive.effect
    @reactive.event(reload_content_view_flag, ignore_init=True)
    @print_func_name
    def reloadContentView():
    
        file_change_flag.set(not file_change_flag.get())
        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())

    @reactive.effect
    @reactive.event(input.switch_show_lit_research, ignore_init=True)
    @print_func_name
    def enableLitResearch():
        
        if not config_app.generated_files_id:
            ui.notification_show("Please create a new file or select an existing file.", type="error")
            return
        
        if not input.switch_show_lit_research():
            if config_app.vector_db_collections_id_lit_search:
                detachDocs(config_app.generated_files_id, config_app.vector_db_collections_id_lit_search)
                config_app.vector_db_collections_id_lit_search = None
            return
        
        if config_app.vector_db_collections_id_lit_search: return

        current_time = datetime.now()

        # Reuse deleted literature type collections
        records = selectFromDB(table_name='vector_db_collections',
                                field_names=['generated_files_id', 'type'], 
                                field_values=[[config_app.generated_files_id], [vector_db_collections_type.LITERATURE.value]],
                                order_by_field_names=['update_date'],
                                order_by_types=['DESC'],
                                limit=1)
        
        if not records.empty:
            vector_db_collections_id = records['id'].iloc[0]
            updateDB(table_name='vector_db_collections', 
                    update_fields=['status', 'update_date'], 
                    update_values=[vector_db_collections_status.ACTIVE.value, current_time], 
                    select_fields=['id'], 
                    select_values=[[vector_db_collections_id]])
        else:
            ids = insertIntoDB(table_name='vector_db_collections', 
                        field_names=['email', 'session', 'generated_files_id', 'type', 'status', 'create_date', 'update_date'],
                        field_values=[[config_app.email], [config_app.session_id], [config_app.generated_files_id],
                                    [vector_db_collections_type.LITERATURE.value], 
                                    [vector_db_collections_status.ACTIVE.value], 
                                    [current_time], [current_time]])
            vector_db_collections_id = ids[0]
        
        vector_db_collection_name_lit_search = f'{Config.APP_NAME_AS_PREFIX}_collection_{vector_db_collections_id}'
        createVectorDBCollection(collection_name=vector_db_collection_name_lit_search)

        ai_architecture = generated_files_ai_architecture.RAG.value

        updateDB(table_name='generated_files', 
                update_fields=['ai_architecture', 'update_date'], 
                update_values=[ai_architecture, current_time], 
                select_fields=['id'], 
                select_values=[[config_app.generated_files_id]])

        if config_app.vector_db_collections_id:
            vector_db_collection_name = f'{Config.APP_NAME_AS_PREFIX}_collection_{config_app.vector_db_collections_id}'
        else:
            vector_db_collection_name = ''

        config_app.vector_db_collections_id_lit_search = vector_db_collections_id
        config_app.agent = Architecture(model_name=config_app.llm, 
                                        temperature=config_app.temperature, 
                                        instructions=config_app.instructions, 
                                        type=ai_architecture,
                                        collection_name= vector_db_collection_name,
                                        collection_name_lit_search=vector_db_collection_name_lit_search).agent

    @reactive.calc
    @reactive.event(reload_rag_and_ref_flag)
    @print_func_name
    def applyGetVectorDBFiles():

        files, file_info = [], {}
        if config_app.vector_db_collections_id is not None:
            refs, uploaded_file_info = getVectorDBFiles(config_app.vector_db_collections_id)
            files += refs
            file_info |= uploaded_file_info
        if config_app.vector_db_collections_id_lit_search is not None:
            refs, literature_info = getVectorDBFiles(config_app.vector_db_collections_id_lit_search)
            files += refs
            file_info |= literature_info

        return files, file_info
    
    @reactive.effect
    @reactive.event(input.btn_delete_rag)
    @print_func_name
    def applyDetachDocs():

        detachDocs(config_app.generated_files_id, config_app.vector_db_collections_id)
        config_app.vector_db_collections_id = None
        reload_rag_and_ref_flag.set(not reload_rag_and_ref_flag.get())
        
    @reactive.effect
    @reactive.event(file_change_flag)
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

        raw_outline = '\n'.join(getRawOutline(d_outline))
        
        # Cancel writing
        stream.latest_stream.cancel()

        # Show file name, outline and content
        ui.update_text(id='text_file_name', value=config_app.file_name)
        ui.update_text_area(id='text_outline', value=raw_outline)

        references.set([])
        attached_references, _ = applyGetVectorDBFiles()
        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, 
                                                        outline_file_path, 
                                                        write_n_contents=0, 
                                                        attached_references=attached_references), 
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

        raw_outline = '\n'.join(getRawOutline(d_outline))
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

        references.set([])
        attached_references, _ = applyGetVectorDBFiles()
        loop = asyncio.get_event_loop()
        loop.create_task(stream.stream(generateResponse(d_outline, 
                                                        outline_file_path,
                                                        write_n_contents=1,
                                                        attached_references=attached_references), 
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
    async def generateResponse(d_outline, outline_file_path, write_n_contents=-1, attached_references=[]):

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
            d_outline[top_level_key]['References'] = [('ref', f'{v}') for v in enumerate(ref_list)]

        @print_func_name
        def processCitation(content, ref_list, attached_references):

            ref_groups = re.findall(r'\[CITE\((.+?(,\ ?.+?)*)\)\]', content)
    
            refs_seen = set()
            d_ref = {}
            for refs, _ in ref_groups:
                if refs in refs_seen: continue
                refs_seen.add(refs)
                for ref in refs.split(','):
                    ref = ref.strip()
                    if ref not in attached_references: continue
                    if ref in d_ref: continue
                    try:
                        d_ref[ref] = ref_list.index(attached_references[ref]) + 1
                    except ValueError:
                        ref_list.append(attached_references[ref])
                        d_ref[ref] = len(ref_list)
            
                ref_links = sorted([d_ref[ref.strip()] for ref in refs.split(',') if ref in d_ref])
                content = content.replace(f'[CITE({refs})]', f'[{', '.join([f'<a href="#:~:text=References">{ref_cite}</a>' for ref_cite in ref_links])}]')
        
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
        attached_references = {str(k): v for k, v, _ in attached_references}
        while True:

            content_pre, current_section_list, is_gen_needed = getHierarchy(d_outline)
            
            current_section = getSectionText(current_section_list)

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

            yield content_pre_new
            
            if write_n_contents == 0 or not is_gen_needed: break
        
            # if attached_references:
            #     response = await dummy(len(ref_list))  
            # else:
            #     response = await dummy()
            response = await config_app.agent.ainvoke({'content_pre': '\n\n'.join(content_pre), 'current_section': current_section}, {"configurable": {"thread_id": "abc123"}})
            
            content = response['content']
            attached_references = response.get('references', {})

            print(content)

            insertContent(d_outline, current_section_list, content)
            if attached_references:
                response_with_citations, ref_list = processCitation(content, ref_list, attached_references)
                references.set(ref_list.copy())
                await reactive.flush()
                insertReferences(d_outline, ref_list)
                tokens = response_with_citations.split(' ')
            else:
                tokens = content.split(' ')

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
        attached_references, _ = applyGetVectorDBFiles()
        await stream.stream(generateResponse(d_outline, 
                                             outline_file_path,
                                             attached_references=attached_references), 
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
            
            loop = asyncio.get_event_loop()
            loop.create_task(session.send_custom_message('reload_content', {'ui_id': 'main-contents'}))

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

    return content