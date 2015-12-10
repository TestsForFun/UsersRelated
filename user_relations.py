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
from tornado.log import logging
from tornado.options import options, define, parse_config_file

define('USE_DB', default=True, help='Using Momoko')
define('FILL_DB', default=False, help='Fill db with test data')
define('USE_RC', default=True, help='Using Redis')
define('FLUSH_RC', default=False, help='Flush old data')
define('TABLE_NAME', default='ipaddresses', help='Name of big table')
define('TEST_COUNT', default=100000, help='Count of test inserts')

def _fill_db(db):
    import random
    import socket
    import struct
    try:
        db.execute('DROP TABLE IF EXISTS %s;' % options.TABLE_NAME)
        db.execute('CREATE TABLE %s (user_id INT, ip INET, dt TIMESTAMP);' % options.TABLE_NAME)
        for n in range(1, options.TEST_COUNT):
            randip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
            randuser = random.randint(1000, 10000)
            db.execute("INSERT INTO %s VALUES(%i, '%s', NOW());" % (
                options.TABLE_NAME,
                randuser, randip
            ))
            #logging.info('%i %s' % (n,randip))
        logging.info('Done - %i', n)
    except (psycopg2.Warning, psycopg2.Error) as error:
        logging.info(str(error))

class BaseHandler(tornado.web.RequestHandler):
    """
    Base

    """
    @property
    def db(self):
        return self.application.db

    @property
    def rc(self):
        return self.application.rc

class MainHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        first_user_id = int(self.request.arguments['first_user_id'][0])
        second_user_id = int(self.request.arguments['second_user_id'][0])
        result = False

        if options.USE_RC:
            sstring = '%s#%s' % (first_user_id, second_user_id)
            result = self.rc.sismember('Related', sstring)
            if not result:
                logging.info('No matches for %i and %i found before' % (
                    first_user_id, second_user_id
                ))
                if options.USE_DB:
                    logging.info('Trying to analyse DB...')
                    for uid in (first_user_id, second_user_id):
                        if self.rc.scard(uid) > 0:
                            self.rc.expire(uid, 300)
                        cursor = yield self.db.execute(
                            "SELECT host(ip) FROM %s where user_id=%i;" % (options.TABLE_NAME, uid))
                        for ips in cursor.fetchall():
                            self.rc.sadd(uid, ips[0])
                    if self.rc.scard(first_user_id) > self.rc.scard(second_user_id):
                        self.rc.sadd('Related', sstring)
                        result = True

        self.write("Users %i and %i are related: %s." % (
            first_user_id, second_user_id,
            result
        ))
        self.finish()

if __name__ == "__main__":
    try:
        parse_config_file('config.conf')
    except:
        logging.info('Config file ./config.conf not found')

    application = tornado.web.Application([
        (r"/user_relations/", MainHandler),
    ])

    ioloop = tornado.ioloop.IOLoop.instance()

    if options.USE_RC:
        redisConnectionPool = redis.ConnectionPool(
            host='localhost',
            port=6379, db=12
        )
        application.rc = redis.Redis(connection_pool=redisConnectionPool)
        logging.info('Using Redis')

        if options.FLUSH_RC:
            application.rc.flushdb()

    if options.USE_DB:
        application.db = momoko.Pool(
            dsn='dbname=exness user=ror password=rorx '
            'host=localhost port=5432',
            size=1,
            max_size=100,
            ioloop=ioloop,
        )
        future = application.db.connect()
        ioloop.add_future(future, lambda f: ioloop.stop())
        ioloop.start()
        future.result()
        logging.info('Using Database')

        if options.FILL_DB:
            logging.info('Filling Database')
            _fill_db(application.db)

    logging.info("Starting tornado web server")
    application.listen(8888)
    ioloop.start()

