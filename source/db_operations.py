import logging
import uuid
from datetime import datetime

import psycopg2

from settings import DB_SETTINGS


def user_exists_in_user_chats(connection, user_id: str):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user_chats WHERE id = %s", (user_id,))
    if cursor.fetchone():
        return True
    else:
        return False


def save_new_user_to_db(user_id: str, chat_id: str):
    connection = psycopg2.connect(**DB_SETTINGS)
    if not user_exists_in_user_chats(connection, user_id):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user_chats (id, chat_id, created_at) VALUES (%s, %s, %s);",
                       (user_id, chat_id, datetime.now()))
        connection.commit()
        logging.info("New user has been inserted into the database. id = {}".format(user_id))


def user_exists_in_users(user_id: str, connection=None):
    if not connection:
        connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone():
        return True
    else:
        return False


def save_or_update_user_information(registration_form):
    connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    if not user_exists_in_users(registration_form.user_id, connection):
        cursor.execute(
            "INSERT INTO users (id, pin, full_name, phone_number) VALUES (%s, %s, %s, %s);",
            (registration_form.user_id, registration_form.pin, registration_form.full_name,
             registration_form.phone_number,))
        logging.info("New user info has been inserted into the database. ({})".format(registration_form))
    else:
        cursor.execute(
            "UPDATE users SET pin=%s, full_name=%s, phone_number=%s WHERE id = %s;",
            (registration_form.pin, registration_form.full_name, registration_form.phone_number,
             registration_form.user_id))
        logging.info("User (id = {}) has been updated. ({})".format(registration_form.user_id, registration_form))
    connection.commit()


def get_user_info(user_id):
    connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()


def save_application(application_form):
    connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO user_applications (id, user_id, reason, start_location_longitude, start_location_latitude, destination_longitude, destination_latitude, start_time, end_time, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s",
        (uuid.uuid1(), application_form.user_id, application_form.reason, application_form.start_location.longitude,
         application_form.start_location.latitude, application_form.destination.longitude,
         application_form.destination.latitude, application_form.start_time, application_form.end_time, datetime.now()))
    connection.commit()
    logging.info(
        "New application has been created by the user (id = {}): {}".format(application_form.user_id, application_form))


def check_database():
    logging.info('Starting checking the database...')
    try:
        connection = psycopg2.connect(**DB_SETTINGS)
        logging.info('Successfully connected to the database')
        cursor = connection.cursor()
        logging.info('Checking "user_chats" table')

        cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='user_chats')")
        if not cursor.fetchone()[0]:
            raise psycopg2.errors.UndefinedTable('table "user_chats" does not exist')
        logging.info('Table "user_chats" exists')

        logging.info('Checking "users" table')
        cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='users')")
        if not cursor.fetchone()[0]:
            raise psycopg2.errors.UndefinedTable('table "users" does not exist')
        logging.info('Table "users" exists')


    except Exception as exception:
        logging.exception(exception)
        exit(1)
    logging.info('Database is checked')
