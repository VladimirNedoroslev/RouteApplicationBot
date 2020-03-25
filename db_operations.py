import logging
from datetime import datetime

import psycopg2

from registration_form import RegistrationForm
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


def user_exists_in_users(connection, user_id: str):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone():
        return True
    else:
        return False


def save_or_update_user_information(registration_form: RegistrationForm):
    connection = psycopg2.connect(**DB_SETTINGS)
    cursor = connection.cursor()
    if not user_exists_in_users(connection, registration_form.user_id):
        cursor.execute(
            "INSERT INTO users (id, family_name, given_name, middle_name, phone_number, address_longitude, address_latitude) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (registration_form.user_id, registration_form.family_name, registration_form.given_name,
             registration_form.middle_name, registration_form.phone_number, registration_form.address_longitude,
             registration_form.address_latitude))
        logging.info("New user info has been inserted into the database. ({})".format(registration_form))
    else:
        cursor.execute(
            "UPDATE users SET family_name=%s, given_name=%s, middle_name=%s, phone_number=%s, address_longitude=%s, address_latitude=%s WHERE id = %s;",
            (registration_form.family_name, registration_form.given_name,
             registration_form.middle_name, registration_form.phone_number, registration_form.address_longitude,
             registration_form.address_latitude, registration_form.user_id))
        logging.info("User (id = {}) has been updated. ({})".format(registration_form.user_id, registration_form))
    connection.commit()
