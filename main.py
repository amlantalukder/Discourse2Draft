from shiny.express import wrap_express_app
from pathlib import Path

app = wrap_express_app(Path('app.py'))
    