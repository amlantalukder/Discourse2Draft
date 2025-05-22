from shiny import ui as core_ui, reactive
from shiny.express import ui, module
from src.llms import extractAvailableLLMs
from src.architecture import Architecture
from app_defaults import ConfigApp

def showDialog(ui_content):

    m = ui.modal(
        ui_content,
        title="",
        easy_close=False,
        footer=None,
        size='l'
    )

    ui.modal_show(m)

@module
def mod_settings(input, output, session, callback_fn, config_app):

    ui_content = core_ui.div(
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
            core_ui.input_selectize('select_llm', 'LLM', choices=extractAvailableLLMs(), selected=config_app.llm),
            core_ui.input_slider('slide_temp', 'Temperature', min=0, max=1, step=0.1, value=config_app.temperature),
            class_='row justify-content-between'
        ),
        core_ui.input_text_area('text_instructions', 'Instructions', value=config_app.instructions),
        class_='settings'
    )

    @reactive.effect
    @reactive.event(input.btn_save_settings, ignore_init=True)
    def saveSettings():
        config_app.llm = input.select_llm()
        config_app.temperature = input.slide_temp()
        config_app.instructions = input.text_instructions()
        config_app.agent = Architecture(model_name=config_app.llm, temperature=config_app.temperature, instructions=config_app.instructions).agent

        callback_fn()

        ui.notification_show("Settings saved", type="message")

    @reactive.effect
    @reactive.event(input.btn_close_settings, ignore_init=True)
    def close():
        ui.modal_remove()

    return ui_content