from dash.dash import Dash
from dash_bootstrap_components.themes import GRID, BOOTSTRAP

from smoof.layout import serve_layout
from smoof.callbacks import (
    set_callback_load_df,
    set_callback_var_vizs_interactivity
)
from smoof.cache import create_cache

def get_app() -> Dash:

    app = Dash(
        __name__,
        external_stylesheets=[GRID, BOOTSTRAP],
        external_scripts=[
            'layout.py', 'callbacks.py', 'load.py', 'identify_var_type.py',
            'var_viz.py', 'cache.py', 'filter.py'
            ],
        suppress_callback_exceptions=True
        )
    cache = create_cache(app)
    
    app.layout = serve_layout

    set_callback_load_df(app, cache)
    set_callback_var_vizs_interactivity(app, cache)

    return app

def main() -> None:

    app = get_app()
    app.run_server()

if __name__ == '__main__':

    main()
