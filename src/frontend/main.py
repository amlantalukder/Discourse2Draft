from shiny import reactive
from shiny.express import ui, render, module
from utils import getUIID, print_func_name
from .contents import mod_contents
from .sidebar_modules.sidebar import mod_sidebar

@module
def mod_main(input, output, session, config_app, reload_view_flag):

    reload_content_view_flag = reactive.value(True)
    reload_content_attached_files_view_flag = reactive.value(True)
    reload_generated_docs_view_flag = reactive.value(True)
    reload_uploaded_docs_view_flag = reactive.value(True)

    with ui.div(class_='app-body-container'):
        with ui.layout_sidebar():
            with ui.sidebar(id='sidebar_docs', position="left", open='open', bg="#f8f8f8", width=400):
                @render.express
                @print_func_name
                def renderSideBar():
                    mod_sidebar(id=getUIID('sidebar'), 
                                config_app=config_app, 
                                reload_content_view_flag=reload_content_view_flag,
                                reload_content_attached_files_view_flag = reload_content_attached_files_view_flag, 
                                reload_generated_docs_view_flag=reload_generated_docs_view_flag,
                                reload_uploaded_docs_view_flag=reload_uploaded_docs_view_flag)

            with ui.div(class_='app-body'):
                @render.express
                @print_func_name
                def renderView():
                    ui_id = getUIID('contents')
                    mod_contents(ui_id, 
                            config_app=config_app,
                            reload_view_flag=reload_content_view_flag,
                            reload_attached_files_view_flag=reload_content_attached_files_view_flag,
                            reload_generated_docs_view_flag=reload_generated_docs_view_flag,
                            reload_uploaded_docs_view_flag=reload_uploaded_docs_view_flag,
                            ui_id=f'main-{ui_id}')

    @reactive.effect
    @reactive.event(reload_view_flag)
    @print_func_name
    def reloadView():
        reload_content_view_flag.set(not reload_content_view_flag.get())
        reload_generated_docs_view_flag.set(not reload_generated_docs_view_flag.get())
        reload_uploaded_docs_view_flag.set(not reload_uploaded_docs_view_flag.get())         