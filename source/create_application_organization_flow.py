import logging
import re
from datetime import datetime

import telegram
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from bot_messages import APP_REASONS, ORGANIZATION_APP_START, NOT_REGISTERED_ERROR, REASON_LENGTH_ERROR, \
    ORGANIZATION_NAME_PROMPT, ORGANIZATION_NAME_LENGTH_ERROR, ORGANIZATION_TIN_PROMPT, TIN_LENGTH_ERROR, \
    TIN_FORMAT_ERROR, CAR_NUMBER_PROMPT, CAR_NUMBER_LENGTH_ERROR, CAR_TYPE_PROMPT, CAR_TYPE_LENGTH_ERROR, \
    PASSENGERS_PROMPT, PASSENGER_NAME_LENGTH_ERROR, PASSENGER_PIN_PROMPT, PIN_LENGTH_ERROR, PIN_FORMAT_ERROR, \
    PASSENGER_ADDED, ADDRESS_LENGTH_ERROR, CURRENT_ADDRESS_PROMPT, DESTINATION_ADDRESS_PROMPT, START_TIME_PROMPT, \
    START_TIME_LESS_ERROR, END_TIME_PROMPT, TIME_FORMAT_ERROR, END_TIME_EQUALS_ERROR, END_TIME_LESS_ERROR, \
    YES_NO_REPLY_KEYBOARD, ORGANIZATION_APP_READY, IS_CORRECT, NO_PASSENGERS, GENERATING_QR_CODE, QR_CODE_CAPTION, \
    ORGANIZATION_APP_AGAIN, ORGANIZATION_APP_CANCEL
from classes.application_organization_form import ApplicationOrganizationForm
from classes.passenger import Passenger
from create_application_flow import ApplicationForm
from db_operations import user_exists
from qr_coder import get_qrcode_from_string
from settings import USER_DATA_APPLICATION_ORGANIZATION_FORM, TELEGRAM_BOT_TOKEN, CHECK_RESPONSE_REGEX, \
    CANCEL_COMMAND, SKIP_COMMAND, CREATE_ORGANIZATION_APPLICATION_COMMAND
from utilities import is_cancel_command, exceeds_max_length, is_skip_command

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
    if user_exists(user_id):
        user = update.message.from_user
        logging.info("User %s (id = %s) has started a new organization application", user, user_id)
        update.message.reply_text(
            context.user_data['lang'][ORGANIZATION_APP_START],
            reply_markup=ReplyKeyboardMarkup(context.user_data['lang'][APP_REASONS]))

        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM] = ApplicationOrganizationForm()
        return REASON
    else:
        update.message.reply_text(context.user_data['lang'][NOT_REGISTERED_ERROR])
        return ConversationHandler.END


