import logging
import re
from datetime import datetime

import telegram
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from application_sender import send_organization_application_and_get_response
from create_application_flow import ApplicationForm
from db_operations import user_exists_in_users
from qr_coder import get_qrcode_from_string
from settings import USER_DATA_APPLICATION_ORGANIZATION_FORM, REASONS, TELEGRAM_BOT_TOKEN, INPUT_TIME_REGEX


class ApplicationOrganizationForm(ApplicationForm):
    def __init__(self):
        super().__init__()
        self.organization_name = None
        self.organization_tin = None
        self.car_number = None,
        self.car_info = None
        self.passengers = []

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

    def __init__(self, full_name):
        self.fullName = full_name
        self.pin = None

    def __str__(self):
        return '{} {}'.format(self.fullName, self.pin)

    def __repr__(self):
        return '{} {}'.format(self.fullName, self.pin)


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
        logging.info("User %s (id = %s) has started a new organization application", user, user.id)
        update.message.reply_text(
            'Вы начали составление маршрутного листа для организации. Выберите причину выхода. Если Вашей причины нет в списке, '
            'то укажите её самостоятельно. Для отмены используйте команду /cancel',
            reply_markup=ReplyKeyboardMarkup(REASONS))

        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM] = ApplicationOrganizationForm()
        return REASON


def reason(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].reason = message_text
    logging.info("Reason of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(
        'Напишите наименование Вашей организации', reply_markup=ReplyKeyboardRemove())
    return ORGANIZATION_NAME


def organization_name(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].organization_name = message_text
    logging.info("Organization name of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(
        'Теперь напишите ИНН Вашей организации (14 цифр)', )
    return ORGANIZATION_TIN


def organization_tin(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    if len(message_text) != 14:
        update.message.reply_text('ИНН должен быть длиной 14 цифр. Попробуйте ещё раз')
        return ORGANIZATION_TIN
    if not message_text.isnumeric():
        update.message.reply_text('ИНН содержит недопустимые символы. Попробуйте ещё раз ')
        return ORGANIZATION_TIN

    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].organization_tin = message_text
    logging.info("Organization tin of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(
        'Хорошо, теперь введита номер Вашей машины', )
    return CAR_NUMBER


def car_number(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].car_number = message_text
    logging.info("Car number of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(
        'Супер! Какая у Вашей машины марка и модель?', )
    return CAR_INFORMATION


def car_information(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    user = update.message.from_user
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].car_info = message_text
    logging.info("Car information of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(
        'Теперь нужно ввести данные граждан, которые будут с вами следовать на машине (пассажиры).\n'
        'Напишите ФИО пасскажира.\n\n'
        'Если у Вас не будет пассажиров или вы уже всех указали, то используйте команду /skip.', )
    return PASSENGERS_NAME


def passenger_name(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    if message_text == '/skip':
        return skip_passengers(update, context)

    user = update.message.from_user
    logging.info("Passenger name of %s (id = %s): %s", user.first_name, user.id, message_text)
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].passengers.append(Passenger(message_text))
    update.message.reply_text(
        'Напишите ПИН пассажира (персональный идентификационный номер) он указан в паспорте (14 цифр)')
    return PASSENGERS_PIN


def passenger_pin(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    if message_text == '/skip':
        return skip_passengers(update, context)
    if len(message_text) != 14:
        update.message.reply_text('Персональный номер должен быть длиной 14 цифр. Попробуйте ещё раз')
        return PASSENGERS_PIN
    if not message_text.isnumeric():
        update.message.reply_text('Ваш персональный номер содержит недопустимые символы. Попробуйте ещё раз ')
        return PASSENGERS_PIN

    user = update.message.from_user
    logging.info("Passenger pin of %s (id = %s): %s", user.first_name, user.id, message_text)

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].passengers[-1].pin = message_text
    update.message.reply_text(
        'Отлично! Вы добавили пассажира к маршрутному листу.\n'
        'Напишите ФИО следующего пассажира.\n\n'
        'Если у Вас больше не будет пассажиров, то используйте команду /skip')
    return PASSENGERS_NAME


def skip_passengers(update, context):
    update.message.reply_text('Напишите ваш текущий адрес')
    return START_LOCATION


def application_start_location(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_location = message_text

    user = update.message.from_user
    logging.info("Start location of %s (id = %s): %s", user.first_name, user.id, message_text)
    update.message.reply_text('Теперь напишите адрес, куда Вы направляетесь', )
    return DESTINATION


def destination(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].destination = message_text

    user = update.message.from_user
    logging.info("Destination of %s (id = %s): %s", user.first_name, user.id,
                 context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].destination)

    update.message.reply_text(
        'Когда Вы планируете выйти? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)',
        parse_mode=ParseMode.HTML)
    return START_TIME


