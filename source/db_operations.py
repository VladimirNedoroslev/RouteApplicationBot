import logging
from datetime import datetime

import psycopg2

from settings import DB_SETTINGS


def user_exists(user_id: str, connection=None):
    if not connection:
        connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone():
        return True
    else:
        return False


def save_user(user_id, chat_id, registration_form):
    connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (id, chat_id, pin, full_name, phone_number, created_at) VALUES (%s, %s, %s, %s, %s, %s);",
        (user_id, chat_id, registration_form.pin, registration_form.full_name,
         registration_form.phone_number, datetime.now()))
    connection.commit()
    logging.info("New user (id = {}) has been inserted into the database. ({})".format(user_id, registration_form))


def update_user(user_id, registration_form):
    connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET pin=%s, full_name=%s, phone_number=%s WHERE id = %s;",
        (registration_form.pin, registration_form.full_name, registration_form.phone_number, user_id))
    connection.commit()
    logging.info("User (id = {}) has been updated. ({})".format(user_id, registration_form))


def get_user(user_id):
    connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    cursor.execute("SELECT pin, full_name, phone_number FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()


def check_database():
    logging.info('Starting checking the database...')
    try:
        connection = psycopg2.connect(**DB_SETTINGS)
        logging.info('Successfully connected to the database')
        cursor = connection.cursor()

        logging.info('Checking "users" table')
        cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='users')")
        if not cursor.fetchone()[0]:
            raise psycopg2.errors.UndefinedTable('table "users" does not exist')
        logging.info('Table "users" exists')
    except Exception as exception:
        logging.exception(exception)
        exit(1)
    logging.info('Database is checked')
