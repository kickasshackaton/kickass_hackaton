from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    Target,
    User
    )

def site_layout():
    renderer = get_renderer("templates/main.pt")
    layout = renderer.implementation().macros['layout']
    return layout

@view_config(route_name='home', renderer='templates/courses.pt')
def home(request):

    try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
        targets = DBSession.query(User).filter(User.id == request.matchdict["id"]).all()[0].my_targets
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'layout' : site_layout(),'targets' : targets}

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_kickass_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

