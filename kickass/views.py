from datetime import (
    datetime,
    timedelta
    )
from time import time
from urllib.parse import urlsplit
from os import path
from functools import reduce
import urllib.request

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import get_renderer
from sqlalchemy.exc import DBAPIError
from pyramid.httpexceptions import HTTPFound
from bs4 import BeautifulSoup

from .kick import (
    CourseraApi
)
from .models import (
    DBSession,
    Target,
    User,
    charity_funds
    )


def site_layout():
    renderer = get_renderer("templates/main.pt")
    layout = renderer.implementation().macros['layout']
    return layout


def new_target_payment_method():
    renderer = get_renderer("templates/new_target_payment_method.pt")
    layout = renderer.implementation().macros['new_target_payment_method']
    return layout


def parse_coursera_api(url):
    mypath = urlsplit(url)[2]
    mypath = "/"+mypath
    url = path.basename(mypath)
    return url


@view_config(route_name="account", renderer='templates/account.pt')
def account(request):
    if request.method == "GET":
        user = DBSession.query(User).filter(User.id == 1).first() ## TODO Hardcoded user.id
        return {'layout': site_layout(), "user": user, "menu": "account",
                "new_target_payment_method": new_target_payment_method(), "user_savings": user_savings(user.id)}
    else:
        user = DBSession.query(User).filter(User.id == request.POST["user_id"]).first()
        user.money += int(request.POST["money"])
        return {"status": "ok"}


@view_config(route_name='readit', renderer='templates/readit.pt')
def readed(request):
    try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
        targets = DBSession.query(User).filter(User.id == 1).first().my_targets# TODO Hardcoded user.id
        list_users = DBSession.query(User).all()
        out_targets = []
        for target in targets:
            if target.type != "coursera_course":
                out_targets.append(target)
        user = DBSession.query(User).filter(User.id == 1).first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'layout': site_layout(), "user": user, 'targets': out_targets, 'charity_funds': charity_funds,
            'list_overseers': list_users, "menu": "readit", "new_target_payment_method": new_target_payment_method()}


@view_config(route_name='watched_courses', renderer='templates/watched_courses.pt')
def watched_courses(request):
    try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
        targets = DBSession.query(User).filter(User.id == 1).first().overseered_targets
        print(targets)# TODO Hardcoded user.id
        list_users = DBSession.query(User).all()
        user = DBSession.query(User).filter(User.id == 1).first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'layout': site_layout(), 'targets': targets, 'list_users': list_users,
            'list_overseers': list_users, 'charity_funds': charity_funds, "enrollable": get_enrollable_courses(),
            "user": user, "menu": "watched_courses", "new_target_payment_method": new_target_payment_method()}


@view_config(route_name='home', renderer='templates/courses.pt')
def home(request):

    try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
        targets = DBSession.query(User).filter(User.id == request.matchdict["id"]).first().my_targets#.filter(Target.type=="coursera_course").all()
        out_targets = []
        for target in targets:
            if target.type == "coursera_course":
                out_targets.append(target)
        list_users = DBSession.query(User).all()
        list_users = DBSession.query(User).all()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'layout': site_layout(), 'targets': out_targets, 'list_users': list_users,
            'list_overseers': list_users, 'charity_funds': charity_funds, "enrollable": get_enrollable_courses(),
            "menu": "courses", "new_target_payment_method": new_target_payment_method()}


@view_config(route_name='home_default', renderer='templates/courses.pt')
def home_default(request):
    try:
        #one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
        targets = DBSession.query(User).filter(User.id == 1).first().my_targets#.filter(Target.type=="coursera_course").all()
        out_targets = []
        for target in targets:
            if target.type == "coursera_course":
                out_targets.append(target)
        list_users = DBSession.query(User).all()
        user = DBSession.query(User).filter(User.id == 1).first()#TODO hardcoded user.id
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'layout': site_layout(), 'targets': out_targets, 'list_users': list_users,
            'list_overseers': list_users, 'charity_funds': charity_funds, "enrollable": get_enrollable_courses(),
            "user": user, "menu": "courses", "new_target_payment_method": new_target_payment_method()}


@view_config(route_name='list_users', renderer='json')
def list_users(request):
    user_list = DBSession.query(User).all()
    return {"user_list": user_list} #{"list_users" : user_list}

def get_course_deadline(course):
    course['weeks'] = int(course['duration_string'].partition(' ')[0])
    #print("Current course")
    #print("%s %s %s" % (course['start_year'], course['start_month'], course['start_day']))
    if (course['start_day'] is None):
        course['start_day'] = 1

    return datetime(course['start_year'], course['start_month'], course['start_day']) + timedelta(weeks = course['weeks'])

def get_enrolled_course_deadline_by_url(url):
    return get_course_deadline(get_enrolled_course_by_url(url)['course'])

def get_enrolled_course_by_url(url):
    courseraApi = CourseraApi('ilya@nikans.ru','$e(ureP@66')
    listingCombined = courseraApi.listingCombined()
    topics = listingCombined['list2']['topics']
    courses = listingCombined['list2']['courses']
    enrollmentCoursesId = list(map(lambda enrollment:
                    enrollment['course_id']
        ,listingCombined['enrollments']))
    topic = reduce(lambda result, itemKey:
                    topics[itemKey] if topics[itemKey]['short_name'] == url else result
        ,topics, None)

    if topic == None:
        return topic

    return reduce(lambda result, item:
                    {'course' : item, 'topic' : topic} if item['topic_id'] == topic['id'] and item['id'] in enrollmentCoursesId else result
        ,courses, None)

