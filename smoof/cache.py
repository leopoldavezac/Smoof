from flask_caching import Cache

from dash import Dash


def create_cache(app:Dash) -> Cache:

    return Cache(
        app.server,
        config={
            'CACHE_TYPE': 'filesystem',
            'CACHE_DIR': 'cache-directory',
            'CACHE_THRESHOLD': 200
            }
        )