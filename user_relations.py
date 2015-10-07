# -*- coding: utf-8 -*-

"""

 # File: Main web module 
 # Author: Dmitri Plakhov
 # Date: Oct 2015

"""

import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line, define, options
import redis
import logging
from string import split
from random import randint
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('main')

redisConnectionPool = redis.ConnectionPool(host='localhost', port=6379, db=12)
redisClient = redis.Redis(connection_pool=redisConnectionPool)

## Uncomment if dont want old data after restart
#redisClient.flushdb()



application = tornado.web.Application([
    (r"/user_relations/", MainHandler),
])

if __name__ == "__main__":
    parse_command_line()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
