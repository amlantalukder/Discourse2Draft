from shiny import reactive, ui as core_ui, render as core_render
from shiny.express import ui, render, input, session, module
import faicons
from pathlib import Path
from src.llms import extractAvailableLLMs
from src.architecture import Architecture
import asyncio
import json

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
instructions = '''\
    The user will input an outline for a manuscript on a specific topic. You are a scholarly ghost‑writer with a PhD in that topic area. Your task is to convert a detailed, hierarchically coded outline into polished manuscript prose. Follow the following global constraints for every section you draft.
 
    **Voice & register**
    
    - Doctoral‑level, formal scientific style (as in a peer‑reviewed journal).
    - Integrate definitions, mechanisms, empirical findings and theoretical nuance as appropriate.
    - Write at great enough depth that the reader will fully understand the various aspects of the sub section, but avoid being overly redundant with other sections.
    
    **Form**

    - Only paragraphs — no headings, no numbering, no bullet points, no embedded outline codes.
    - You may use multiple paragraphs if needed to cover the content deeply and coherently.
    
    **Use of outline**
    
    - Each outline line is structured as “<alphanumeric code> -> <level‑1 topic> -> <level‑2 topic> -> …”.
    - Begin every new answer by quoting, verbatim, the last ontological branch term (i.e, only the text after the last sequential “ -> ”) that you are expanding. For example,  if the outline section heading you are working on is “<alphanumeric code> -> <level‑1 topic> -> <level‑2 topic> you would only quote <level‑2 topic> with its alphanumeric designation
    - Treat higher‑level nodes as contextual background, lower‑level nodes as focal content.
    - Avoid repeating detailed explanations already supplied for earlier sections unless essential for clarity; instead, use concise forward/backward references if necessary.
    - Confidence scoring: For each factual statement generated, include a confidence score between 1-10 (1 being the lowest and 10 being the highest) in the form of “(CS= [score])”. This score should reflect the level of scientific consensus or evidence supporting the statement, with 1 indicating speculative or weakly supported claims and 10 indicating well-established facts.),

    **Writing Depth and Style**
    
    - Where deemed necessary to illustrate a point/provide clarity, employ specific/detailed examples that help the reader better understand critical concepts.
    - When responding your sole values should be scientific accuracy, application of rigorous scientific reasoning, and material reasoning/rationality.
    - Identify hidden biases in your answer and correct them.
    '''

agent = Architecture(model_name=llm, temperature=temperature, instructions=instructions).agent

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
            core_ui.input_select('select_llm', 'LLM', choices=extractAvailableLLMs(), selected=llm),
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
            with ui.div(class_='row', style='font-size: 0.8em !important'):
                with ui.div(class_='col'):
                    ui.input_checkbox('chk_example', 'Use example', value=False)
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

@reactive.effect
@reactive.event(input.btn_save_settings)
def openSettings():
    global llm, temperature, instructions, agent
    llm = input.select_llm()
    temperature = input.slide_temp()
    instructions = input.text_instructions()
    agent = Architecture(model_name=llm, temperature=temperature, instructions=instructions).agent

    ui.notification_show("Settings saved", type="message")

@reactive.effect
@reactive.event(input.btn_close_settings)
def closeSettings():
    ui.modal_remove()

@reactive.effect
@reactive.event(input.chk_example)
def useExample():
    example = '''\
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
    <content>
    '''
    if not input.chk_example(): example = ''
    ui.update_text_area('txt_outline', value=example)
    

async def getResponse(sts):
    contents = []
    flag_first = True
    for st in sts:
        st_elements = st.split(' -> ')
        if flag_first: 
            section_headers = '\n'.join([f'{'#' * (i+1)} {v}' for i, v in enumerate(st_elements)]) + '\n'
        else:
            section_headers = f'{'#' * len(st_elements)} {st_elements[-1]}\n'
        flag_first = False
        contents.append(section_headers)
        yield section_headers
        
        response = await agent.ainvoke({'current_section': st}, {"configurable": {"thread_id": "abc123"}})
        response = response['response']
        
        print(response)
        response = list(response.values())[0]
        contents.append(response)
        
        tokens = response.split(' ')

        for i, s in enumerate(tokens):
            await asyncio.sleep(0.1 if not write_faster else 0.01)
            yield s + ' ' if i < len(tokens)-1 else s + '\n'

        with open(f'data/manuscript_{session.id}.md', 'a') as f:
            f.write('\n'.join(contents)+'\n')
            ui.notification_show("Progress saved", type="message")
            contents = []

def saveOutline():

    outline = input.txt_outline().strip()
    if outline == '': return False
    
    output, lines = [], []
    for x in outline.split('<content>'):
        x = x.strip()
        if not x: continue
        for line_x in x.split('\n'):
            line_x = line_x.strip()
            if not line_x: continue
            hashes = line_x.split()[0]
            text = ' '.join(line_x.split()[1:])

            if hashes != '#' * len(hashes):
                ui.notification_show("Each line in the outline must start with '#'s followed by a space or have the '<content>' tag", type="error")
                return False
            
            if len(hashes) > len(lines) + 1:
                ui.notification_show(f"Expected no more than {len(lines) + 1} '#'s before {text}", type="error")
                return False
            
            if len(hashes) <= len(lines):
                lines = lines[:len(hashes)-1]

            lines.append(text)

        output.append(' -> '.join(lines))
    
    with open(f'data/outline_{session.id}.txt', 'w') as fp:
        fp.write('\n'.join(output))
    
    return True

@reactive.effect
@reactive.event(input.btn_generate)
async def start():

    if not saveOutline(): return

    with open(f'data/outline_{session.id}.txt') as f:
        sts = [st.strip() for st in f.readlines() if st.strip() != '']

    await stream.stream(getResponse(sts), clear=True)

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