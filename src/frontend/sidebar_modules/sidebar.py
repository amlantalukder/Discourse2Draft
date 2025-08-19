from shiny import reactive
from shiny.express import ui, module, render
from .generated_docs import mod_generated_docs_view, mod_generated_docs_detailed_view
from .uploaded_docs import mod_uploaded_docs_view
from utils import getUIID, print_func_name

@module
def mod_sidebar(input, output, session, 
                config_app, 
                reload_rag_and_ref_flag, 
                reload_content_view_flag, 
                reload_generated_docs_view_flag, 
                reload_uploaded_docs_view_flag):

    reload_generated_docs_detailed_view_flag = reactive.value(True)

    with ui.hold() as content:
        with ui.div():
            with ui.accordion(id='acc_sidebar', open=['Generated documents', 'Uploaded documents'] if config_app.email != '' else '', multiple=True):
                with ui.accordion_panel('Generated documents'):

                    @render.express
                    @print_func_name
                    def renderGeneratedDocs():
                        mod_generated_docs_view(id=getUIID('generated_docs'), 
                                                config_app=config_app, 
                                                reload_content_view_flag=reload_content_view_flag, 
                                                reload_view_flag=reload_generated_docs_view_flag,
                                                reload_detailed_view_flag=reload_generated_docs_detailed_view_flag)
                            
                with ui.accordion_panel('Uploaded documents'):

                    @render.express
                    @print_func_name
                    def renderUploadedDocs():
                        mod_uploaded_docs_view(id=getUIID('uploaded_docs'), 
                                        config_app=config_app, 
                                        reload_rag_and_ref_flag=reload_rag_and_ref_flag,
                                        reload_view_flag = reload_uploaded_docs_view_flag,
                                        showGeneratedDocsDetailedView=showGeneratedDocsDetailedView)
        
    @print_func_name
    def showGeneratedDocsDetailedView():

        m = ui.modal(
            mod_generated_docs_detailed_view(id=getUIID('generated_docs_detailed'), 
                                              config_app=config_app, 
                                              reload_content_view_flag=reload_content_view_flag,
                                              reload_view_flag=reload_generated_docs_detailed_view_flag,
                                              reload_parent_view_flag=reload_generated_docs_view_flag),
            title="Generated documents",
            easy_close=True,
            footer=None,
            size='xl'
        )

        ui.modal_show(m)
    
    return content