def reason(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationOrganizationForm.REASON_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][REASON_LENGTH_ERROR])
        return REASON

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].reason = message_text

    user = update.message.from_user
    logging.info("Reason of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][ORGANIZATION_NAME_PROMPT], reply_markup=ReplyKeyboardRemove())
    return ORGANIZATION_NAME


def organization_name(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationOrganizationForm.ORGANIZATION_NAME_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][ORGANIZATION_NAME_LENGTH_ERROR])
        return ORGANIZATION_NAME
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].organization_name = message_text

    user = update.message.from_user
    logging.info("Organization name of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][ORGANIZATION_TIN_PROMPT])
    return ORGANIZATION_TIN


def organization_tin(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if len(message_text) != 14:
        update.message.reply_text(context.user_data['lang'][TIN_LENGTH_ERROR])
        return ORGANIZATION_TIN
    if not message_text.isnumeric():
        update.message.reply_text(context.user_data['lang'][TIN_FORMAT_ERROR])
        return ORGANIZATION_TIN

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].organization_tin = message_text

    user = update.message.from_user
    logging.info("Organization tin of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][CAR_NUMBER_PROMPT])
    return CAR_NUMBER


def car_number(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationOrganizationForm.CAR_NUMBER_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][CAR_NUMBER_LENGTH_ERROR])
        return CAR_NUMBER

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].car_number = message_text

    user = update.message.from_user
    logging.info("Car number of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][CAR_TYPE_PROMPT])
    return CAR_INFORMATION


def car_information(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationOrganizationForm.CAR_INFO_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][CAR_TYPE_LENGTH_ERROR])
        return CAR_INFORMATION

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].car_info = message_text

    user = update.message.from_user
    logging.info("Car information of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][PASSENGERS_PROMPT], )
    return PASSENGERS_NAME


def passenger_name(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if is_skip_command(message_text):
        return skip_passengers(update, context)
    if exceeds_max_length(message_text, Passenger.FULL_NAME_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][PASSENGER_NAME_LENGTH_ERROR])
        return PASSENGERS_NAME

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].passengers.append(Passenger(message_text))

    user = update.message.from_user
    logging.info("Passenger name of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][PASSENGER_PIN_PROMPT])
    return PASSENGERS_PIN


def passenger_pin(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if is_skip_command(message_text):
        return skip_passengers(update, context)

    if len(message_text) != 14:
        update.message.reply_text(context.user_data['lang'][PIN_LENGTH_ERROR])
        return PASSENGERS_PIN
    if not message_text.isnumeric():
        update.message.reply_text(context.user_data['lang'][PIN_FORMAT_ERROR])
        return PASSENGERS_PIN

    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].passengers[-1].pin = message_text

    user = update.message.from_user
    logging.info("Passenger pin of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][PASSENGER_ADDED])
    return PASSENGERS_NAME


def skip_passengers(update, context):
    update.message.reply_text(context.user_data['lang'][CURRENT_ADDRESS_PROMPT])
    return START_LOCATION


def application_start_location(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationForm.LOCATION_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][ADDRESS_LENGTH_ERROR])
        return START_LOCATION
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_location = message_text

    user = update.message.from_user
    logging.info("Start location of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][DESTINATION_ADDRESS_PROMPT])
    return DESTINATION


def destination(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationForm.LOCATION_MAX_LENGTH):
        update.message.reply_text(
            context.user_data['lang'][ADDRESS_LENGTH_ERROR])
        return DESTINATION
    context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].destination = message_text

    user = update.message.from_user
    logging.info("Destination of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][START_TIME_PROMPT], parse_mode=ParseMode.HTML)
    return START_TIME


def application_start_time(update, context):
    try:
        message_text = update.message.text
        if is_cancel_command(message_text):
            return cancel(update, context)
        if len(message_text) != 5:
            raise ValueError
        current_time = datetime.now()
        input_time = datetime.strptime(message_text, "%H.%M")
        start_time = current_time.replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)

        if current_time.minute != start_time.minute and start_time < current_time:
            update.message.reply_text(context.user_data['lang'][START_TIME_LESS_ERROR])
            return START_TIME

        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_time = start_time

        user = update.message.from_user
        logging.info("Start time of %s (id = %s): %s", user.first_name, user.id, message_text)

        update.message.reply_text(context.user_data['lang'][END_TIME_PROMPT], parse_mode=ParseMode.HTML)
        return END_TIME
    except ValueError:
        update.message.reply_text(context.user_data['lang'][TIME_FORMAT_ERROR], parse_mode=ParseMode.HTML)
        return START_TIME


def application_end_time(update, context):
    try:
        message_text = update.message.text
        if is_cancel_command(message_text):
            return cancel(update, context)
        if len(message_text) != 5:
            raise ValueError

        input_time = datetime.strptime(message_text, "%H.%M")
        end_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)
        if end_time < context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_time:
            update.message.reply_text(context.user_data['lang'][END_TIME_LESS_ERROR])
            return END_TIME
        elif end_time == context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].start_time:
            update.message.reply_text(context.user_data['lang'][END_TIME_EQUALS_ERROR])
            return END_TIME

        context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM].end_time = end_time

        user = update.message.from_user
        logging.info("End time of %s (id = %s): %s", user.first_name, user.id, message_text)

        application_form = context.user_data[USER_DATA_APPLICATION_ORGANIZATION_FORM]
        reply_keyboard = context.user_data['lang'][YES_NO_REPLY_KEYBOARD]
        update.message.reply_text(context.user_data['lang'][ORGANIZATION_APP_READY].format(application_form.reason,
                                                                                           application_form.organization_name,
                                                                                           application_form.organization_tin,
                                                                                           application_form.car_number,
                                                                                           application_form.car_info,
                                                                                           passengers_to_str(context,
                                                                                                             application_form.passengers),
                                                                                           application_form.start_location,
                                                                                           application_form.destination,
                                                                                           application_form.start_time,
                                                                                           application_form.end_time),
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                                  parse_mode=ParseMode.HTML)

        update.message.reply_text(context.user_data['lang'][IS_CORRECT])
        return CHECK_APPLICATION
    except ValueError:
        update.message.reply_text(context.user_data['lang'][TIME_FORMAT_ERROR], parse_mode=ParseMode.HTML)
        return END_TIME


