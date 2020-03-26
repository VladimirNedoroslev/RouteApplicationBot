#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 'Теперь отправьте геолокацию Вашего места проживания .'
import logging
import re

from telegram import ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

from create_application_flow import CreateApplicationFlow, application_reason, application_start_location, \
    application_destination, application_start_time, application_end_time, application_check, cancel_application, \
    create_application
from db_operations import save_new_user_to_db, check_database
from registration_flow import RegistrationFlow, start_registration, family_name, given_name, middle_name, phone_number, \
    cancel_registration
from settings import TELEGRAM_BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

COMMANDS_TEXT = """Мне доступны следующие команды:
/change_lang - изменить язык
/register - зарегистрироваться
/create_app - составить маршрутный лист
/create_org_app - составить маршрутый на организацию
/help - как работать с этим чат ботом
/help_video - видео-инструкция
/commands - посмотреть список команд"""


def start(update, context):
    chat_id = update.effective_chat.id
    user_id = str(update.message.from_user.id)

    save_new_user_to_db(user_id=user_id, chat_id=chat_id)
    update.message.reply_text(
        'Привет, я могу помочь Вам с сотавлением электронных маршрутных листов.\n{}'.format(COMMANDS_TEXT))


def commands(update, context):
    ReplyKeyboardRemove()
    update.message.reply_text(COMMANDS_TEXT, reply_markup=ReplyKeyboardRemove())


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


def help(update, context):
    pass


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    registration_handler = ConversationHandler(
        entry_points=[CommandHandler('register', start_registration), ],
        states={
            RegistrationFlow.FAMILY_NAME: [MessageHandler(Filters.text, family_name)],
            RegistrationFlow.GIVEN_NAME: [MessageHandler(Filters.text, given_name)],
            RegistrationFlow.MIDDLE_NAME: [MessageHandler(Filters.text, middle_name)],
            RegistrationFlow.PHONE_NUMBER: [MessageHandler(Filters.contact, phone_number)],
        },
        fallbacks={CommandHandler('cancel', cancel_registration)}
    )

    input_time_regex = '^([0-9][0-9])\.([0-9][0-9])$'
    create_application_handler = ConversationHandler(
        entry_points=[CommandHandler('create_app', create_application), ],
        states={
            CreateApplicationFlow.REASON: [MessageHandler(Filters.text, application_reason)],
            CreateApplicationFlow.START_LOCATION: [MessageHandler(Filters.location, application_start_location)],
            CreateApplicationFlow.DESTINATION: [MessageHandler(Filters.location, application_destination)],
            CreateApplicationFlow.START_TIME: [MessageHandler(Filters.regex(input_time_regex), application_start_time)],
            CreateApplicationFlow.END_TIME: [MessageHandler(Filters.regex(input_time_regex), application_end_time)],
            CreateApplicationFlow.CHECK_APPLICATION: [
                MessageHandler(Filters.regex(re.compile(r'^(да|нет)$', re.IGNORECASE)), application_check)],

        },
        fallbacks=[CommandHandler('cancel', cancel_application)]
    )
    dispatcher.add_handler(CommandHandler('commands', commands))
    dispatcher.add_handler(CommandHandler(start.__name__, start))

    dispatcher.add_handler(create_application_handler)
    dispatcher.add_handler(registration_handler)
    dispatcher.add_error_handler(error)

    updater.start_polling()
    logging.info('Bot polling has been started!')
    updater.idle()


if __name__ == '__main__':
    check_database()
    main()
