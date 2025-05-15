from shiny import reactive, ui as core_ui, render as core_render
from shiny.express import ui, render, input, session, module
import faicons
from pathlib import Path
from src.llms import extractAvailableLLMs
from src.architecture import Architecture
import asyncio
import json
import textwrap
import os
from posit import connect

client = connect.Client()
print(client.users.find(prefix='Amlan'))

# @reactive.calc
# def visitor_client():
#     ## read the user session token and generate a new client
#     user_session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
#     print('env', os.getenv("CONNECT_CONTENT_SESSION_TOKEN"))
#     print('env', os.getenv("CONTENT_SESSION_TOKEN"))
#     return client.with_user_session_token(user_session_token)

# @render.text
# def user_profile():
#     # fetch the viewer's profile information
#     return visitor_client().me

class TreeNode:
    def __init__(self, text = ''):
        self.text = text
        self.children = []

stream = ui.MarkdownStream("stream")
st_tree = TreeNode()

ui.include_css(Path(__file__).parent / "css" / "bootstrap.css", method='link_files')
ui.include_css(Path(__file__).parent / "css" / "bootstrap.min.css", method='link_files')
ui.include_css(Path(__file__).parent / "css" / "custom.css", method='link_files')

ui.page_opts(title="", fillable=True)

counter = reactive.value(-1)
write_faster = False

llm = 'azure-o1-mini'
temperature = 0
instructions = textwrap.dedent('''\
    The user will input an outline for a manuscript on a specific topic. You are a scholarly ghost‑writer with a PhD in that topic area. Your task is to convert a detailed, hierarchically coded outline into polished manuscript prose. Follow the following global constraints for every section you draft.
 
    **Your writing must be consistent with previous section**

    **Voice & register**
    
    - Doctoral‑level, formal scientific style (as in a peer‑reviewed journal).
    - Integrate definitions, mechanisms, empirical findings and theoretical nuance as appropriate.
    - Write at great enough depth that the reader will fully understand the various aspects of the sub section, but avoid being overly redundant with other sections.
    
    **Form**

    - Only paragraphs — no headings, no numbering, no bullet points, no embedded outline codes.
    - You may use multiple paragraphs if needed to cover the content deeply and coherently.
    
    **Use of outline**
    
    - Each outline line is structured as “<alphanumeric code> -> <level‑1 topic> -> <level‑2 topic> -> …”.
    - Treat higher‑level nodes as contextual background, lower‑level nodes as focal content.
    - Avoid repeating detailed explanations already supplied for earlier sections unless essential for clarity; instead, use concise forward/backward references if necessary.
    - Confidence scoring: For each factual statement generated, include a confidence score between 1-10 (1 being the lowest and 10 being the highest) in the form of “(CS= [score])”. This score should reflect the level of scientific consensus or evidence supporting the statement, with 1 indicating speculative or weakly supported claims and 10 indicating well-established facts.),

    **Writing Depth and Style**
    
    - Where deemed necessary to illustrate a point/provide clarity, employ specific/detailed examples that help the reader better understand critical concepts.
    - When responding your sole values should be scientific accuracy, application of rigorous scientific reasoning, and material reasoning/rationality.
    - Identify hidden biases in your answer and correct them.''')

agent = Architecture(model_name=llm, temperature=temperature, instructions=instructions).agent

settings_flag = reactive.value(True)

def mod_settings():

    return core_ui.div(
        core_ui.div(
            core_ui.div(
                core_ui.h5("Settings"),
                class_='col'
            ),
            core_ui.div(
                core_ui.input_action_button('btn_save_settings', 'Save'),
                core_ui.input_action_button('btn_close_settings', 'Close'),
                class_='col d-flex justify-content-end gap-2'
            ),
            class_='row'
        ),
        core_ui.tags.hr(),
        core_ui.div(
            core_ui.input_selectize('select_llm', 'LLM', choices=extractAvailableLLMs(), selected=llm),
            core_ui.input_slider('slide_temp', 'Temperature', min=0, max=1, step=0.1, value=temperature),
            class_='row justify-content-between'
        ),
        core_ui.input_text_area('text_instructions', 'Instructions', value=instructions),
        class_='settings'
    )

