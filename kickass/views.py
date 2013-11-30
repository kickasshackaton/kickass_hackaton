from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from sqlalchemy.exc import DBAPIError
from datetime import datetime
from urllib.parse import urlsplit
from os import path


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

def parse_coursera_api(url):
    mypath = urlsplit(url)[2]
    mypath = "/"+mypath
    url = path.basename(mypath)
    return url


@view_config(route_name='home', renderer='templates/courses.pt')
def home(request):

    try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
        targets = DBSession.query(User).filter(User.id == request.matchdict["id"]).first().my_targets#.filter(Target.type=="coursera_course").all()
        list_users = DBSession.query(User).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'layout' : site_layout(),'targets' : targets, 'list_users' : list_users}

@view_config(route_name='home_default', renderer='templates/courses.pt')
def home_default(request):

    try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
        targets = DBSession.query(User).filter(User.id == 1).first().my_targets#.filter(Target.type=="coursera_course").all()
        list_users = DBSession.query(User).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'layout' : site_layout(),'targets' : targets, 'list_users' : list_users}

@view_config(route_name='list_users', renderer='json')
def list_users(request):
    user_list = DBSession.query(User).all()
    return {"user_list": user_list} #{"list_users" : user_list}

@view_config(route_name='check_target', renderer='json')
def check_target(request):

    # in user_id , url from coursera
    # out Target or False
    #  TODO for any target add code

    if(request.method == "GET"):
        if request.GET["url"] and ("coursera" in request.GET["url"]):
            coursera_id=parse_coursera_api(request.GET["url"])
            user_to_look= DBSession.query(User).filter(User.id == request.GET["user_id"]).first()
            #target_to_look = user_to_look.my_targets.filter(Target.url == coursera_id).first() #TODO filter to InstrumentedList
            for target in user_to_look.my_targets:
                
            target_to_look = user_to_look.my_targets[0]
            if(target_to_look):
                return {"target" : target_to_look}
            else:
                return {"result" : False}
        else: ## IT IS NOT COURSeRAAAAAAAAA TODO
            user_to_look= DBSession.query(User).filter(User.id == request.GET["user_id"]).first()
            target_to_look = user_to_look.my_targets.filter(Target.url == request.GET["url"]).first()
            if(target_to_look):
                return {"target" : target_to_look}
            else:
                return {"result" : False}
    else:
        return {"result" : False}



@view_config(route_name='add_target', renderer='json')
def add_target(request):
    if(request.method == "POST"):
        if(request.POST["type"]):
            new_target = Target(
                name=request.POST["name"],
                deadline=datetime.fromtimestamp(12345566),
                bid=request.POST["bid"],
                url=request.POST["url"]
            )
            new_target.type = request.POST["type"]
        else:
            new_target = Target(
                name=request.POST["name"],
                deadline=datetime.fromtimestamp(12345566),#TODO parse from coursera
                bid=request.POST["bid"],
                url=parse_coursera_api(request.POST["url"])
            )
        DBSession.add(new_target)
        new_target.user = DBSession.query(User).filter(User.id == request.POST["user"]).first()
        new_target.overseer = DBSession.query(User).filter(User.id == request.POST["overseer"]).first()

    return {"Status" : "OK"}





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

