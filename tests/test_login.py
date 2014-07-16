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
import re
import tempfile

import app
from app.models.user import User, Group


def test_login_logout(flask_app):
    ''' Test the login / logout of a "normal" and an "admin" user '''
    rv = login(flask_app, 'admin@admin.org', 'default')
    assert "[admin]" in rv.data
    rv = flask_app.get('/admin')
    assert "Admin welcome to the Matrix" in rv.data
    rv = logout(flask_app)
    assert "CONTENT" in rv.data

    rv = login(flask_app, 'douglas@adams.org', 'default')
    assert "[douglas]" in rv.data
    rv = logout(flask_app)
    assert "CONTENT" in rv.data

    # wrong password
    rv = login(flask_app, 'admin@admin.org', 'defaultt')
    assert "Sign" in rv.data

    # wrong users
    rv = login(flask_app, 'admin', 'default')
    assert "Sign" in rv.data

    rv = login(flask_app, 'unknown@admin.org', 'default')
    assert "Sign" in rv.data


def test_admin_page(flask_app):
    ''' Test the access to the admin page '''
    rv = flask_app.get('/admin')
    assert rv.status_code == 403
    assert "403" in rv.data

    # login as admin
    rv = login(flask_app, 'admin@admin.org', 'default')
    assert "CONTENT" in rv.data
    rv = flask_app.get('/admin')
    rv.status_code == 400
    assert "Admin welcome to the Matrix" in rv.data
    rv = logout(flask_app)
    assert "CONTENT" in rv.data
    rv = flask_app.get('/admin')
    assert rv.status_code == 403
    assert "403" in rv.data

    # login as little_admin
    rv = login(flask_app, 'little_admin@admin.org', 'default')
    assert "CONTENT" in rv.data
    rv = flask_app.get('/admin')
    rv.status_code == 400
    assert "Admin welcome to the Matrix" in rv.data
    rv = logout(flask_app)
    assert "CONTENT" in rv.data

    # login as regular user
    rv = login(flask_app, 'douglas@adams.org', 'default')
    assert "CONTENT" in rv.data
    rv = flask_app.get('/admin')
    rv.status_code == 403
    assert "403" in rv.data
    rv = logout(flask_app)
    assert "CONTENT" in rv.data


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

    def fin():
        os.close(db_fd)
        os.unlink(filename)
    request.addfinalizer(fin)

    return wapp


def add_users(db):
    ''' Add some simple users for some simple login tests. '''
    # create admin group
    group = Group()
    group.name = 'admin'
    db.session.add(group)

    # create admin user
    user = User('admin', 'admin@admin.org')
    user.set_password('default')
    user.groups.append(group)

    # create a subgroup for admins
    sub_group = Group()
    sub_group.name = 'little_admin'
    sub_group.parents.append(group)
    db.session.add(sub_group)

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


def login(app, email, password):
    rv = app.get('/login')

    match = re.search(
        '<input.*id=\"csrf_token\".*value=\"(?P<value>.*)\".*>',
        rv.data)

    csrf_value = match.group('value')
    print csrf_value

    # get data to login
    return app.post('/login', data=dict(email=email, password=password,
                    csrf_token=csrf_value, submit="Signe In"),
                    follow_redirects=True)


def logout(app):
    return app.get('/logout', follow_redirects=True)
