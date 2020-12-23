#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler

from telegram import ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler)

from create_application_flow import get_create_application_conversation_handler
from create_application_organization_flow import get_create_organization_application_conversation_handler
from db_operations import check_database
from registration_flow import get_registration_conversation_handler
from settings import (TELEGRAM_BOT_TOKEN, LOG_TIME_FORMAT, LOG_FORMAT, CHANGE_LANGUAGE_COMMAND, VIEW_COMMANDS_COMMAND,
                      HELP_COMMAND, HELP_VIDEO_COMMAND, REGISTRATION_COMMAND, CHANGE_INFO_COMMAND,
                      CREATE_APPLICATION_COMMAND, CREATE_ORGANIZATION_APPLICATION_COMMAND, CANCEL_COMMAND, SKIP_COMMAND)

COMMANDS_TEXT = """Мне доступны следующие команды:
/{} - изменить язык
/{} - зарегистрироваться
/{} - изменить информацию о себе
/{} - составить маршрутный лист для физического лица
/{} - составить маршрутный лист для юридических лиц
/{} - как работать с этим чат ботом
/{} - видео-инструкция
/{} - посмотреть список команд
/{} - cancel отменить текущую операцию
/{} - пропустить шаг, если возможно""".format(
    CHANGE_LANGUAGE_COMMAND,
    REGISTRATION_COMMAND,
    CHANGE_INFO_COMMAND,
    CREATE_APPLICATION_COMMAND,
    CREATE_ORGANIZATION_APPLICATION_COMMAND,
    HELP_COMMAND,
    HELP_VIDEO_COMMAND,
    VIEW_COMMANDS_COMMAND,
    CANCEL_COMMAND,
    SKIP_COMMAND)


def start(update, context):
    update.message.reply_text(
        'Привет, я могу помочь Вам с сотавлением электронных маршрутных листов.\n{}'.format(COMMANDS_TEXT))


def commands(update, context):
    update.message.reply_text(COMMANDS_TEXT, reply_markup=ReplyKeyboardRemove())


def error(update, context):
    """Log Errors caused by Updates."""
    logging.error('Update "%s" caused error: "%s"', update, context.error)
    update.message.reply_text('Я наткнулся на небольшую техническую неполадку, когда хотел ответить на эту команду. '
                              'Извиняюсь, но я не смогу её обработать.')


def change_lang(update, context):
    update.message.reply_text('Извините, смена языков пока не поддерживается.')


def help(update, context):
    update.message.reply_text('Тут будет инструкция по работе с ботом.')


def help_video(update, context):
    update.message.reply_text('Тут будет видео-инструкция по работе с ботом.')


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    logging.info('Adding bot handlers...')
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler(CHANGE_LANGUAGE_COMMAND, change_lang))
    dispatcher.add_handler(CommandHandler(VIEW_COMMANDS_COMMAND, commands))
    dispatcher.add_handler(CommandHandler(HELP_COMMAND, help))
    dispatcher.add_handler(CommandHandler(HELP_VIDEO_COMMAND, help_video))

    dispatcher.add_handler(get_registration_conversation_handler())
    dispatcher.add_handler(get_create_application_conversation_handler())
    dispatcher.add_handler(get_create_organization_application_conversation_handler())

    dispatcher.add_error_handler(error)
    logging.info('Finished adding handlers, starting polling...')

    updater.start_polling()
    logging.info('Bot polling has been started!')
    updater.idle()


def configure_logging():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_TIME_FORMAT)
    log_file_name = f'route_bot.log'

    logger = logging.getLogger()
    file_handler = TimedRotatingFileHandler(log_file_name, when="midnight", )
    file_handler.formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_TIME_FORMAT)
    logger.addHandler(file_handler)


if __name__ == '__main__':
    configure_logging()
    check_database()
    main()
