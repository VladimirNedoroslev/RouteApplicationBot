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


def save_or_update_user(registration_form):
    connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    if not user_exists(registration_form.user_id, connection):
        cursor.execute(
            "INSERT INTO users (id, pin, full_name, phone_number, created_at) VALUES (%s, %s, %s, %s, %s);",
            (registration_form.user_id, registration_form.pin, registration_form.full_name,
             registration_form.phone_number, datetime.now()))
        logging.info("New user has been inserted into the database. ({})".format(registration_form))
    else:
        cursor.execute(
            "UPDATE users SET pin=%s, full_name=%s, phone_number=%s WHERE id = %s;",
            (registration_form.pin, registration_form.full_name, registration_form.phone_number,
             registration_form.user_id))
        logging.info("User (id = {}) has been updated. ({})".format(registration_form.user_id, registration_form))
    connection.commit()


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
