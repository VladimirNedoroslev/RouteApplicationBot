import logging

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from bot_messages import CHANGE_INFO_START, REGISTER_START, NAME_PROMPT, NAME_LENGTH_ERROR, REGISTER_PIN, \
    PIN_LENGTH_ERROR, PIN_FORMAT_ERROR, SEND_PHONE, PHONE_PROMPT, REGISTER_FINISH, REGISTER_ERROR, \
    CHANGE_INFO_INTERRUPTED, REGISTER_INTERRUPTED
from classes.registration_form import RegistrationForm
from db_operations import save_user, user_exists, update_user
from settings import USER_DATA_REGISTRATION_FORM
from utilities import is_cancel_command, exceeds_max_length

PIN = 1
FULL_NAME = 2
PHONE_NUMBER = 3


def start_registration(update, context):
    user = update.message.from_user
    if user_exists(str(user.id)):
        update.message.reply_text(
            context.user_data['lang'][CHANGE_INFO_START])
    else:
        update.message.reply_text(context.user_data['lang'][REGISTER_START])

    update.message.reply_text(context.user_data['lang'][NAME_PROMPT])
    context.user_data[USER_DATA_REGISTRATION_FORM] = RegistrationForm()

    logging.info("User has started registration process %s (id = %s)", user.first_name, user.id)

    return FULL_NAME


def full_name(update, context):
    message_text = update.message.text
    if is_cancel_command(message_text):
        return cancel(update, context)
    if exceeds_max_length(message_text, RegistrationForm.FULL_NAME_MAX_LENGTH):
        update.message.reply_text(context.user_data['lang'][NAME_LENGTH_ERROR])
        return FULL_NAME
    context.user_data[USER_DATA_REGISTRATION_FORM].full_name = message_text

    user = update.message.from_user
    logging.info("Full name of %s (id = %s): %s", user.first_name, user.id, message_text)

    update.message.reply_text(context.user_data['lang'][REGISTER_PIN].format(message_text))

    return PIN


def pin(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    if len(message_text) != 14:
        update.message.reply_text(context.user_data['lang'][PIN_LENGTH_ERROR])
        return PIN
    if not message_text.isnumeric():
        update.message.reply_text(context.user_data['lang'][PIN_FORMAT_ERROR])
        return PIN

    context.user_data[USER_DATA_REGISTRATION_FORM].pin = message_text

    user = update.message.from_user
    logging.info("Pin of %s (id = %s): %s", user.first_name, user.id, message_text)

    send_contact_button = KeyboardButton(text=context.user_data['lang'][SEND_PHONE], request_contact=True)
    update.message.reply_text(context.user_data['lang'][PHONE_PROMPT],
                              reply_markup=ReplyKeyboardMarkup([[send_contact_button]]))

    return PHONE_NUMBER


def phone_number(update, context):
    user_phone_number = update.effective_message.contact.phone_number

    context.user_data[USER_DATA_REGISTRATION_FORM].phone_number = user_phone_number

    update.message.reply_text(context.user_data['lang'][REGISTER_FINISH], reply_markup=ReplyKeyboardRemove())

    user = update.message.from_user
    logging.info("Phone number of %s (id = %s): %s", user.first_name, user.id, user_phone_number)

    if context.user_data[USER_DATA_REGISTRATION_FORM].is_complete():
        user_id = str(update.message.from_user.id)
        if user_exists(user_id):
            update_user(user_id, context.user_data[USER_DATA_REGISTRATION_FORM])
        else:
            chat_id = update.effective_chat.id
            save_user(user_id, chat_id, context.user_data[USER_DATA_REGISTRATION_FORM])

    else:
        update.message.reply_text(context.user_data['lang'][REGISTER_ERROR])
    return ConversationHandler.END


def cancel(update, context):
    if user_exists(str(update.message.from_user.id)):
        update.message.reply_text(context.user_data['lang'][CHANGE_INFO_INTERRUPTED],
                                  reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(context.user_data['lang'][REGISTER_INTERRUPTED], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def get_registration_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('register', start_registration),
                      CommandHandler('change_info', start_registration)],
        states={
            PIN: [MessageHandler(Filters.text, pin)],
            FULL_NAME: [MessageHandler(Filters.text, full_name)],
            PHONE_NUMBER: [MessageHandler(Filters.contact, phone_number)],
        },
        fallbacks={CommandHandler('cancel', cancel)}
    )
