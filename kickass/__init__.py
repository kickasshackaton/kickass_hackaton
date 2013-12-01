from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/user/{id}')
    config.add_route('home_default', '/my_courses')
    config.add_route('add_target', '/add_target')
    config.add_route('check_target', '/check_target')
    config.add_route('list_users', '/list_users')
    config.add_route('get_charity_funds','/get_charity_funds')
    config.add_route('get_enrollable','/get_enrollable')
    config.add_route('watched_courses', '/watched_courses')
    config.add_route('readit', '/my_readit')
    config.scan()
    return config.make_wsgi_app()
