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

from .. import db
from ..models.user import User


class Event(db.Model):

    ''' A Event object representing an event. With the date and the attendees.
    '''
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256))
    created_at = db.Column(db.DateTime)
    last_changed = db.Column(db.DateTime, default=db.func.now())
    event_date = db.Column(db.DateTime)
    attendees = db.relationship('EventAttendee', cascade="all, delete-orphan",
                                backref="event")

    def __init__(self, name, date):
        self.name = name
        self.created_at = datetime.datetime.now()
        self.event_date = date
        self.order_by = Event.event_date

    def __repr__(self):
        return '<Event {0}:{1}>'.format(self.name, self.event_date)


class EventAttendee(db.Model):
    ''' The table holding all event attendess and their status.
        Invited, Declined, Attending.
    '''
    NEW, INVITED, ATTENDING, DECLINED = range(4)
    __tablename__ = "event_attendees"
    event_id = db.Column(db.Integer,
                         db.ForeignKey('events.id'), primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'), primary_key=True)
    status = db.Column(db.Integer, default=NEW)

    def __init__(self, user):
        self.user = user
        self.status = EventAttendee.NEW

    user = db.relationship(User, lazy='joined')
