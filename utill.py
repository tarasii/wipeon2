import hashlib
from flask import session
from datetime import datetime

# set_of_settings = ['enterprise', 'template',
#                    'line_right', 'line_left',
#                    'color_right', 'color_left',
#                    'category_right', 'category_left',
#                    'barcodeEAN_right', 'barcodeEAN_left']

default_categories = {'C0':'280000000000', 'C1':'280000000001', 'C2':'280000000002', 'CM':'280000000003', 'C+':'280000000005'}

default_colors = {'white':'White', 'brown':'Brown'}

default_products = {'NORM':'Normal', 'QUO':'Quochka', 'DOM':'Domashne', 'EXP':'Export'}

default_settings = {'enterprise':'XX', 'template':'small',
                   'line_right':'01', 'line_left':'02',
                   'color_right':'white', 'color_left':'brown',
                   'category_right':'C0', 'category_left':'C1',
                   'product_right':'NORM', 'product_left':'QUO',
                   'barcodeEAN_right':default_categories['C0'],
                   'barcodeEAN_left':default_categories['C1']}

default_templates = {'small':'small (60x60)', 'big':'big (90x80)'}


def write_error(db, message, barcode=""):
    print barcode, message
    db.execute("INSERT INTO error_log (datetime, value, barcode) VALUES (datetime('now'), ?, ?)", [message, barcode])
    db.commit()

def get_raw_settings(db):
    cur = db.execute('SELECT name, value FROM settings')
    settings_entries = cur.fetchall()
    res = {name: value for name, value in settings_entries}
    # res = {x: settings_from_db.get(x, default_settings[x]) for x in default_settings.keys()}
    return res

def get_settings(settings_db):
    return {x: settings_db.get(x, default_settings[x]) for x in default_settings.keys()}


def save_settings(db, form, settings, settings_db):
    user = session['username']
    dt = {x:form[x] for x in default_settings.keys()}
    for key, val in dt.iteritems():
        if key in settings_db.keys():
            db.execute('UPDATE settings SET value = ? WHERE name = ?', [val, key])
        else:
            db.execute('INSERT INTO settings (name, value) VALUES (?, ?)', [key, val])

        val_old = settings_db.get(key,'')
        if val_old <> val:
            db.execute('INSERT INTO settings_changes (datetime, user, name, value_old, value_new) VALUES (?, ?, ?, ?, ?)',
                       [datetime.now(), user, key, val_old, val])

    db.commit()

    for k, v in dt.iteritems():
        settings[k] = v

    # print dt
    return dt


def make_barcode(enterprise, line, count):
    res = "{:2s}{:2s}{:06d}".format(enterprise, line, count)
    return res


def check_authorization(app, login, password):
    res = None
    users = {'admin':'4badaee57fed5610012a296273158f5f', 'user':'bf92b982bc12d5cc22c403568f1eb9ba'}
    #if login != app.config['USERNAME']:
    if login not in users.keys():
        res = 'Invalid username'
    elif hashlib.md5(password).hexdigest() != users[login]:
        res = 'Invalid password'
    return res

def get_statistics(db):
    id = 0
    status = 0
    cur = db.execute('SELECT id, status FROM printid ORDER BY id DESC LIMIT 1')
    printed_entries = cur.fetchall()
    if printed_entries:
        id = printed_entries[0][0]
        status = printed_entries[0][1]

    count_all = 0
    cur = db.execute('SELECT count(id) FROM printid')
    printed_entries = cur.fetchall()
    if printed_entries:
        count_all = printed_entries[0][0]

    count = 0
    cur = db.execute('SELECT count(id) FROM printid WHERE status = 1')
    printed_entries = cur.fetchall()
    if printed_entries:
        count = printed_entries[0][0]

    barcode = ''
    cur = db.execute('SELECT barcode FROM printid WHERE status = 1 ORDER BY id DESC LIMIT 1')
    printed_entries = cur.fetchall()
    if printed_entries:
        barcode = printed_entries[0][0]

    return (id, count_all, count, barcode, status)