with ui.div(class_="app-container"):
    with ui.div(class_='row title-bar'):
        with ui.div(class_='col'):
            ui.h4('AI Word processor')
        with ui.div(class_='col d-flex justify-content-end'):
            ui.input_action_button('btn_settings', '', icon=faicons.icon_svg("gear"))
    with ui.div(class_='row input'):
        with ui.div(class_='col'):
            with ui.div(class_='row justify-content-between', style='font-size: 0.8em !important'):
                with ui.div(class_='col'):
                    ui.input_checkbox('chk_example', 'Use example', value=False)
                with ui.div(class_='col'):
                    @render.express
                    def showLLMandTemp():
                        llm, temp = getLLMandTemp()
                        ui.span(f'LLM: {llm}, Temperature: {temp}')
                with ui.div(class_='col text-end'):
                    ui.p("(Drag the text area from the bottom right corner to show more text)")
            ui.input_text_area('txt_outline', '', placeholder='''Write an outline...''', rows=7, width='100%')
        with ui.div(class_='col-auto d-flex justify-content-around align-items-end p-3'):
            with ui.div(class_='row flex-column gap-2'):
                ui.input_action_button('btn_generate', '', icon=faicons.icon_svg("play"))
                ui.input_action_button('btn_stop', '', icon=faicons.icon_svg("stop"))
                ui.input_action_button('btn_speed', '', icon=faicons.icon_svg("person-running"))

                @render.download(label=faicons.icon_svg("download"), filename='manuscript.md')
                async def downloadDoc():
                    doc_path = Path(f'data/manuscript_{session.id}.md')
                    if not doc_path.exists(): return
                    with open(doc_path) as f:
                        for l in f.readlines():
                            yield l
                
    with ui.div(class_='row content'):
        stream.ui(content=core_ui.p('Content starts here ...', class_='mt-3'), width='100%')

@reactive.effect
@reactive.event(input.btn_settings)
def openSettings():
    m = ui.modal(
        mod_settings(),
        title="",
        easy_close=False,
        footer=None,
        size='l'
    )
    ui.modal_show(m)

@reactive.calc()
@reactive.event(settings_flag)
def getLLMandTemp():
    return llm, temperature

@reactive.effect
@reactive.event(input.btn_save_settings)
def saveSettings():
    global llm, temperature, instructions, agent
    llm = input.select_llm()
    temperature = input.slide_temp()
    instructions = input.text_instructions()
    settings_flag.set(not settings_flag.get())
    agent = Architecture(model_name=llm, temperature=temperature, instructions=instructions).agent

    ui.notification_show("Settings saved", type="message")

@reactive.effect
@reactive.event(input.btn_close_settings)
def closeSettings():
    ui.modal_remove()

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
    ui.update_text_area('txt_outline', value=example)

def saveOutline():

    outline = input.txt_outline().strip()
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

    def insertOutline(d, outline_items):

        if len(outline_items) == 1:
            d['content'] = d.get('content', []) + outline_items
            return d
        
        if outline_items[0] not in d:
            d[outline_items[0]] = {}
        
        d[outline_items[0]] = insertOutline(d[outline_items[0]].copy(), outline_items[1:])

        return d
    
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
    
    with open(f'data/outline_{session.id}.json', 'w') as fp:
        json.dump(d_outline, fp)
    
    return True

async def generateResponse(d_outline):

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
    
        response = await agent.ainvoke({'content_pre': '\n\n'.join(content_pre), 'current_section': current_section}, {"configurable": {"thread_id": "abc123"}})
        
        response = response['response']
        #response = 'dummy ai'

        insertContent(d_outline, current_section_list, response)
        
        print(response)
        
        tokens = response.split(' ')

        for i, s in enumerate(tokens):
            await asyncio.sleep(0.1 if not write_faster else 0.01)
            yield s + ' ' if i < len(tokens)-1 else s + '\n\n'

        with open(f'data/manuscript_{session.id}.md', 'a') as f:
            f.write(section_header + response + '\n\n')
            ui.notification_show("Progress saved", type="message")

@reactive.effect
@reactive.event(input.btn_generate)
async def start():

    if not saveOutline(): return

    with open(f'data/outline_{session.id}.json') as fp:
        #sts = [st.strip() for st in f.readlines() if st.strip() != '']
        d_outline = json.load(fp)
    
    await stream.stream(generateResponse(d_outline), clear=True)

@reactive.effect
@reactive.event(input.btn_stop)
def stop():
    stream.latest_stream.cancel()
    ui.notification_show("Writing stopped", type="warning")

@reactive.effect
def _():
    ui.update_action_button(
        "btn_stop", disabled=stream.latest_stream.status() != "running"
    )

@reactive.effect
@reactive.event(input.btn_speed)
def speed():
    global write_faster
    write_faster = not write_faster
    ui.update_action_button(
        "btn_speed", icon=faicons.icon_svg("person-running" if write_faster else "person-walking")
    )