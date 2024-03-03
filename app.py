# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    sort_selected = request.args.get('sort_selected', None)
    db = get_db()

    ALLOWED_SORT_FIELDS = ['name', 'email', 'phone_number', 'address']
    entries = []

    if sort_selected in ALLOWED_SORT_FIELDS:
        # Safely sorting based on predefined allowed fields
        query = f'SELECT name, email, phone_number, address FROM entries ORDER BY {sort_selected}'
        entries = db.execute(query).fetchall()
    else:
        # If no sort is specified or it's not allowed, show all entries without sorting
        entries = db.execute('SELECT name, email, phone_number, address FROM entries').fetchall()

    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    # make sure all entries have data
    if request.form['name'] and request.form['email'] and request.form['address'] and request.form['phone']:
        db.execute('insert into entries (name, email, address, phone_number) values (?, ?, ?, ?)',
               [request.form['name'], request.form['email'],
                request.form['address'],request.form['phone']])
        db.commit()
        flash('New entry was successfully posted')
    else:
        flash('Please fill in all required fields')

    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def delete_entry():
    db = get_db()
    db.execute('DELETE FROM entries WHERE name = ? AND email = ? AND phone_number = ? AND address = ?',
               [request.form['name'], request.form['email'],
                request.form['phone_number'], request.form['address']])
    db.commit()
    flash('Entry was successfully deleted')
    return redirect(url_for('show_entries'))