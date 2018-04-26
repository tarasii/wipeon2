from sqlite3 import dbapi2 as sqlite3
import os
import utill
from datetime import datetime
import shutil

import sys
import tty, termios

run_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(run_path, 'main')
template_path = os.path.join(run_path, 'templates')
raw_path = os.path.join(run_path, 'raw')
fdev = '/dev/usb/lp0'


error_template_text = 'CLS' \
                      'TEXT 50, 50, "2", 270, 1, 1, "TEMPLATE ERROR"' \
                      'PRINT 1' \
                      'EOP'

file_name = os.path.join(template_path, 'error.bas')
with open(file_name) as ft:
    error_template_text = ft.read()


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(db_path)
    rv.row_factory = sqlite3.Row
    return rv


def render_barcode_template(template_name, **kwargs):
    file_name =  os.path.join(template_path, template_name)
    str = ""
    with open(file_name) as ft:
        str = ft.read()

    try:
        res = str.format(**kwargs)
    except:
        res = error_template_text

    return res


def prepare_barcode(db, line_side='left'):
    """prepare template for barcode printing"""

    settings_db = utill.get_raw_settings(db)
    settings_form = utill.get_settings(settings_db)

    replace_suffix = '_{}'.format(line_side)
    if line_side == 'left':
        pop_suffix = '_right'
    else:
        pop_suffix = '_left'

    settings = {}
    for key, val in settings_form.iteritems():
        if key.endswith(pop_suffix):
            continue

        if key in ['template']:
            continue

        new_key = key.replace(replace_suffix,"")
        settings[new_key] = val

    dt = datetime.now()

    settings['datetime'] = dt
    settings['status'] = 0
    settings['year'] = dt.year
    settings['month'] = dt.month
    settings['day'] = dt.day
    settings['hour'] = dt.hour

    fields_str = ", ".join(settings.keys())
    values_str = ", ".join(["?"] * len(settings.keys()))
    qstr = 'INSERT INTO printid ({}) VALUES ({})'.format(fields_str, values_str)
    db.execute(qstr, settings.values())
    db.commit()

    id = 0
    cur = db.execute('SELECT id FROM printid ORDER BY id DESC LIMIT 1')
    printed_entries = cur.fetchall()
    if printed_entries:
        id = printed_entries[0][0]

    settings['id'] = "{:06d}".format(id)
    settings['day'] = dt.day
    settings['month'] = dt.month
    settings['year'] = dt.year
    settings['color'] = settings['color'][0].upper()

    barcode = utill.make_barcode(settings['enterprise'], settings['line'], id)
    settings_form['barcode'] = barcode
    settings_form['datetime'] = dt
    settings_form['id'] = id

    template_name = "{}.bas".format(settings_form['template'])


    return (settings_form, render_barcode_template(template_name, **settings))


def print_barcode(line_side='left'):
    """prints barcode based on saved settings"""

    db = connect_db()
    no_error = True

    settings_form, str = prepare_barcode(db, line_side=line_side)
    print settings_form

    if not settings_form:
        utill.write_error(db, "no settings")
        no_error = False

    if not 'id' in settings_form.keys():
        utill.write_error(db, "no id")
        no_error = False

    file_name = os.path.join(raw_path, 'barcode.bas')
    with  open(file_name,'wb') as fd:
        fd.write(str)

    if os.path.exists(fdev):
        try:
            shutil.copy(file_name, fdev)
        except:
            utill.write_error(db, "copy to printer", settings_form['barcode'])
            no_error = False

    else:
        utill.write_error(db, "no printer", settings_form['barcode'])
        no_error = False

    if no_error:
        db.execute('UPDATE printid SET barcode = ?, status = 1 WHERE id = ?', [settings_form['barcode'], settings_form['id']])
        db.commit()

    db.close()


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def keyboard_print():
    """prints barcode from keypress"""

    while True:
        ch = getch()
        if ch == 'q':
            break

        if ch == 'r':
            print_barcode('right')
        else:
            print_barcode()


def button_print():
    """prints barcode from gpio button click"""

    from time import sleep
    import RPi.GPIO as GPIO


    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN)   # button pin
    GPIO.setup(17, GPIO.OUT) # led pin
    GPIO.setup(27, GPIO.IN)  # distance sensor oin
    GPIO.output(17, True)    # led ON - redy

    z1 = not GPIO.input(4)
    z2 = not GPIO.input(27)
    z = z1 and z2
    if (z == True):
        GPIO.output(17, False)
        GPIO.cleanup()
        quit()

    print_barcode()  # first label when ready

    p = False
    while True:
        z1 = not GPIO.input(4)
        z2 = not GPIO.input(27)
        z = z1 or z2
        if (z != p):
            if (z == True):
                GPIO.output(17, False)
                print_barcode()
                sleep(2)
                GPIO.output(17, True)

                # sleep(1)

        p = z

    GPIO.output(17, False)
    GPIO.cleanup()


if __name__ == "__main__":
    docstring = "use 'python print_barcode.py buttons' to print barcode on gpio buttons press \n" \
                "    'python print_barcode.py'         to print barcode on keypress \n" \
                "        'r' - right line settings,\n" \
                "        'q' - quit "
    print docstring #my_func.__doc__
    if 'buttons' in sys.argv:
        print "buttons mode"
        button_print()
    else:
        print "keyboard mode"
        keyboard_print()