[![Build Status](https://travis-ci.org/TestsForFun/UsersRelated.svg?branch=master)](https://travis-ci.org/TestsForFun/UsersRelated)
# User IP Relations

$ virtualenv venv

$ . ./venv/bin/activate

$ pip install -r requirements.txt

Edit config.conf

Set FILL_DB to True for first use

Create PostgreSQL database

$ ./start.sh


http://localhost:8888/user_relations/?first_user_id=5376&second_user_id=8852


See test results in 'benchmark' folder (MacBook Air '13 4Gb RAM - Ubuntu 14.04)


# TODO

Compare IP-addresses
