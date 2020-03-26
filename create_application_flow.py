import logging
import re
from datetime import datetime

import telegram
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from application_sender import send_application_and_get_url
from db_operations import user_exists_in_users
from qr_coder import get_qrcode_from_string
from settings import USER_DATA_APPLICATION_FORM, REASONS, TELEGRAM_BOT_TOKEN, INPUT_TIME_REGEX


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


REASON = 1
START_LOCATION = 2
DESTINATION = 3
START_TIME = 4
END_TIME = 5
CHECK_APPLICATION = 6


def create_application(update, context):
    user_id = str(update.message.from_user.id)
    if not user_exists_in_users(user_id):
        update.message.reply_text(
            'Вы не можете составлять маршрутные листы пока не закончите регистрацию.'
            'Для этого выполните команду /register.')
        return ConversationHandler.END
    else:
        user = update.message.from_user
        logging.info("User %s (id = %s) has started a new application", user, user.id)
        update.message.reply_text(
             'Вы начали составление маршрутного листа. Выберите причину выхода. Если Вашей причины нет в списке, '
            'то укажите её самостоятельно. Для отмены используйте команду /cancel',
            reply_markup=ReplyKeyboardMarkup(REASONS))

        context.user_data[USER_DATA_APPLICATION_FORM] = ApplicationForm()
        return REASON


def application_reason(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_FORM].reason = message_text
    logging.info("Reason of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(
        'Укажите геолокацию, где Вы находитесь. (Нажмите на скрепку, выберите "Геолокация" и укажите на карте Ваше местоположение)',
        reply_markup=ReplyKeyboardRemove())
    return START_LOCATION


def application_start_location(update, context):
    user = update.message.from_user
    start_location = update.message.location
    context.user_data[USER_DATA_APPLICATION_FORM].start_location = start_location

    logging.info("Start location of %s (id = %s): %s", user.first_name, user.id, start_location)
    update.message.reply_text(
        'Теперь укажите геолокацию места, куда Вы направлятесь. (так же, как и в предыдущем шаге)', )
    return DESTINATION


def application_destination(update, context):
    user = update.message.from_user
    destination = update.message.location
    context.user_data[USER_DATA_APPLICATION_FORM].destination = destination

    logging.info("Destination of %s (id = %s): %s", user.first_name, user.id, destination)

    update.message.reply_text(
        'Когда Вы планируете выйти? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)',
        parse_mode=ParseMode.HTML)
    return START_TIME


def application_start_time(update, context):
    user = update.message.from_user
    try:
        input_time = datetime.strptime(update.message.text, "%H.%M")
        start_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0,
                                            microsecond=0).isoformat()
        context.user_data[USER_DATA_APPLICATION_FORM].start_time = start_time

        logging.info("Start time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

        update.message.reply_text(
            'Когда Вы планируете вернуться? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)',
            parse_mode=ParseMode.HTML)
        return END_TIME
    except ValueError as exception:
        update.message.reply_text('Пожалуйста укажите время в формате ЧЧ.ММ (например <b>23.45</b> или <b>15.20</b>)',
                                  parse_mode=ParseMode.HTML)
        return START_TIME


def application_end_time(update, context):
    user = update.message.from_user
    try:
        input_time = datetime.strptime(update.message.text, "%H.%M")
        end_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0,
                                          microsecond=0).isoformat()
        context.user_data[USER_DATA_APPLICATION_FORM].end_time = end_time
        logging.info("End time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

        application_form = context.user_data[USER_DATA_APPLICATION_FORM]

        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text(
            'Ваш маршрутный лист почти готов. Проверьте Ваши данные.\n'
            '<b>Причина</b>: {},\n<b>Дата выхода</b>: {},\n<b>Дата возвращения</b>: {}'.format(application_form.reason,
                                                                                               application_form.start_time,
                                                                                               application_form.end_time),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard),
            parse_mode=ParseMode.HTML)
        bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
        chat_id = update.effective_chat.id

        update.message.reply_text('Место нахождения:')
        bot.send_location(chat_id, location=application_form.start_location)

        update.message.reply_text('Место направления:')
        bot.send_location(chat_id, location=application_form.destination)

        update.message.reply_text('Всё ли верно? (да/нет)')
        return CHECK_APPLICATION
    except ValueError as exception:
        update.message.reply_text('Пожалуйста укажите время в формате ЧЧ.ММ (например <b>23.45</b> или <b>15.20</b>)',
                                  parse_mode=ParseMode.HTML)
        return END_TIME


def check_application(update, context):
    if update.message.text.lower() == 'да':
        update.message.reply_text('Ваш маршрутный лист создан. Генерирую QR-код...',
                                  reply_markup=ReplyKeyboardRemove())

        url = send_application_and_get_url(str(update.message.from_user.id),
                                           context.user_data[USER_DATA_APPLICATION_FORM])
        qr_code = get_qrcode_from_string(url)
        bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
        chat_id = update.effective_chat.id
        update.message.reply_text('Ваш QR-код для проверки маршуртного листа.')
        bot.send_photo(chat_id, photo=qr_code)
        user = update.message.from_user
        logging.info("User %s (id = %s) has finished application_form.", user.first_name, user.id)
    else:
        update.message.reply_text(
            'Вы можете снова создать маршрутный лист через команду /create_app',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(
        'Вы прервали создание заяки. Для того чтобы заполнить заявку введите команду /create_app.',
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def get_create_application_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('create_app', create_application), ],
        states={
            REASON: [MessageHandler(Filters.text, application_reason)],
            START_LOCATION: [MessageHandler(Filters.location, application_start_location)],
            DESTINATION: [MessageHandler(Filters.location, application_destination)],
            START_TIME: [MessageHandler(Filters.regex(INPUT_TIME_REGEX), application_start_time)],
            END_TIME: [MessageHandler(Filters.regex(INPUT_TIME_REGEX), application_end_time)],
            CHECK_APPLICATION: [
                MessageHandler(Filters.regex(re.compile(r'^(да|нет)$', re.IGNORECASE)), check_application)],

        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
