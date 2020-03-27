# -*- coding: utf-8 -*-

import logging
import re
from datetime import datetime

import telegram
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from application_sender import send_application_and_get_response
from db_operations import user_exists
from qr_coder import get_qrcode_from_string
from settings import USER_DATA_APPLICATION_FORM, REASONS, TELEGRAM_BOT_TOKEN, CHECK_RESPONSE_REGEX, CANCEL_COMMAND, \
    REGISTRATION_COMMAND, CREATE_APPLICATION_COMMAND, SKIP_COMMAND


class ApplicationForm:

    def __init__(self):
        self.reason = None
        self.start_location = None
        self.destination = None
        self.start_time = None
        self.end_time = None

    def is_complete(self) -> bool:
        return all([self.reason, self.start_time, self.end_time, self.start_location,
                    self.destination])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'reason={}, start_time={}, end_time={}, start_location = {} destination = {}'.format(self.reason,
                                                                                                    self.start_time,
                                                                                                    self.end_time,
                                                                                                    self.start_location,
                                                                                                    self.destination)


def is_cancel_command(message_text):
    if message_text == '/{}'.format(CANCEL_COMMAND):
        return True
    return False


def is_skip_command(message_text):
    if message_text == '/{}'.format(SKIP_COMMAND):
        return True
    return False


REASON = 'reason'
START_LOCATION = 'start_location'
DESTINATION = 'destination'
START_TIME = 'start_time'
END_TIME = 'end_time'
CHECK_APPLICATION = 'check_application'


def create_application(update, context):
    user_id = str(update.message.from_user.id)
    if user_exists(user_id):
        user = update.message.from_user
        logging.info("User %s (id = %s) has started a new application", user, user_id)
        update.message.reply_text(
            'Вы начали составление маршрутного листа. Выберите причину выхода. Если Вашей причины нет в списке, '
            'то укажите её самостоятельно. Для отмены используйте команду /{}'.format(CANCEL_COMMAND),
            reply_markup=ReplyKeyboardMarkup(REASONS))

        context.user_data[USER_DATA_APPLICATION_FORM] = ApplicationForm()
        return REASON
    else:
        update.message.reply_text('Вы не можете составлять маршрутные листы пока не закончите регистрацию. Для этого '
                                  'выполните команду /{}.'.format(REGISTRATION_COMMAND))
        return ConversationHandler.END


