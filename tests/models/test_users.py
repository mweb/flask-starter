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

import app
from app.models.user import User, Group


def test_users(flask_app):
    ''' Test db acces to the db users '''

    admin_user = User.query.filter_by(email='admin@admin.org').one()
    assert admin_user.name == 'Admin'
    assert not admin_user.check_password('other')
    assert admin_user.check_password('default')
    admin_user.set_password('other')
    assert not admin_user.check_password('default')
    assert admin_user.check_password('other')
    admin_user.set_password('default')
    assert str(admin_user) == '<User Admin>'
    assert len(admin_user.groups) == 1
    assert admin_user.groups[0].name == 'admin'
    assert len(admin_user.groups[0].parents) == 0
    # require this call that the db remains valid
    flask_app.get('')


def test_ubgroups(flask_app):
    ''' Test db acces to the db groups '''

    group = Group.query.filter_by(name='little_admin').one()
    assert group.name == 'little_admin'
    assert str(group) == '<Group little_admin>'
    assert len(group.users) == 1
    assert group.users[0].name == 'little admin'
    assert group.users[0].email == 'little_admin@admin.org'
    assert len(group.parents) == 1
    assert group.parents[0].name == 'admin'
    assert len(group.parents[0].users) == 1
    assert group.parents[0].users[0].name == 'Admin'
    assert group.parents[0].users[0].email == 'admin@admin.org'
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
