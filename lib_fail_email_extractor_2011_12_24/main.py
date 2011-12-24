# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2011 Andrej A Antonov <polymorphm@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

import sys, argparse, configparser, traceback
import getpass
import tornado.stack_context

class UserError(Exception):
    pass

class ProgError(Exception):
    pass

def on_error(e_type, e_value, e_traceback):
    try:
        raise e_value
    except UserError as e:
        print('UserError: {}'.format(e), file=sys.stderr)
        exit(2)
    except ProgError as e:
        print('ProgError: {}'.format(e), file=sys.stderr)
        exit(1)
    except Exception as e:
        traceback.print_exc()
        exit(1)

def main():
    with tornado.stack_context.ExceptionStackContext(on_error):
        parser = argparse.ArgumentParser(
                description='Utility for extracting fail email-addresses')
        
        parser.add_argument(
            '--server',
            help='Receive mail server',
        )
        
        parser.add_argument(
            '--login',
            help='Auth login for receive mail server',
        )
        
        parser.add_argument(
            '--cfg',
            help='Config file',
        )
        
        parser.add_argument(
            '--out',
            help='File for writing fail email-addresses list',
        )
        
        args = parser.parse_args()
        
        server = args.server
        login = args.login
        
        if args.cfg is not None:
            config = configparser.ConfigParser(
                    interpolation=configparser.ExtendedInterpolation())
            config.read(args.cfg)
            
            if server is None:
                server = config.get('auth', 'server', fallback=None)
            
            if login is None:
                login = config.get('auth', 'login', fallback=None)
            
            password = config.get('auth', 'password', fallback=None)
        
        if server is None:
            raise UserError('\'server\' not set')
        
        if login is None:
            raise UserError('\'login\' not set')
        
        if password is None:
            password = getpass.getpass()
        
        if args.out is not None:
            out = open(args.out, mode='w', encoding='utf-8', newline='\n')
        else:
            out = sys.stdout
        
        print((server, login, password, out)) # TEST
