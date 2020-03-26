import logging
import re
from datetime import datetime
from io import BytesIO

import qrcode
import telegram
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from db_operations import user_exists_in_users
from settings import USER_DATA_APPLICATION_FORM, TELEGRAM_BOT_TOKEN, REASONS


class ApplicationForm:

    def __init__(self):
        self.user_id = None
        self.reason = None
        self.start_location = None
        self.destination = None
        self.start_time = None
        self.end_time = None

    def is_complete(self) -> bool:
        return all([self.user_id, self.reason, self.start_time, self.end_time, self.start_location,
                    self.destination])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'user_id = {} reason={}, start_time={}, end_time={}, start_location = {} destination = {}'.format(
            self.user_id, self.reason,
            self.start_time, self.end_time,
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
            'Вы начали создание заявки. Выберите причину выхода. Для отмены используйте команду /cancel',
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
        start_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)
        context.user_data[USER_DATA_APPLICATION_FORM].application_start_time = start_time

        logging.info("Start time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

        update.message.reply_text(
            'Когда Вы планируете вернуться? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)',
            parse_mode=ParseMode.HTML)
        return END_TIME
    except ValueError as exception:
        update.message.reply_text('Вы ввели неверное время. Попробуйте ещё раз.')
        return START_TIME


def application_end_time(update, context):
    user = update.message.from_user
    try:
        input_time = datetime.strptime(update.message.text, "%H.%M")
        end_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)
        context.user_data[USER_DATA_APPLICATION_FORM].end_time = end_time
        logging.info("End time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

        registration_form = context.user_data[USER_DATA_APPLICATION_FORM]

        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text(
            'Ваш маршрутный лист почти готов. Проверьте Ваши данные. Всё верно?\n'
            '<b>Причина</b>: {},\n<b>Дата выхода</b>: {},\n<b>Дата возвращения</b>: {}'.format(registration_form.reason,
                                                                                               registration_form.application_start_time,
                                                                                               registration_form.end_time),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard),
            parse_mode=ParseMode.HTML)
        return CHECK_APPLICATION
    except ValueError as exception:
        update.message.reply_text('Вы ввели неверное время. Попробуйте ещё раз.')
        return END_TIME


def check_application(update, context):
    if update.message.text.lower() == 'да':
        update.message.reply_text('Ваша заявка создана. Ваш QR-код:',
                                  reply_markup=ReplyKeyboardRemove())
        context.user_data[USER_DATA_APPLICATION_FORM].user_id = str(update.message.from_user.id)
        # save_application(context.user_data[USER_DATA_APPLICATION_FORM])

        image = qrcode.make('Some QR code')
        chat_id = update.effective_chat.id
        qr_code = BytesIO()
        qr_code.name = 'qr_code.jpeg'
        image.save(qr_code, 'JPEG')
        qr_code.seek(0)
        bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
        bot.send_photo(chat_id, photo=qr_code)

        user = update.message.from_user
        logging.info("User %s (id = %s) has finished application_form.", user.first_name, user.id)
    else:
        update.message.reply_text(
            'Ваша заявка составлена неправильно. Создайте её снова через команду /create_app',
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(
        'Вы прервали создание заяки. Для того чтобы заполнить заявку введите команду /create_app.',
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def get_create_application_conversation_handler():
    input_time_regex = '^([0-9][0-9])\.([0-9][0-9])$'
    return ConversationHandler(
        entry_points=[CommandHandler('create_app', create_application), ],
        states={
            REASON: [MessageHandler(Filters.text, application_reason)],
            START_LOCATION: [MessageHandler(Filters.location, application_start_location)],
            DESTINATION: [MessageHandler(Filters.location, application_destination)],
            START_TIME: [MessageHandler(Filters.regex(input_time_regex), application_start_time)],
            END_TIME: [MessageHandler(Filters.regex(input_time_regex), application_end_time)],
            CHECK_APPLICATION: [
                MessageHandler(Filters.regex(re.compile(r'^(да|нет)$', re.IGNORECASE)), check_application)],

        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
