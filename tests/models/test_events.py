#
# Copyright (C) 2014 Mathias Weber <mathew.weber@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
#

import pytest
import os
import tempfile
import datetime

import app
from app.models.user import User, Group
from app.models.event import Event, EventAttendee


def test_events(flask_app):
    ''' Test db acces to the db users '''

    event = Event.query.filter_by(name='One').one()
    assert event is not None
    assert event.name == "One"
    assert len(event.attendees) == 1
    assert event.attendees[0].status == EventAttendee.NEW
    assert event.attendees[0].user.name == 'douglas'

    event = Event.query.filter_by(name='Two').one()
    assert event is not None
    assert event.name == "Two"
    assert str(event) == "<Event Two:2014-06-13 18:00:00>"
    assert len(event.attendees) == 3
    for attendee in event.attendees:
        assert attendee.status == EventAttendee.NEW
        assert attendee.user.name in ['douglas', 'Admin', 'little admin']

    events = Event.query.join('attendees', 'user')
    events = events.filter(User.name == 'douglas')
    cnt = 0
    for event in events:
        cnt += 1
        assert event is not None
        assert event.name in ["One", "Two"]
    assert cnt == 2

    # require this call that the db remains valid
    flask_app.get('')


@pytest.fixture
def flask_app(request):
    ''' Get a flask app to call the flask app as an example client '''

    db_fd, filename = tempfile.mkstemp()
    app.app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///{0}'.format(filename)
    app.app.config['TESTING'] = True
    wapp = app.app.test_client()
    app.db.create_all()

    add_users(app.db)
    add_events(app.db)

    def fin():
        os.close(db_fd)
        os.unlink(filename)
    request.addfinalizer(fin)

    return wapp


def add_users(db):
    ''' Add some simple users for some simple tests. '''
    # create admin group
    group = Group()
    group.name = 'admin'
    db.session.add(group)

    # create admin user
    user = User('Admin', 'admin@admin.org')
    user.set_password('default')
    user.groups.append(group)

    # create a subgroup for admins
    sub_group = Group()
    sub_group.name = 'little_admin'
    sub_group.parents.append(group)
    db.session.add(group)

    # create little admin user
    user = User('little admin', 'little_admin@admin.org')
    user.set_password('default')
    user.groups.append(sub_group)

    # create users group
    group = Group()
    group.name = 'users'
    db.session.add(group)

    # add standard user
    user = User('douglas', 'douglas@adams.org')
    user.set_password('default')
    user.groups.append(group)
    db.session.add(user)
    db.session.commit()


def add_events(db):
    ''' Add some simple events for testing '''
    admin = User.query.filter_by(email='admin@admin.org').one()
    little_admin = User.query.filter_by(email='little_admin@admin.org').one()
    douglas = User.query.filter_by(email='douglas@adams.org').one()

    event_one = Event('One', datetime.datetime(2014, 05, 13, 18, 00))
    attendee = EventAttendee(douglas)
    attendee.event = event_one

    event_two = Event('Two', datetime.datetime(2014, 06, 13, 18, 00))
    attendee = EventAttendee(douglas)
    attendee.event = event_two

    attendee = EventAttendee(admin)
    attendee.event = event_two

    attendee = EventAttendee(little_admin)
    attendee.event = event_two

    db.session.add(event_one)
    db.session.add(event_two)

    db.session.commit()
