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

import threading, functools
import imaplib
import tornado.ioloop, tornado.stack_context
from .error_types import SearchEmailError, FetchEmailError

def fail_email_extractor(server, login, password,
        filter_from=None, on_email=None, on_fail_email=None,
        on_final=None):
    io_loop = tornado.ioloop.IOLoop.instance()
    
    @tornado.stack_context.wrap
    def _on_fail_email(email):
        # TODO ...
        
        if on_fail_email is not None:
            on_fail_email(email)
    
    @tornado.stack_context.wrap
    def _on_email(num, data):
        if on_email is not None:
            result = on_email(num, data)
            
            if result:
                return
        
        headers = data[0][1]
        
        print('_on_email(data): \n{!r}\n\n'.format(headers)) # TEST
    
    @tornado.stack_context.wrap
    def _on_final(error):
        if error is not None:
            raise error
        
        if on_final is not None:
            on_final()
    
    def daemon():
        error = None
        
        try:
            m = imaplib.IMAP4(host=server)
            
            m.login(login, password)
            try:
                m.select(readonly=True)
                try:
                    typ, inbox_data = m.search(None, 'ALL')
                    
                    if typ != 'OK':
                        raise SearchEmailError('Search email in inbox error') 
                    
                    for num in inbox_data[0].split():
                        typ, data = m.fetch(num, '(RFC822)')
                        
                        if typ != 'OK':
                            raise FetchEmailError('Fetch email error') 
                        
                        io_loop.add_callback(
                            functools.partial(_on_email, num, data))
                finally:
                    m.close()
            finally:
                m.logout()
        except Exception as e:
            error = e
        
        io_loop.add_callback(
                functools.partial(_on_final, error))
    
    thread = threading.Thread(target=daemon)
    thread.daemon = True
    thread.start()
