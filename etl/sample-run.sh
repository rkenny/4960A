#!/bin/bash
# do not commit this to git! It has passwords .
DB_USER='username' DB_PASSWORD='real_password' DB_NAME='target_db' python3 ./dblp-db-insert.py
