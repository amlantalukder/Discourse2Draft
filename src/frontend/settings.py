from shiny import reactive
from shiny.express import ui, module
from ..backend.llms import extractAvailableLLMs
from ..backend.architecture import Architecture

@module
def mod_settings(input, output, session, callback_fn, config_app):

    with ui.hold() as content:
        with ui.div(class_='settings'):
            with ui.div(class_='row'):
                with ui.div(class_='col'):
                    ui.h5('Settings')
                with ui.div(class_='col d-flex justify-content-end gap-2'):
                    ui.input_action_button('btn_save_settings', 'Save')
                    ui.input_action_button('btn_close_settings', 'Close')
            ui.tags.hr()
            with ui.div(class_='row justify-content-between'):
                ui.input_selectize('select_llm', 'LLM', choices=extractAvailableLLMs(), selected=config_app.llm)
                ui.input_slider('slide_temp', 'Temperature', min=0, max=1, step=0.1, value=config_app.temperature)
            ui.input_text_area('text_instructions', 'Instructions', value=config_app.instructions)

    @reactive.effect
    @reactive.event(input.btn_save_settings)
    def saveSettings():
        config_app.llm = input.select_llm()
        config_app.temperature = input.slide_temp()
        config_app.instructions = input.text_instructions()
        config_app.agent = Architecture(model_name=config_app.llm, temperature=float(config_app.temperature), instructions=config_app.instructions).agent

        callback_fn()

        ui.notification_show("Settings saved", type="message")

    @reactive.effect
    @reactive.event(input.btn_close_settings)
    def close():
        print('closing')
        ui.modal_remove()

    return content