def filter_non_unique_courses(courses):
    unique = []
    result = []

    for course in courses:
        if course['topic_id'] not in unique:
            unique.append(course['topic_id'])
            result.append(course)

    return result

def filter_past_courses(course):
    return course['start_year'] != None and get_course_deadline(course) > datetime.now()


def get_enrollable_courses():
    courseraApi = CourseraApi('ilya@nikans.ru','$e(ureP@66')
    listingCombined = courseraApi.listingCombined()
    topics = listingCombined['list2']['topics']
    courses = filter_non_unique_courses(listingCombined['list2']['courses'])
    courses = filter(filter_past_courses, courses)
    return list(map(lambda item:
                    { "course" : item, "topic": topics[str(item['topic_id'])] }
        ,courses))


@view_config(route_name='check_target', renderer='json')
def check_target(request):

    # in user_id , url from coursera
    # out Target or False
    #  TODO for any target add code

    if(request.method == "GET"):
        if request.GET.has_key("url") and ("coursera" in request.GET["url"]):
            coursera_id=parse_coursera_api(request.GET["url"])
            user_to_look= DBSession.query(User).filter(User.id == request.GET["user_id"]).first()
            #target_to_look = user_to_look.my_targets.filter(Target.url == coursera_id).first()
            target_to_look = False
            for target in user_to_look.my_targets:
                if(target.url == coursera_id):
                    target_to_look = target#user_to_look.my_targets[0]
            #target_to_look = user_to_look.my_targets[0]
            if(target_to_look):
                return {"target" : target_to_look}
            else:
                enroll=get_enrolled_course_by_url(coursera_id)
                #print("Enroll = " + enroll)
                if(enroll != None):
                    return {"enrolled" : True,"result" : False}
                return {"enrolled" : False,"result" : False}
        else: ## IT IS NOT COURSeRAAAAAAAAA TODO
            user_to_look= DBSession.query(User).filter(User.id == request.GET["user_id"]).first()
            #target_to_look = user_to_look.my_targets.filter(Target.url == request.GET["url"]).first() ##
            target_to_look = False
            for target in user_to_look.my_targets:
                if(target.url == request.GET["url"]):
                    target_to_look = target#user_to_look.my_targets[0]
            if(target_to_look):
                return {"target" : target_to_look}
            else:
                return {"result" : False}
    else:
        return {"result" : False}



@view_config(route_name='add_target', renderer='json')
def add_target(request):
    if (request.method == "POST"):#TODO redirect by payment_method
        if (request.POST.has_key("type") and request.POST["type"] != "coursera_course"):

            new_deadline = datetime.fromtimestamp(
                time() + timedelta(days=int(request.POST["deadline_days"])).microseconds)
            new_deadline = datetime.now()
            new_target = Target(
                name=request.POST["name"],
                deadline=new_deadline,
                bid=float(request.POST["bid"]),
                url=request.POST["url"]
            )
            new_target.type = request.POST["type"]
            new_target.charity_type = request.POST["charity_type"]
        else:
            url = parse_coursera_api(request.POST["url"])
            print("BID: " + request.POST["bid"])

            new_target = Target(
                name=get_enrolled_course_by_url(url)["topic"]["name"], #request.POST["name"],
                deadline=get_enrolled_course_deadline_by_url(url),
                bid=float(request.POST["bid"]),
                url=url
            )
            new_target.charity_type = request.POST["charity_type"]
            #new_target.user = DBSession.query(User).filter(User.id == request.POST["user"]).first()
            #new_target.overseer = DBSession.query(User).filter(User.id == request.POST["overseer"]).first()

        # form fields
        # name charity_type overseer bid
        DBSession.add(new_target)
        new_target.user = DBSession.query(User).filter(User.id == request.POST["user"]).first()
        if request.POST.has_key("overseer") and request.POST["overseer"] != "0":
            new_target.overseer = DBSession.query(User).filter(User.id == request.POST["overseer"]).first()
        current_user = DBSession.query(User).filter(User.id == 1).first()
        current_user.money -= float(request.POST["bid"])
    return HTTPFound(location="/my_courses")


@view_config(route_name='get_charity_funds', renderer='json')
def get_charity_funds(request):
    return charity_funds

@view_config(route_name='get_enrollable', renderer='json')
def get_enrollable(request):
    return get_enrollable_courses()


def user_savings(user_id):
    user = DBSession.query(User).filter(User.id == user_id).first()
    (saved, lost) = (0.0, 0.0)
    for target in user.my_targets:
        if (target.is_success == "success"):
            saved += target.bid
        if (target.is_success == "fail"):
            lost += target.bid

    return {"saved": saved,
            "lost": lost}


@view_config(route_name='get_name_url', renderer='string')
def get_name_url(request):
    url = request.GET["url"]
    print(url)
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    return soup.html.head.title.string


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

