#!/bin/sh

export MOMOKO_TEST_DB='your_db'
export MOMOKO_TEST_USER='your_user'
export MOMOKO_TEST_PASSWORD='your_password'
export MOMOKO_TEST_HOST='localhost'
export MOMOKO_TEST_PORT='5432'

/usr/bin/env python user_relations.py
