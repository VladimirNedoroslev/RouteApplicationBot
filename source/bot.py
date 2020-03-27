import logging
from datetime import date

from telegram import ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler)

from create_application_flow import get_create_application_conversation_handler
from create_application_organization_flow import get_create_organization_application_conversation_handler
from db_operations import save_new_user_to_db, check_database
from registration_flow import get_registration_conversation_handler
from settings import TELEGRAM_BOT_TOKEN, LOG_TIME_FORMAT, LOG_FORMAT

COMMANDS_TEXT = """Мне доступны следующие команды:
/change_lang - изменить язык
/register - зарегистрироваться
/change_info - изменить информацию о себе
/create_app - составить маршрутный лист для физического лица
/create_org_app - составить маршрутный лист для юридических лиц
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
    dispatcher.add_handler(CommandHandler('change_lang', change_lang))
    dispatcher.add_handler(CommandHandler('commands', commands))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('help_video', help_video))

    dispatcher.add_handler(get_registration_conversation_handler())
    dispatcher.add_handler(get_create_application_conversation_handler())
    dispatcher.add_handler(get_create_organization_application_conversation_handler())

    dispatcher.add_error_handler(error)
    logging.info('Finished adding handlers, starting polling...')

    updater.start_polling()
    logging.info('Bot polling has been started!')
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(filename='{}_{}.log'.format(__file__, date.today()), level=logging.INFO, format=LOG_FORMAT,
                        datefmt=LOG_TIME_FORMAT)
    check_database()
    main()
