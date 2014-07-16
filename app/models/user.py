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

import datetime

from .. import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


groups_table = db.Table('group_to_user',
                        db.Column('user_id', db.Integer,
                                  db.ForeignKey('users.id')),
                        db.Column('group_id', db.Integer,
                                  db.ForeignKey('groups.id')))

group_to_group = db.Table('group_to_group',
                          db.Column('parent_id', db.Integer,
                                    db.ForeignKey('groups.id'),
                                    primary_key=True),
                          db.Column('child_id', db.Integer,
                                    db.ForeignKey('groups.id'),
                                    primary_key=True))


class Group(db.Model):

    ''' A simple Group class that represents the users groups required for the
        permissions.
    '''
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    users = db.relationship('User', secondary=groups_table,
                            backref=db.backref('group_to_user',
                                               lazy='dynamic',
                                               order_by=name))
    parents = db.relationship('Group', secondary=group_to_group,
                              primaryjoin=(id == group_to_group.c.parent_id),
                              secondaryjoin=(id == group_to_group.c.child_id),
                              backref="children",
                              remote_side=[group_to_group.c.parent_id])

    def __repr__(self):
        return "<Group {0}>".format(self.name)


class User(db.Model):

    ''' A simple User class that is stored in the DB. The password value is
        a salted password hash.
    '''
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(40))
    created_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime, default=db.func.now())
    groups = db.relationship('Group', secondary=groups_table,
                             backref=db.backref('group_to_user',
                                                lazy='dynamic',
                                                order_by=name))
    events = db.relationship('Event', secondary='event_attendees')

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.created_at = datetime.datetime.now()
        self.order_by = User.name

    def set_password(self, password):
        ''' store a new password as hashed value.

        :password: The new password to set
        '''
        self.password = generate_password_hash(password)

    def check_password(self, password):
        ''' Check if the provided password matches the set password.

        :password: The password to check
        :return: True if the password is correct and False if not
        '''
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        ''' Return True if the user is authenticated. If a user object gets
            created it should allways be authenticated therefore return True.
            (Required by Flask-Login)
        '''
        return True

    def is_active(self):
        ''' Is the user active, at the moment there is no plan for innactive
            users.
            (Required by Flask-Login)
        '''
        return True

    def is_anonymous(self):
        ''' Is this an anonymous user. Always no.
            (Required by Flask-Login)
        '''
        return False

    def get_id(self):
        ''' Get id for flask-login requires a unicode string
            (Required by Flask-Login)
        '''
        return unicode(self.id)

    def __repr__(self):
        return '<User {0}>'.format(self.name)


@login_manager.user_loader
def load_user(id):
    ''' Get the user for a given user id.

    :id: The unicde representation of the id (numerical value)
    '''
    return User.query.get(int(id))



