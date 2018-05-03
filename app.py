from flask import Flask, session, request, render_template, redirect, flash, url_for, g, jsonify
import requests
import os
import utill
import json

from sqlite3 import dbapi2 as sqlite3


app = Flask(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'main'),
    DEBUG=True,
    SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/'
))

# def create_app(config=None):
#     app = Flask(__name__)
#
#     app.config.update(dict(
#         DATABASE=os.path.join(app.root_path, 'flaskr.db'),
#         DEBUG=True,
#         SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
#         USERNAME='admin',
#         PASSWORD='default'
#     ))
#     app.config.update(config or {})
#     app.config.from_envvar('FLASKR_SETTINGS', silent=True)
#
#
#     return app

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


# def init_db():
#     """Initializes the database."""
#     db = get_db()
#     with current_app.open_resource('schema.sql', mode='r') as f:
#         db.cursor().executescript(f.read())
#     db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.route("/")
def index():
    return redirect(url_for('go'))

@app.route("/go", methods=['GET', 'POST'])
def go():
    db = get_db()
    settings_db = utill.get_raw_settings(db)
    settings_form = utill.get_settings(settings_db)

    if request.method == 'POST':
        session['logged_in'] = False
        utill.save_settings(db, request.form, settings_form, settings_db)

    id, count_all, count, barcode, status = utill.get_statistics(db)

    settings_form['count'] = "{}/{}".format(count, count_all)
    settings_form['last_id'] = id
    settings_form['status'] = status

    settings_form['categories_all'] = utill.default_categories
    settings_form['colors_all'] = utill.default_colors
    settings_form['templates_all'] = utill.default_templates
    settings_form['products_all'] = utill.default_products


    settings_form['barcode_right'] = utill.make_barcode(settings_form['enterprise'], settings_form['line_right'], id+1)
    settings_form['barcode_left'] = utill.make_barcode(settings_form['enterprise'], settings_form['line_left'], id+1)
    settings_form['barcode_last'] = barcode

    return render_template('index.html', **settings_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #session['logged_in'] = False
    error = None
    if request.method == 'POST':
        error = utill.check_authorization(app, request.form['username'], request.form['password'])
        if not error:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('go'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    #session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('go'))


@app.route('/get_settings')
def get_settings():
    db = get_db()
    settings_db = utill.get_raw_settings(db)
    settings_form = utill.get_settings(settings_db)
    return jsonify(settings_form)

@app.route('/get_errors')
def get_errors():
    db = get_db()
    cur = db.execute('SELECT datetime, barcode, value FROM error_log ORDER BY id DESC LIMIT 20')
    error_entries = cur.fetchall()

    return render_template('get_errors.html', errors=error_entries)

@app.route("/all")
def all_devices():
    devices = ['127.0.0.1','10.2.195.84','10.2.195.85','10.2.195.86','10.2.195.87',
               '10.2.195.90','10.2.195.92','10.2.195.93','10.2.195.94','10.2.195.95','10.2.195.96','10.2.195.97',
               '10.2.195.98','10.2.195.99','10.2.195.100']

    empty_data = {x:"-" for x in utill.default_settings.keys()}

    devices_status = []
    for dev in devices:
        uri = 'http://{}:5000/get_settings'.format(dev)
        try:
            uResponse = requests.get(uri, timeout=0.2)
            data = uResponse.json()
            res = "Connected"
            print data
        except requests.ConnectionError:
            res = "No connected"
            data = empty_data
        except requests.Timeout:
            res = "No connected"
            data = empty_data

        devices_status.append((dev, res, data['enterprise'],
                               data['line_right'], data['category_right'], data['color_right'], data['product_right'], data['barcodeEAN_right'],
                               data['line_left'], data['category_left'], data['color_left'], data['product_left'], data['barcodeEAN_left']))


    return render_template('all.html', devices=devices, statuses=devices_status )

if __name__=='__main__':
    app.run(host='0.0.0.0', threaded=True)