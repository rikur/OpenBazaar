#!./env/bin/python
# OpenBazaar's launcher script.
import argparse
import os
from network_util import check_NAT_status


def is_osx():
    return os.uname()[0].startswith('Darwin')


def osx_check_dyld_library_path():
    '''This is a necessary workaround as you cannot set the DYLD_LIBRARY_PATH by the time python has started.'''
    if 'DYLD_LIBRARY_PATH' not in os.environ or len(os.environ['DYLD_LIBRARY_PATH']) == 0:
        print 'WARNING: DYLD_LIBRARY_PATH not set, this might cause issues with openssl elliptic curve cryptography and other libraries.'
        print "It is recommended that you stop OpenBazaar and set your DYLD_LIBRARY_PATH environment variable as follows\n"
        print 'export DYLD_LIBRARY_PATH=$(brew --prefix openssl)/lib:${DYLD_LIBRARY_PATH}', "\n"
        print 'then restart OpenBazaar.', "\n"

        from ctypes import cdll
        try:
            print "Attempting to load libcrypto.dylib and libssl.dylib."
            openssl_prefix = os.popen('brew --prefix openssl')
            if openssl_prefix is not None:
                cdll.LoadLibrary(openssl_prefix + '/lib/libcrypto.dylib')
                cdll.LoadLibrary(openssl_prefix + '/lib/libssl.dylib')
                print "Attempting to load libcrypto.dylib and libssl.dylib."
        except:
            pass


def initArgumentParser():
    parser = argparse.ArgumentParser(usage=usage())

    parser.add_argument('-i', '--server-public-ip', help='Server Public IP')

    parser.add_argument('-p', '--server-public-port', '--my-market-port',
                        default=12345,
                        type=int,
                        help='Server Public Port (default 12345)')

    parser.add_argument('-k', '--http-ip', '--web-ip',
                        default='127.0.0.1',
                        help='Web Interface IP (default 127.0.0.1;' +
                        ' use 0.0.0.0 for any)')

    parser.add_argument('-q', '--web-port', '--http-port',
                        type=int, default=-1,
                        help='Web Interface Port (default random)')

    parser.add_argument('-l', '--log',
                        default='logs/production.log',
                        help='Log File')

    parser.add_argument('-d', '--development-mode', action='store_true',
                        help='Development mode')

    parser.add_argument("--database",
                        default='db/ob.db',
                        help="Database filename")

    parser.add_argument('-n', '--dev-nodes',
                        type=int,
                        help='Number of Dev nodes to start up')

    parser.add_argument('--bitmessage-user', '--bmuser',
                        default='username',
                        help='Bitmessage API username')

    parser.add_argument('--bitmessage-pass', '--bmpass',
                        default='password',
                        help='Bitmessage API password')

    parser.add_argument('--bitmessage-port', '--bmport',
                        type=int,
                        default=8442,
                        help='Bitmessage API port')

    parser.add_argument('-u', '--market-id',
                        help='Market ID')

    parser.add_argument('-j', '--disable-upnp',
                        action='store_true',
                        default=False,
                        help='Disable automatic UPnP port mappings')

    parser.add_argument('-S', '--seed-mode',
                        action='store_true',
                        default=False,
                        help='Enable Seed Mode')

    parser.add_argument('-s', '--seeds',
                        nargs='*',
                        default=[])
    parser.add_argument('--disable-open-browser',
                        action='store_true',
                        default=False,
                        help='Don\'t open preferred web browser ' +
                        'automatically on start')
    parser.add_argument('--config-file',
                        default=None,
                        help='Disk path to an OpenBazaar configuration file')

    parser.add_argument('command')
    return parser


def getDefaults():
    return {'SERVER_PORT': 12345,
            'LOGDIR': 'logs',
            'LOG_FILE': 'production.log',
            'DBDIR': 'db',
            'DEVELOPMENT': False,
            'SEED_URI': 'seed.openbazaar.org seed2.openbazaar.org seed.openlabs.co us.seed.bizarre.company eu.seed.bizarre.company'.split(),
            'DISABLE_UPNP': False,
            'DISABLE_OPEN_DEFAULT_WEBBROWSER': False,
            'LOG_LEVEL': 10,  # CRITICAL=50, ERROR=40, WARNING=30, DEBUG=10, NOTSET=0
            'NODES': 3,
            'HTTP_IP': '127.0.0.1',
            'HTTP_PORT': -1
            }


def usage():
    return """
openbazaar [options] <command>

    COMMANDS
        start            Start OpenBazaar
        stop             Stop OpenBazaar

    OPTIONS
    -i, --server-public-ip
        Server public IP

    -p, --server-public-port, --my-market-port
        Server public (P2P) port (default 12345)

    -k, --http-ip, --web-ip
        Web interface IP (default 127.0.0.1; use 0.0.0.0 for any)

    -q, --web-port, --http-port
        Web interface port (random by default)

    -l, --log
        Log file (default 'logs/production.log')

    -d, --development-mode
        Enable development mode

    --database
        Database filename. (default 'db/od.db')

    -n, --dev-nodes
        Number of dev nodes to start up

    --bitmessage-user, --bmuser
        Bitmessage API username

    --bitmessage-pass, --bmpass
        Bitmessage API password

    --bitmessage-port, --bmport
        Bitmessage API port

    -u, --market-id
        Market ID

    -j, --disable-upnp
        Disable automatic UPnP port mappings

    -S, --seed-mode
        Enable seed mode

    --disable-open-browser
        Don't open preferred web browser automatically on start

    --config-file
        Disk path to an OpenBazaar configuration file



"""

if __name__ == '__main__':

    parser = initArgumentParser()
    arguments = parser.parse_args()

    if is_osx():
        osx_check_dyld_library_path()

    defaults = getDefaults()

    print "Checking NAT Status..."
    nat_status = check_NAT_status()

    if arguments.server_public_ip is not None:
        my_market_ip = arguments.server_public_ip
    else:
        print nat_status
        my_market_ip = nat_status['external_ip']

    """
    import openbazaar_daemon
    openbazaar_daemon.start_node(my_market_ip,
                                 my_market_port,
                                 http_ip,
                                 http_port,
                                 log_file,
                                 market_id,
                                 bm_user,
                                 bm_pass,
                                 bm_port,
                                 seed_peers,
                                 seed_mode,
                                 dev_mode,
                                 log_level,
                                 database,
                                 disable_upnp,
                                 disable_open_browser)
    """
