import logging
from datetime import datetime
from io import BytesIO

import qrcode
import telegram
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from db_operations import user_exists_in_users
from settings import USER_DATA_APPLICATION_ORGANIZATION_FORM, TELEGRAM_BOT_TOKEN


class ApplicationOrganizationForm:
    def __init__(self):
        self.reason = None
        self.organization_name = None
        self.organization_tin = None
        self.car_number = None,
        self.car_info = None
        self.passengers = []
        self.start_location = None
        self.destination = None
        self.start_time = None
        self.end_time = None

    def is_complete(self) -> bool:
        return all([self.reason, self.organization_name, self.organization_tin, self.car_number, self.car_info,
                    self.passengers, self.start_location, self.destination, self.start_time, self.end_time])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'reason = {}, organization = {} {}, car = {} {}, passengers = {} start_location = {}, destination = {}, start_time = {}, end_time = {}'.format(
            self.reason,
            self.organization_name,
            self.organization_tin, self.car_number, self.car_info, self.passengers, self.start_location,
            self.destination,
            self.start_time,
            self.end_time)


class Passenger:

    def __init__(self):
        self.full_name = None
        self.pin = None

    def __str__(self):
        return 'Passenger: {} {}'.format(self.full_name, self.pin)


REASON = 1

ORGANIZATION_NAME = 2
ORGANIZATION_TIN = 3

CAR_NUMBER = 4
CAR_INFORMATION = 5

PASSENGERS_NAME = 6
PASSENGERS_PIN = 7

START_LOCATION = 8
DESTINATION = 9

START_TIME = 10
END_TIME = 11

CHECK_APPLICATION = 12


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
            'Вы начали создание заявки. Опишите кратко причину выхода. Для отмены используйте команду /cancel')

        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM] = ApplicationOrganizationForm()
        return REASON


def reason(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].reason = update.message.text
    logging.info("Reason of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    update.message.reply_text(
        'Укажите геолокацию, где Вы находитесь. (Нажмите на скрепку, выберите "Геолокация" и укажите на карте Ваше местоположение)', )
    return ORGANIZATION_NAME


def organization_name(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    update.message.reply_text('some text')


def organization_tin(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    update.message.reply_text('some text')


def car_number(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    update.message.reply_text('some text')


def car_information(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    update.message.reply_text('some text')


def passenger_name(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    update.message.reply_text('some text')


def passenger_pin(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    update.message.reply_text('some text')


def application_start_location(update, context):
    user = update.message.from_user
    start_location = update.message.location
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_location = start_location

    logging.info("Start location of %s (id = %s): %s", user.first_name, user.id, start_location)
    update.message.reply_text(
        'Теперь укажите геолокацию места, куда Вы направлятесь. (так же, как и в предыдущем шаге)', )
    return DESTINATION


def destination(update, context):
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].destination = update.message.location

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
        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].application_start_time = start_time

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
        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].end_time = end_time
        logging.info("End time of %s (id = %s): %s", user.first_name, user.id, update.message.text)

        application_form = context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM]

        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text(
            'Ваш маршрутный лист почти готов. Проверьте Ваши данные. Всё верно?\n'
            '<b>Причина</b>: {},\n<b>Дата выхода</b>: {},\n<b>Дата возвращения</b>: {}'.format(application_form.reason,
                                                                                               application_form.application_start_time,
                                                                                               application_form.end_time),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard),
            parse_mode=ParseMode.HTML)
        return CHECK_APPLICATION
    except ValueError as exception:
        update.message.reply_text('Вы ввели неверное время. Попробуйте ещё раз.')
        return END_TIME


def check_application(update, context):
    if update.message.text.lower() == 'да':
        update.message.reply_text('Ваша заявка создана. Ваш QR-код:',
                                  reply_markup=ReplyKeyboardRemove()
                                  )
        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].user_id = str(update.message.from_user.id)
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
    update.message.reply_text('Вы отменили составления заявки для организации.')
    return ConversationHandler.END


def get_create_organization_application_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('create_org_app', create_application), ],
        states={
            REASON: [MessageHandler(Filters.text, reason)],
            ORGANIZATION_NAME: [MessageHandler(Filters.text, organization_name)],
            ORGANIZATION_TIN: [MessageHandler(Filters.text, organization_tin)],
            CAR_NUMBER: [MessageHandler(Filters.text, car_number)],
            CAR_INFORMATION: [MessageHandler(Filters.text, car_information)],
            PASSENGERS_NAME: [MessageHandler(Filters.text, passenger_name)],
            PASSENGERS_PIN: [MessageHandler(Filters.text, passenger_pin)],
            START_LOCATION: [MessageHandler(Filters.location, application_start_location)],
            DESTINATION: [MessageHandler(Filters.location, destination)],
            START_TIME: [MessageHandler(Filters.text, application_start_time)],
            END_TIME: [MessageHandler(Filters.text, application_end_time)],
            CHECK_APPLICATION: [MessageHandler(Filters.text, check_application)],
        },
        fallbacks={CommandHandler('cancel', cancel)}
    )
