#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

import psycopg2
import telegram
from telegram import (ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from db_operations import save_new_user_to_db, save_or_update_user_information
from registration_form import RegistrationForm
from settings import TELEGRAM_BOT_TOKEN, DB_SETTINGS, USER_DATA_APPLICATION_REASON, \
    USER_DATA_APPLICATION_DESTINATION_LONGITUDE, USER_DATA_APPLICATION_DESTINATION_LATITUDE, USER_DATA_REGISTRATION_FORM
from time_options import TimeOptions

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

FAMILY_NAME, GIVEN_NAME, MIDDLE_NAME, PHONE_NUMBER, LOCATION = range(5)

REASON, DESTINATION, START_TIME, END_TIME, CHECK_APPLICATION = range(5)


def start(update, context):
    chat_id = update.effective_chat.id
    user_id = str(update.message.from_user.id)

    save_new_user_to_db(user_id=user_id, chat_id=chat_id)

    context.user_data[USER_DATA_REGISTRATION_FORM] = RegistrationForm()
    update.message.reply_text(
        'Привет. Для того чтобы подавать заявки, Вам необходимо ввести информацию о Вас. '
        'Пожалуйста введите ваше фамилию.')

    return FAMILY_NAME


def family_name(update, context):
    user = update.message.from_user
    context.user_data[USER_DATA_REGISTRATION_FORM].family_name = update.message.text
    logger.info("Family Name of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    update.message.reply_text('Введите ваше имя')
    return GIVEN_NAME


def given_name(update, context):
    user = update.message.from_user
    context.user_data[USER_DATA_REGISTRATION_FORM].given_name = update.message.text
    logger.info("Given Name of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    update.message.reply_text('Введите ваше отчество')
    return MIDDLE_NAME


def middle_name(update, context):
    user = update.message.from_user
    logger.info("Middle name of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    context.user_data[USER_DATA_REGISTRATION_FORM].middle_name = update.message.text

    send_contact_button = telegram.KeyboardButton(text="Отправить свой номер телефона", request_contact=True)
    reg_form = context.user_data[USER_DATA_REGISTRATION_FORM]
    name = '{} {} {}'.format(reg_form.family_name, reg_form.given_name, reg_form.middle_name)
    update.message.reply_text(
        'Хорошо, {}, теперь мне нужен Ваш номер телефона - для этого нажмите на кнопку "Отправить свой номер телефона".'.format(
            name),
        reply_markup=telegram.ReplyKeyboardMarkup([[send_contact_button]]))

    logger.info(context.user_data[USER_DATA_REGISTRATION_FORM])
    return PHONE_NUMBER


def phone_number(update, context):
    user = update.message.from_user
    user_phone_number = update.effective_message.contact.phone_number

    logger.info("Phone number of %s (id = %s): %s", user.first_name, user.id, user_phone_number)
    update.message.reply_text(
        'Теперь отправьте геолокацию Вашего места проживания (Нажмите на скрепку, выберите "Геолокация" и укажите на карте место, где Вы живёте).',
        reply_markup=ReplyKeyboardRemove())
    context.user_data[USER_DATA_REGISTRATION_FORM].phone_number = user_phone_number

    logger.info(context.user_data[USER_DATA_REGISTRATION_FORM])
    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_address = update.message.location

    logger.info("Address of %s (id = %s): %s", user.first_name, user.id, user_address)
    context.user_data[USER_DATA_REGISTRATION_FORM].address_longitude = user_address.longitude
    context.user_data[USER_DATA_REGISTRATION_FORM].address_latitude = user_address.latitude
    context.user_data[USER_DATA_REGISTRATION_FORM].user_id = str(update.message.from_user.id)
    if context.user_data[USER_DATA_REGISTRATION_FORM].is_complete():
        save_or_update_user_information(context.user_data[USER_DATA_REGISTRATION_FORM])
    update.message.reply_text(
        'Отлично, Ваша регистрация завершена! Теперь Вы можете создать заявку через команду /createApplication')

    logger.info(context.user_data[USER_DATA_REGISTRATION_FORM])

    return ConversationHandler.END


def cancel_registration(update, context):
    update.message.reply_text(
        'Вы прервали регистрацию. Пока Вы не заполните все данные, Вы не сможете заполнять заявки. Начать регистрацию можно через команду /start',
        reply_markup=ReplyKeyboardRemove())
    context.user_data[USER_DATA_REGISTRATION_FORM].reset()
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def create_application(update, context):
    user = update.message.from_user
    logger.info("User %s (id = %s) has started a new application", user, user.id)
    update.message.reply_text(
        'Вы начали создание заявки. Опишите причину выхода.')
    return REASON


def application_reason(update, context):
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_REASON] = update.message.text
    logger.info("Reason of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    update.message.reply_text(
        'Укажите геолокацию, куда вы идёте. (так же, как и при регистрации)')
    return DESTINATION


def application_destination(update, context):
    user = update.message.from_user
    destination = update.message.location
    context.user_data[USER_DATA_APPLICATION_DESTINATION_LONGITUDE] = destination.longitude
    context.user_data[USER_DATA_APPLICATION_DESTINATION_LATITUDE] = destination.latitude

    logger.info("Destination of %s (id = %s): %s", user.first_name, user.id, destination)

    reply_keyboard = [TimeOptions.OPTIONS]

    update.message.reply_text(
        'Сколько времени это у вас займёт?',
        reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard))
    return START_TIME


def application_start_time(update, context):
    user = update.message.from_user
    # context.user_data[USER_DATA_APPLICATION_APPROXIMATE_TIME] =
    logger.info("Start time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text(
        'Ваша заявка собрана. Проверьте Ваши данные. Всё верно?',
        reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard))

    return END_TIME

def application_end_time(update, context):
    user = update.message.from_user
    # context.user_data[USER_DATA_APPLICATION_APPROXIMATE_TIME] =
    logger.info("End time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    reply_keyboard = [['Да', 'Нет']]
    update.message.reply_text(
        'Ваша заявка собрана. Проверьте Ваши данные. Всё верно?',
        reply_markup=telegram.ReplyKeyboardMarkup(reply_keyboard))

    return END_TIME



def application_check(update, context):
    if update.message.text.lower() == 'да':
        update.message.reply_text('Ваша заявка создана. Ваш QR-код:',
                                  reply_markup=ReplyKeyboardRemove()
                                  )
    #     send QR-code
    else:
        update.message.reply_text(
            'Ваша заявка составлена неправильно. Создайте её снова через команду /createApplication',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def cancel_application(update, context):
    update.message.reply_text(
        'Вы прервали создание заяки. Для того чтобы заполнить заявку введите команду /createApplication.',
        reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    registration_handler = ConversationHandler(
        entry_points=[CommandHandler(start.__name__, start)],

        states={
            FAMILY_NAME: [MessageHandler(Filters.text, family_name)],
            GIVEN_NAME: [MessageHandler(Filters.text, given_name)],
            MIDDLE_NAME: [MessageHandler(Filters.text, middle_name)],
            PHONE_NUMBER: [MessageHandler(Filters.contact, phone_number)],
            LOCATION: [MessageHandler(Filters.location, location)]

        },

        fallbacks=[CommandHandler(cancel_registration.__name__, cancel_registration)]
    )

    time_regex = '^({}|{}|{}|{})$'.format(TimeOptions.LESS_THAN_HOUR, TimeOptions.ONE_TO_THREE_HOURS,
                                          TimeOptions.ONE_TO_THREE_HOURS, TimeOptions.MORE_THAN_SIX_HOURS)
    create_application_handler = ConversationHandler(
        entry_points=[CommandHandler('createApplication', create_application)],
        states={
            REASON: [MessageHandler(Filters.text, application_reason)],
            DESTINATION: [MessageHandler(Filters.location, application_destination)],
            START_TIME: [MessageHandler(Filters.regex(time_regex),
                                        application_start_time)],
            END_TIME: [MessageHandler(Filters.text, application_end_time)],

            CHECK_APPLICATION: [MessageHandler(Filters.regex('^(Да|Нет)$'), application_check)],

        },
        fallbacks=[CommandHandler(cancel_application.__name__, cancel_application)]
    )

    dispatcher.add_handler(registration_handler)
    dispatcher.add_handler(create_application_handler)
    dispatcher.add_error_handler(error)

    updater.start_polling()
    logger.info('Bot polling has been started!')
    updater.idle()


def check_database():
    logging.info('Starting checking the database...')
    try:
        connection = psycopg2.connect(**DB_SETTINGS)
        logging.info('Successfully connected to the database')
        cursor = connection.cursor()
        logging.info('Checking user_chats table')

        cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='user_chats')")
        if not cursor.fetchone()[0]:
            raise psycopg2.errors.UndefinedTable('table "user_chats" does not exist')
        logging.info('Table user_chats exists')

        cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='users')")
        if not cursor.fetchone()[0]:
            raise psycopg2.errors.UndefinedTable('table "users" does not exist')
        logging.info('Table users exists')

        cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='user_applications')")
        if not cursor.fetchone()[0]:
            raise psycopg2.errors.UndefinedTable('table "user_applications" does not exist')
        logging.info('Table user_applications exists')

    except Exception as exception:
        logging.exception(exception)
        exit(1)
    logging.info('Database is checked')


if __name__ == '__main__':
    check_database()
    main()
