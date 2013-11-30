import os
import sys
import transaction
import datetime

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
        target1 = Target(name="first course", deadline=datetime.datetime(year=1987,month=10, day=5),bid=100)
        target1.user = user1
        target1.overseer = user3
        DBSession.add(target1)
        DBSession.add(user1)
        DBSession.add(user2)
        DBSession.add(user3)
        DBSession.add(model)
        users = DBSession.query(User).all()
        print(users)

