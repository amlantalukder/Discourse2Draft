from shiny import reactive
from shiny.express import ui, module, render
import faicons
from utils import print_func_name, Config, getUIID
from ..backend.ai.llms import extractAvailableLLMs
from ..backend.ai.architecture import Architecture

@module
def tocLink(input, output, session, header, children, level):

    is_expanded = reactive.value(False)

    with ui.hold() as content:
        with ui.div(class_='ms-4' if level > 0 else ''):
            @render.express
            def renderExpandShrink():
                
                if not children:
                    ui.HTML(f'<a href="#:~:text={header}" style="text-decoration:none">{header}</a>')
                    return
                
                if is_expanded.get():
                    with ui.div(class_='d-flex justify-content-between'):
                        ui.HTML(f'<a href="#:~:text={header}" style="text-decoration:none">{header}</a>')
                        ui.input_action_link(id="expand_shrink", label="", icon=faicons.icon_svg("caret-down"))
                    children
                else:
                    with ui.div(class_='d-flex justify-content-between'):
                        ui.HTML(f'<a href="#:~:text={header}" style="text-decoration:none">{header}</a>')
                        ui.input_action_link(id="expand_shrink", label="", icon=faicons.icon_svg("caret-right"))

    @reactive.effect
    @reactive.event(input.expand_shrink)
    def expandOrShrink():
        is_expanded.set(not is_expanded.get())
    
    return content

@module
def mod_about(input, output, session):

    with ui.hold() as content:
        with ui.layout_sidebar():
            with ui.sidebar():
                with ui.div(class_='border rounded toc-container'):
                    @render.ui
                    @print_func_name
                    def renderSections():
                        return extractOutlineSections()
                    
            with ui.div(class_='text-container'):
                @render.express
                @print_func_name
                def renderAboutText():
                    txt = '\n'.join(loadText())
                    txt = txt.replace('./www/assets/', '/assets/')
                    ui.markdown(txt)

    @reactive.calc
    @print_func_name
    def loadText():
        about_text = []
        with open(Config.DIR_HOME / 'docs' / 'README.md') as fp:
            about_text = fp.readlines()
        return about_text
    
    @reactive.calc
    @print_func_name
    def extractOutlineSections():
        @print_func_name
        def getOutlineHierarchy(d, level=0):

            if not d: return
            
            return [tocLink(id = getUIID(f'toc{level}'),
                            header = k, 
                            children = getOutlineHierarchy(d[k], level=level+1),
                            level = level) for k in d]
        
        @print_func_name
        def insertOutline(d, outline_items):

            if len(outline_items) == 1:
                return {outline_items[0]: {}}
            
            if outline_items[0] not in d:
                d[outline_items[0]] = {}
            
            d[outline_items[0]] |= insertOutline(d[outline_items[0]].copy(), outline_items[1:])

            return d
        
        outline_sections = []

        about_text = loadText()
        outline_items = []
        d_outline = {}
        for line_x in about_text:

            line_x = line_x.strip()

            if not line_x.startswith('#'): continue
            
            hashes = line_x.split()[0]
            header = ' '.join(line_x.split()[1:])
            
            if len(hashes) == 1:
                if d_outline: outline_sections += getOutlineHierarchy(d_outline)
                d_outline = {}
                outline_items = []
            
            if hashes != '#' * len(hashes):
                print(f'Invalid header: {line_x}')
                break
            
            if len(hashes) > len(outline_items) + 1:
                print(f'Invalid number of "#"s in the header, expected number of hashes <= {len(outline_items) + 1}, found {len(hashes)}')
                break
            
            if len(hashes) <= len(outline_items):
                outline_items = outline_items[:len(hashes)-1]
                
            outline_items.append(header)
            d_outline = insertOutline(d_outline.copy(), outline_items)

        if d_outline: outline_sections += getOutlineHierarchy(d_outline)
                                      
        return outline_sections
    
    return content
