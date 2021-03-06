import os
import sys
import datetime

import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    MyModel,
    Base,
    User,
    Target
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        user1 = User(name="Vasya",username="vasya",password="123456",mail="vasya@mail.ru")

        user2 = User(name="Petya",username="petya",password="123456",mail="petya@mail.ru")

        user3 = User(name="Mama",username="mom",password="123456",mail="mom@mail.ru")

        target1 = Target(name="Python for real dummies like us", deadline=datetime.datetime(year=1987, month=10, day=5),
                         bid=100,
                         url="biomech")
        target1.planned_progress = 70
        target1.current_progress = 30
        target1.user = user1
        target1.overseer = user2
        target1 = Target(name="Inroduction to Gay Ritchi technologies",
                         deadline=datetime.datetime(year=2008, month=10, day=5), bid=500, url="nanotech")
        target1.planned_progress = 60
        target1.current_progress = 40
        target1.is_success = "success"
        target1.user = user2
        target1.overseer = user3
        DBSession.add(target1)
        target1 = Target(name="Total unconciousness!", deadline=datetime.datetime(year=2012, month=10, day=5), bid=900,
                         url="nanotech")
        target1.planned_progress = 60
        target1.current_progress = 40
        target1.is_success = "fail"
        target1.user = user2
        target1.overseer = user3
        DBSession.add(target1)
        target1 = Target(name="Subj to read", deadline=datetime.datetime(year=2008, month=10, day=5), bid=500,
                         type="omni", url="http://fullcycle.ru")
        target1.planned_progress = 80
        target1.current_progress = 70
        target1.user = user2
        target1.overseer = user3
        DBSession.add(user1)
        DBSession.add(user2)
        DBSession.add(user3)
        #DBSession.add(model)
        users = DBSession.query(User).all()
        print(users)

