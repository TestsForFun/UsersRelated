# -*- coding: utf-8 -*-

"""

 # File: Main web module 
 # Author: Dmitri Plakhov
 # Date: Oct 2015

"""

import redis
import psycopg2
import momoko
import tornado.web
import tornado.ioloop
from datetime import datetime
from tornado.options import options, define, parse_config_file

define('USE_DB', default=True, help='Using Momoko')
define('USE_RC', default=False, help='Using Redis')
define('FLUSH_RC', default=False, help='Flush old data')

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    @property
    def rc(self):
        return self.application.rc

class MainHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        first_user_id = self.request.arguments['first_user_id'][0]
        second_user_id = self.request.arguments['second_user_id'][0]
        if options.USE_DB: 
            cursor = yield self.db.execute("SELECT 1;")
            result = cursor.fetchone()
        if options.USE_RC: 
            result = self.rc.sismember('A','B')
        self.write("Users %s and %s are related: %s." % (
            self.request.arguments['first_user_id'][0], 
            self.request.arguments['second_user_id'][0], 
            result
        ))
        self.finish()

if __name__ == "__main__":
    try:
        parse_config_file('config.conf')
    except:
        print 'No config file'

    application = tornado.web.Application([
        (r"/user_relations/", MainHandler),
    ])

    ioloop = tornado.ioloop.IOLoop.instance()

    if options.USE_DB:
        application.db = momoko.Pool(
            dsn='dbname=exness user=ror password=rorx '
            'host=localhost port=5432',
            size=1,
            ioloop=ioloop,
        )
        future = application.db.connect()
        ioloop.add_future(future, lambda f: ioloop.stop())
        ioloop.start()
        future.result()

    if options.USE_RC:
        redisConnectionPool = redis.ConnectionPool(host='localhost', port=6379, db=12)
        application.rc = redis.Redis(connection_pool=redisConnectionPool)
        if options.FLUSH_RC:
            application.rc.flushdb()

    application.listen(8888)
    ioloop.start()

