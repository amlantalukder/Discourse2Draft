from shiny import reactive
from shiny.express import ui, module, render
from utils import print_func_name, Config
from ..backend.ai.llms import extractAvailableLLMs
from ..backend.ai.architecture import Architecture

@module
def mod_about(input, output, session):

    dir_about = Config.DIR_DATA / 'about'
    current_page = reactive.value('introduction')

    with ui.hold() as content:
        with ui.layout_sidebar():
            with ui.sidebar():
                ui.input_action_button(id='btn_introduction', label='Introduction')
                ui.input_action_button(id='btn_method', label='Method')

            with ui.div(class_='text-container outline'):
                @render.express
                @print_func_name
                def renderAboutText():
                    about_text = ''
                    with open(dir_about / f'{current_page.get()}.txt') as fp:
                        about_text = fp.read()
                    ui.markdown(about_text)

    @reactive.effect
    @reactive.event(input.btn_introduction)
    @print_func_name
    def setIntroduction():
        current_page.set('introduction')

    @reactive.effect
    @reactive.event(input.btn_method)
    @print_func_name
    def setMethod():
        current_page.set('method')
    
    return content
