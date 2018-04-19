import logging
import socket
import sys
from time import sleep

from zeroconf import ServiceInfo, Zeroconf

from sqlite3 import dbapi2 as sqlite3
import os
import utill

run_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(run_path, 'main')

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(db_path)
    rv.row_factory = sqlite3.Row
    return rv

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    db = connect_db()
    settings_db = utill.get_raw_settings(db)
    settings_form = utill.get_settings(settings_db)
    descr = {k:v for k,v in settings_form.iteritems() if k in ['enterprise','line_left','line_right']}
    print descr
    db.close()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    addr = s.getsockname()[0]
    print(addr)
    s.close()

    info = ServiceInfo("_http._tcp.local.",
                       "wipeon._http._tcp.local.",
                       socket.inet_aton(addr), 80, 0, 0,
                       descr, "ash-2.local.")

    zeroconf = Zeroconf()
    print("Registration of a service, press Ctrl-C to exit...")
    zeroconf.register_service(info)
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()