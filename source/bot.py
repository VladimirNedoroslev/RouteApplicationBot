#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters)

from bot_messages import HELLO, COMMANDS, ERROR, BOT_HELP, BOT_VIDEO_HELP, LANGUAGE_CHOSEN, CHOOSE_LANGUAGE_PROMPT
from create_application_flow import get_create_application_conversation_handler
from create_application_organization_flow import get_create_organization_application_conversation_handler
from db_operations import check_database
from registration_flow import get_registration_conversation_handler, cancel
from settings import (TELEGRAM_BOT_TOKEN, LOG_TIME_FORMAT, LOG_FORMAT, CHANGE_LANGUAGE_COMMAND, VIEW_COMMANDS_COMMAND,
                      HELP_COMMAND, HELP_VIDEO_COMMAND, CANCEL_COMMAND)
from utilities import set_language_dict_for_user, is_cancel_command

HANDLE_CHANGE_LANG = 0


def start(update, context):
    set_language_dict_for_user(context)
    lang_dict = context.user_data['lang']
    update.message.reply_text(lang_dict[HELLO].format(lang_dict[COMMANDS]))


def commands(update, context):
    update.message.reply_text(context.user_data['lang'][COMMANDS], reply_markup=ReplyKeyboardRemove())


def error(update, context):
    logging.error('Update "%s" caused error: "%s"', update, context.error)
    update.message.reply_text(context.user_data['lang'][ERROR])


def change_lang(update, context):
    languages_reply_keyboard = [['Русский', 'Кыргызча'], ]
    update.message.reply_text(context.user_data['lang'][CHOOSE_LANGUAGE_PROMPT],
                              reply_markup=ReplyKeyboardMarkup(languages_reply_keyboard, one_time_keyboard=True))
    return HANDLE_CHANGE_LANG


def handle_change_lang(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)

    if message_text == 'Русский':
        set_language_dict_for_user(context, 'ru')
        update.message.reply_text(context.user_data['lang'][LANGUAGE_CHOSEN])
    if message_text == 'Кыргызча':
        set_language_dict_for_user(context, 'kg')
        update.message.reply_text(context.user_data['lang'][LANGUAGE_CHOSEN])
    else:
        update.message.reply_text(context.user_data['lang'][LANGUAGE_CHOSEN])
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text(context.user_data['lang'][BOT_HELP])


def help_video(update, context):
    update.message.reply_text(context.user_data['lang'][BOT_VIDEO_HELP])


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.info('Adding bot handlers...')

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler(CHANGE_LANGUAGE_COMMAND, change_lang), ],
        states={HANDLE_CHANGE_LANG: [MessageHandler(Filters.text, handle_change_lang)], },
        fallbacks=[CommandHandler(CANCEL_COMMAND, cancel)]
    ))
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
