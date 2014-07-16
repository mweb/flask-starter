# Flask-Starter

This is a slightly flask starter templates that provides a started project
for flask applications. The starter template includes the following python 
packages:

  * Flask
  * Flask-WTF
  * Flask-Bable
  * Flask-Login
  * Flask-Principal
  * Flask-Script
  * Flask-sqlalchemy
  * Flask-migrate
  * path.py

For testing:

  * pytest

The web front end uses bootstrap, font-awesome, jquery and Moment.js.

## Open Issues

The current starter templates is ready to be used but I intend to fix the 
following points:

**For Version 1.0**

  * i18n
  * Better example page

**For Future Versions**
  * Support for asynchronous job scheduling (celery & redis?)
  * Deployment
  * Blueprints
  * Use Flask-Assets für js files

## Setup

To setup the project clone the project into some directory and then create
a virtualenv for it.


    mkvirtualenv flask-env
    python setup.py develop
    pip install pytest pytest-cov


This should install all the required packages to get started with the
development.

Now the DB needs to be initialiezed and afterwards the development webserver
can be started with:

    python run.py runserver

On default the webserver is listening on port 5000.

## DB

Setup a new DB, since there is no release yet we don't use alembic revisions
yet. We use alembic but the DB schema isn't stored in git which you would do
for all revisions that you deploy somewhere.

    mkdir migrations/versions
    python run.py db migrate
    python run.py db upgrade

Then you are haven a simple db but no data in it. The data can be added
manually by starting the the flask shell and adding the users either by hand
or with the given method call:

    python run.py shell
    
    >>> import migrations.init_db as init_db
    >>> init_db.add_users()

## Bable

Extract all the string form the application:

    pybable extract -f bable.cfg -o messages.pot .

Start the translation for example for German:

    pybabel init -i messages.dot -d translations -l de

Translations is the folder where the translations get stored. The po file can
be found here `translations/de/LC_MESSAGES/messages.po`
When the translations is finished compile the translation file:

    pybabel compile -d translations

When string changed you can use pybable to merge the changes

    pybable update -i messages.pot -d translations

## Testing

to run the test start them with the following command:

    py.test tests

To get coverage feedback run it like this:

    py.test --cov app tests

To get html output with the possibility to see each line missing run it like
this:

    py.test --cov app --cov-report html