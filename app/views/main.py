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

from flask import (
    render_template,
    redirect,
    url_for,
    request,
    session,
    current_app,
    g)
from flask.ext.login import (
    login_user,
    logout_user,
    current_user,
    login_required)
from flask.ext.principal import (
    identity_changed,
    identity_loaded,
    AnonymousIdentity,
    Identity,
    RoleNeed,
    UserNeed)

from .. import app, admin_permission
from ..forms.login_form import LoginForm
from .navigations import Navigation, Dropdown, Divider


@app.before_request
def before_request():
    """ Set the current flask-login user to g.user
    """
    g.user = current_user


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    ''' Set the correct roles for the current user
    :sender: Not used
    :identity: The identity to set the user and the user roles
    '''
    # set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'groups'):
        for group in current_user.groups:
            identity.provides.add(RoleNeed(group.name))
            add_parents(identity, group)


def add_parents(identity, group):
    ''' Add the parent groups to the Roles
    :identity: The identity to add the roles to
    :group: The group object to get the parents from
    '''
    for parent in group.parents:
        identity.provides.add(RoleNeed(parent.name))
        add_parents(identity, parent)


@app.route('/')
@app.route('/index')
def index():
    ''' The start page '''
    if g.user.is_authenticated():
        return render_template("index.html",
                               title="App",
                               data="DATA",
                               navigations=[
                                    Navigation('test', '#test'),
                                    Navigation('About', '#about'),
                                    Dropdown('[{0}]'.format(g.user.name),
                                             [Navigation('Settings', '/index'),
                                              Divider(),
                                              Navigation('Logout', '/logout')])])
    else:
        return render_template("index.html", title="App",
                               data="DATA",
                               navigations=[Navigation('test', '#test'),
                                            Navigation('About', '#about'),
                                            Navigation('Login', '/login')])


@app.route('/admin')
@admin_permission.require(403)
def admin():
    ''' The admin start page '''
    return render_template('admin.html',
                           text="Admin welcome to the Matrix {0}".format(
                               g.user.name),
                           title="App [Admin]",
                           navigations=[Navigation('test', '#test'),
                                        Navigation('About', '#about')])


@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' The Login handler for all users. '''
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me)
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(form.user.id))
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    ''' Logout the current user. '''
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Prinicpal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def access_denied(e):
    return render_template('403.html'), 403
