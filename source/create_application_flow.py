# -*- coding: utf-8 -*-

import logging
import re
from datetime import datetime

import telegram
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from bot_messages import APP_START, APP_START_NO_REGISTER, REASON_LENGTH_ERROR, CURRENT_ADDRESS_PROMPT, \
    ADDRESS_LENGTH_ERROR, \
    DESTINATION_ADDRESS_PROMPT, START_TIME_PROMPT, START_TIME_LESS_ERROR, END_TIME_PROMPT, TIME_FORMAT_ERROR, \
    END_TIME_EQUALS_ERROR, \
    APP_READY, IS_CORRECT, GENERATING_QR_CODE, QR_CODE_CAPTION, APP_AGAIN, APP_CANCEL, YES_NO_REPLY_KEYBOARD, \
    APP_REASONS
from classes.application_form import ApplicationForm
from db_operations import user_exists
from qr_coder import get_qrcode_from_string
from settings import USER_DATA_APPLICATION_FORM, TELEGRAM_BOT_TOKEN, CHECK_RESPONSE_REGEX, CANCEL_COMMAND, \
    CREATE_APPLICATION_COMMAND
from utilities import is_cancel_command, exceeds_max_length, set_language_dict_for_user

REASON = 'reason'
START_LOCATION = 'start_location'
DESTINATION = 'destination'
START_TIME = 'start_time'
END_TIME = 'end_time'
CHECK_APPLICATION = 'check_application'


def create_application(update, context):
    set_language_dict_for_user(context)
    user_id = str(update.message.from_user.id)
    if user_exists(user_id):
        user = update.message.from_user
        logging.info("User %s (id = %s) has started a new application", user, user_id)
        update.message.reply_text(context.user_data['lang'][APP_START],
                                  reply_markup=ReplyKeyboardMarkup(context.user_data['lang'][APP_REASONS]))

        context.user_data[USER_DATA_APPLICATION_FORM] = ApplicationForm()
        return REASON
    else:
        update.message.reply_text(context.user_data['lang'][APP_START_NO_REGISTER])
        return ConversationHandler.END


def ask_reason(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationForm.REASON_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][REASON_LENGTH_ERROR])
        return REASON
    context.user_data[USER_DATA_APPLICATION_FORM].reason = message_text

    user = update.message.from_user
    logging.info("Reason of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][CURRENT_ADDRESS_PROMPT], reply_markup=ReplyKeyboardRemove())
    return START_LOCATION


def ask_start_location(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationForm.LOCATION_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][ADDRESS_LENGTH_ERROR])
        return START_LOCATION

    context.user_data[USER_DATA_APPLICATION_FORM].start_location = message_text

    user = update.message.from_user
    logging.info("Start location of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][DESTINATION_ADDRESS_PROMPT])
    return DESTINATION


def ask_destination(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, ApplicationForm.LOCATION_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][ADDRESS_LENGTH_ERROR])
        return DESTINATION

    context.user_data[USER_DATA_APPLICATION_FORM].destination = message_text

    user = update.message.from_user
    logging.info("Destination of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][START_TIME_PROMPT], parse_mode=ParseMode.HTML)
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
            update.message.reply_text(context.user_data['lang'][START_TIME_LESS_ERROR])
            return START_TIME

        context.user_data[USER_DATA_APPLICATION_FORM].start_time = start_time

        user = update.message.from_user
        logging.info("Start time of %s (id = %s): %s", user.first_name, user.id, message_text)

        update.message.reply_text(context.user_data['lang'][END_TIME_PROMPT], parse_mode=ParseMode.HTML)
        return END_TIME
    except ValueError:
        update.message.reply_text(context.user_data['lang'][TIME_FORMAT_ERROR], parse_mode=ParseMode.HTML)
        return START_TIME


def ask_end_time(update, context):
    try:
        message_text = update.message.text
        if is_cancel_command(message_text):
            return cancel(update, context)
        if len(message_text) != 5:
            raise ValueError
        input_time = datetime.strptime(message_text, "%H.%M")

        end_time = datetime.now().replace(hour=input_time.hour, minute=input_time.minute, second=0, microsecond=0)

        if end_time < context.user_data[USER_DATA_APPLICATION_FORM].start_time:
            update.message.reply_text(context.user_data['lang'][START_TIME_LESS_ERROR])
            return END_TIME
        elif end_time == context.user_data[USER_DATA_APPLICATION_FORM].start_time:
            update.message.reply_text(context.user_data['lang'][END_TIME_EQUALS_ERROR])
            return END_TIME

        context.user_data[USER_DATA_APPLICATION_FORM].end_time = end_time

        user = update.message.from_user
        logging.info("End time of %s (id = %s): %s", user.first_name, user.id, message_text)

        application_form = context.user_data[USER_DATA_APPLICATION_FORM]

        reply_keyboard = context.user_data['lang'][YES_NO_REPLY_KEYBOARD]
        update.message.reply_text(
            context.user_data['lang'][APP_READY].format(
                application_form.reason,
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


def ask_check_application(update, context):
    possible_yes_answers = ('da', 'да', 'ooba', 'ооба', 'yes')
    message_text = update.message.text.lower()
    if message_text in possible_yes_answers:
        update.message.reply_text(context.user_data['lang'][GENERATING_QR_CODE], reply_markup=ReplyKeyboardRemove())

        # response = send_application_and_get_response(str(update.message.from_user.id),
        #                                              context.user_data[USER_DATA_APPLICATION_FORM])

        # if response.status_code == 200:
        qr_code = get_qrcode_from_string("998879716137645217594579474123264")
        bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
        chat_id = update.effective_chat.id
        bot.send_photo(chat_id, photo=qr_code, caption=context.user_data['lang'][QR_CODE_CAPTION])
        user = update.message.from_user
        logging.info("User %s (id = %s) has finished application_form.", user.first_name, user.id)
        # else:
        #     if response.status_code == 503:
        #         update.message.reply_text('Извините, сейчас я не могу сгенерировать Ваш QR-код, попробуйте позже')
        #         return ConversationHandler.END
        #     update.message.reply_text('Извините, у меня не получается сгенерировать QR-код. Но я исправлюсь!')

    update.message.reply_text(context.user_data['lang'][APP_AGAIN], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(context.user_data['lang'][APP_CANCEL], reply_markup=ReplyKeyboardRemove())
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