def passengers_to_str(context, passengers):
    if not passengers or (len(passengers) == 1 and not passengers[0].is_complete()):
        return context.user_data['lang'][NO_PASSENGERS]
    str_list = []
    for passenger in passengers:
        if passenger.is_complete():
            str_list.append(passenger.__str__())
    return ', '.join(str_list)


def check_application(update, context):
    possible_yes_answers = ('da', 'да', 'ooba', 'ооба', 'yes')
    message_text = update.message.text.lower()
    if message_text in possible_yes_answers:
        update.message.reply_text(context.user_data['lang'][GENERATING_QR_CODE], reply_markup=ReplyKeyboardRemove())

        # response = send_organization_application_and_get_response(str(update.message.from_user.id),
        #                                                           context.user_data[
        #                                                               USER_DATA_APPLICATION_ORGANIZATION_FORM])
        # if response.status_code == 200:
        qr_code = get_qrcode_from_string("2165798715749124791731745174147")
        bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
        chat_id = update.effective_chat.id
        bot.send_photo(chat_id, photo=qr_code, caption=context.user_data['lang'][QR_CODE_CAPTION])
        user = update.message.from_user
        logging.info("User %s (id = %s) has finished organization application_form.", user.first_name, user.id)
        # else:
        #     if response.status_code == 503:
        #         update.message.reply_text('Извините, сейчас я не могу сгенерировать Ваш QR-код, попробуйте позже')
        #         return ConversationHandler.END
        #     update.message.reply_text('Извините, у меня не получается сгенерировать QR-код. Но я исправлюсь!')

    update.message.reply_text(context.user_data['lang'][ORGANIZATION_APP_AGAIN], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(context.user_data['lang'][ORGANIZATION_APP_CANCEL], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def get_create_organization_application_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler(CREATE_ORGANIZATION_APPLICATION_COMMAND, create_application), ],
        states={
            REASON: [MessageHandler(Filters.text, reason)],
            ORGANIZATION_NAME: [MessageHandler(Filters.text, organization_name)],
            ORGANIZATION_TIN: [MessageHandler(Filters.text, organization_tin)],
            CAR_NUMBER: [MessageHandler(Filters.text, car_number)],
            CAR_INFORMATION: [MessageHandler(Filters.text, car_information)],

            PASSENGERS_NAME: [MessageHandler(Filters.text, passenger_name),
                              CommandHandler(SKIP_COMMAND, skip_passengers)],
            PASSENGERS_PIN: [MessageHandler(Filters.text, passenger_pin),
                             CommandHandler(SKIP_COMMAND, skip_passengers)],

            START_LOCATION: [MessageHandler(Filters.text, application_start_location)],
            DESTINATION: [MessageHandler(Filters.text, destination)],
            START_TIME: {MessageHandler(Filters.text, application_start_time)},
            END_TIME: [MessageHandler(Filters.text, application_end_time)],
            CHECK_APPLICATION: [
                MessageHandler(Filters.regex(re.compile(CHECK_RESPONSE_REGEX, re.IGNORECASE)), check_application)],
        },
        fallbacks={CommandHandler(CANCEL_COMMAND, cancel)}
    )