def ask_reason(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    context.user_data[USER_DATA_APPLICATION_FORM].reason = message_text

    user = update.message.from_user
    logging.info("Reason of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text('Напишите ваш текущий адрес', reply_markup=ReplyKeyboardRemove())
    return START_LOCATION


def ask_start_location(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)

    context.user_data[USER_DATA_APPLICATION_FORM].start_location = message_text

    user = update.message.from_user
    logging.info("Start location of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text('Теперь напишите адрес, куда Вы направляетесь', )
    return DESTINATION


def ask_destination(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)

    context.user_data[USER_DATA_APPLICATION_FORM].destination = message_text

    user = update.message.from_user
    logging.info("Destination of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(
        'Когда Вы планируете выйти? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)',
        parse_mode=ParseMode.HTML)
    return START_TIME


def ask_start_time(update, context):
    try:
        message_text = update.message.text
        if is_cancel_command(message_text):
            return cancel(update, context)
        if len(message_text) != 5:
            raise ValueError

        current_time = datetime.now()
        input_time = datetime.strptime(message_text, "%H.%M")
        start_time = current_time.replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)
        if start_time.minute != current_time.minute and start_time < current_time:
            update.message.reply_text('Вы указали время меньше текущего')
            return START_TIME

        context.user_data[USER_DATA_APPLICATION_FORM].start_time = start_time

        user = update.message.from_user
        logging.info("Start time of %s (id = %s): %s", user.first_name, user.id, message_text)

        update.message.reply_text(
            'Когда Вы планируете вернуться? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)',
            parse_mode=ParseMode.HTML)
        return END_TIME
    except ValueError:
        update.message.reply_text('Пожалуйста укажите время в формате ЧЧ.ММ (например <b>23.45</b> или <b>15.20</b>)',
                                  parse_mode=ParseMode.HTML)
        return START_TIME


def ask_end_time(update, context):
    try:
        message_text = update.message.text
        if is_cancel_command(message_text):
            return cancel(update, context)
        if len(message_text) != 5:
            raise ValueError
        input_time = datetime.strptime(message_text, "%H.%M")

        end_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0,
                                          microsecond=0)

        if end_time < context.user_data[USER_DATA_APPLICATION_FORM].start_time:
            update.message.reply_text('Время прибытия не может быть меньше времени выхода')
            return END_TIME
        elif end_time == context.user_data[USER_DATA_APPLICATION_FORM].start_time:
            update.message.reply_text('Время прибытия не может быть равным времени выхода')
            return END_TIME

        context.user_data[USER_DATA_APPLICATION_FORM].end_time = end_time

        user = update.message.from_user
        logging.info("End time of %s (id = %s): %s", user.first_name, user.id, message_text)

        application_form = context.user_data[USER_DATA_APPLICATION_FORM]

        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text(
            'Ваш маршрутный лист почти готов. Проверьте Ваши данные.\n'
            '<b>Причина</b>: {},\n<b>Место нахождения</b>: {},\n<b>Пункт назначения</b>: {},\n<b>Дата выхода</b>: {},'
            '\n<b>Дата возвращения</b>: {}'.format(
                application_form.reason,
                application_form.start_location,
                application_form.destination,
                application_form.start_time,
                application_form.end_time),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard),
            parse_mode=ParseMode.HTML)

        update.message.reply_text('Всё ли верно? (да/нет)')
        return CHECK_APPLICATION
    except ValueError:
        update.message.reply_text('Пожалуйста укажите время в формате ЧЧ.ММ (например <b>23.45</b> или <b>15.20</b>)',
                                  parse_mode=ParseMode.HTML)
        return END_TIME


def ask_check_application(update, context):
    message_text = update.message.text.lower()
    if message_text == 'да' or message_text == 'da':

        update.message.reply_text('Ваш маршрутный лист составлен! Генерирую QR-код...',
                                  reply_markup=ReplyKeyboardRemove())

        response = send_application_and_get_response(str(update.message.from_user.id),
                                                     context.user_data[USER_DATA_APPLICATION_FORM])

        if response.status_code == 200:
            qr_code = get_qrcode_from_string(response.content)
            bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
            chat_id = update.effective_chat.id
            bot.send_photo(chat_id, photo=qr_code, caption='Ваш QR-код для проверки маршуртного листа')
            user = update.message.from_user
            logging.info("User %s (id = %s) has finished application_form.", user.first_name, user.id)
        else:
            if response.status_code == 503:
                update.message.reply_text('Извините, сейчас я не могу сгенерировать Ваш QR-код, попробуйте позже')
                return ConversationHandler.END
            update.message.reply_text('Извините, у меня не получается сгенерировать QR-код. Но я исправлюсь!')

    update.message.reply_text(
        'Вы можете снова составить маршрутный лист через команду /{}'.format(CREATE_APPLICATION_COMMAND),
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(
        'Вы отменили составление маршрутного листа. Вы можете составить маршрутный лист через команду /{}'.format(
            CREATE_APPLICATION_COMMAND),
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def get_create_application_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler(CREATE_APPLICATION_COMMAND, create_application), ],
        states={
            REASON: [MessageHandler(Filters.text, ask_reason)],
            START_LOCATION: [MessageHandler(Filters.text, ask_start_location)],
            DESTINATION: [MessageHandler(Filters.text, ask_destination)],
            START_TIME: [MessageHandler(Filters.text, ask_start_time)],
            END_TIME: [MessageHandler(Filters.text, ask_end_time)],
            CHECK_APPLICATION: [
                MessageHandler(Filters.regex(re.compile(CHECK_RESPONSE_REGEX, re.IGNORECASE)), ask_check_application)],

        },
        fallbacks=[CommandHandler(CANCEL_COMMAND, cancel)]
    )