def application_start_time(update, context):
    user = update.message.from_user
    try:
        message_text = update.message.text
        if len(message_text) != 5:
            raise ValueError
        input_time = datetime.strptime(message_text, "%H.%M")
        start_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)

        if start_time < datetime.now():
            update.message.reply_text('Вы указали время меньше текущего')
            return START_TIME

        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_time = start_time
        logging.info("Start time of %s (id = %s): %s", user.first_name, user.id, message_text)
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
        message_text = update.message.text
        if len(message_text) != 5:
            raise ValueError
        input_time = datetime.strptime(message_text, "%H.%M")

        end_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)
        if end_time < context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_time:
            update.message.reply_text('Время прибытия не может быть меньше времени выхода')
            return END_TIME
        elif end_time == context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_time:
            update.message.reply_text('Время прибытия не может быть равным времени выхода')
            return END_TIME
        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].end_time = end_time
        logging.info("End time of %s (id = %s): %s", user.first_name, user.id, message_text)

        application_form = context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM]
        passengers = get_passengers(application_form.passengers)
        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text(
            "Ваш маршрутный лист почти готов. Проверьте Ваши данные.\n<b>Причина</b>: {},\n<b>Название "
            "организации</b>: {}\n<b>ИНН организации</b>: {}\n<b>Номер машины</b>: {}\n<b>Марка и модель машины</b>: "
            "{}\n<b>Пассажиры</b>: {}\n<b>Место нахождения</b>: {}\n<b>Пункт назначения</b>: {}\n<b>Время выхода</b>: {},\n<b>Время возвращения</b>: {}".
                format(application_form.reason,
                       application_form.organization_name,
                       application_form.organization_tin,
                       application_form.car_number,
                       application_form.car_info,
                       passengers,
                       application_form.start_location,
                       application_form.destination,
                       application_form.start_time,
                       application_form.end_time),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard),
            parse_mode=ParseMode.HTML)

        update.message.reply_text('Всё ли верно? (да/нет)')
        return CHECK_APPLICATION
    except ValueError as exception:
        update.message.reply_text('Пожалуйста укажите время в формате ЧЧ.ММ (например <b>23.45</b> или <b>15.20</b>)',
                                  parse_mode=ParseMode.HTML)
        return END_TIME


def get_passengers(passengers):
    if not passengers:
        return '<i>нет пассажиров</i>'
    str_list = []
    for passenger in passengers:
        str_list.append(passenger.__str__())
    return ', '.join(str_list)


def check_application(update, context):
    if update.message.text.lower() == 'да':
        update.message.reply_text('Ваш маршрутный лист создан. Генерирую QR-код...',
                                  reply_markup=ReplyKeyboardRemove()
                                  )

        response = send_organization_application_and_get_response(str(update.message.from_user.id),
                                                                  context.user_data[
                                                                      USER_DATA_APPLICATION_ORGANIZATION_FORM])
        if response.status_code != 200:
            update.message.reply_text('Упс, извините, у меня не получается сгенерировать QR-код. Но я исправлюсь!')
            return ConversationHandler.END
        qr_code = get_qrcode_from_string(response.content)
        bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
        chat_id = update.effective_chat.id
        bot.send_photo(chat_id, photo=qr_code, caption='Ваш QR-код для проверки маршуртного листа')
        user = update.message.from_user
        logging.info("User %s (id = %s) has finished organization application_form.", user.first_name, user.id)
    else:
        update.message.reply_text(
            'Вы можете снова составить маршрутный лист для организации через команду /create_org_app',
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
            PASSENGERS_NAME: [MessageHandler(Filters.text, passenger_name),
                              CommandHandler('skip', skip_passengers)],
            PASSENGERS_PIN: [MessageHandler(Filters.text, passenger_pin),
                             CommandHandler('skip', skip_passengers)],
            START_LOCATION: [MessageHandler(Filters.text, application_start_location)],
            DESTINATION: [MessageHandler(Filters.text, destination)],
            START_TIME: {MessageHandler(Filters.regex(INPUT_TIME_REGEX), application_start_time)},
            END_TIME: [MessageHandler(Filters.regex(INPUT_TIME_REGEX), application_end_time)],
            CHECK_APPLICATION: [
                MessageHandler(Filters.regex(re.compile(r'^(да|нет)$', re.IGNORECASE)), check_application)],
        },
        fallbacks={CommandHandler('cancel', cancel)}
    )
