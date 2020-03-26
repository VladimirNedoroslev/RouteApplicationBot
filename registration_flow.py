import logging
from enum import Enum

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler

from db_operations import save_or_update_user_information
from registration_form import RegistrationForm
from settings import USER_DATA_REGISTRATION_FORM


class RegistrationFlow(Enum):
    PIN = 1
    FAMILY_NAME = 2
    GIVEN_NAME = 3
    MIDDLE_NAME = 4
    PHONE_NUMBER = 5
    ADDRESS = 6
    CAR_STATE_NUMBER = 7
    CAR_INFORMATION = 8
    ORGANIZATION_TIN = 9
    ORGANIZATION_NAME = 10


def start_registration(update, context):
    update.message.reply_text(
        'Вы начали процесс регистрации. Для отмены используйте команду /cancel.\nПожалуйста введите вашу фамилию. ')

    return RegistrationFlow.FAMILY_NAME


def family_name(update, context):
    user = update.message.from_user
    context.user_data[USER_DATA_REGISTRATION_FORM] = RegistrationForm()
    context.user_data[USER_DATA_REGISTRATION_FORM].family_name = update.message.text
    logging.info("Family Name of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    update.message.reply_text('Введите ваше имя')
    return RegistrationFlow.GIVEN_NAME


def given_name(update, context):
    user = update.message.from_user
    context.user_data[USER_DATA_REGISTRATION_FORM].given_name = update.message.text
    logging.info("Given Name of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    update.message.reply_text('Введите ваше отчество')
    return RegistrationFlow.MIDDLE_NAME


def middle_name(update, context):
    user = update.message.from_user
    logging.info("Middle name of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    context.user_data[USER_DATA_REGISTRATION_FORM].middle_name = update.message.text

    send_contact_button = KeyboardButton(text="Отправить свой номер телефона", request_contact=True)
    reg_form = context.user_data[USER_DATA_REGISTRATION_FORM]
    name = '{} {} {}'.format(reg_form.family_name, reg_form.given_name, reg_form.middle_name)
    update.message.reply_text(
        'Хорошо, {}, теперь мне нужен Ваш номер телефона - для этого нажмите на кнопку "Отправить свой номер телефона".'.format(
            name),
        reply_markup=ReplyKeyboardMarkup([[send_contact_button]], one_time_keyboard=True))

    logging.info(context.user_data[USER_DATA_REGISTRATION_FORM])
    return RegistrationFlow.PHONE_NUMBER


def phone_number(update, context):
    user = update.message.from_user
    user_phone_number = update.effective_message.contact.phone_number

    logging.info("Phone number of %s (id = %s): %s", user.first_name, user.id, user_phone_number)
    update.message.reply_text(
        'Отлично, Ваша регистрация завершена! Теперь Вы можете создать заявку через команду /create_app', )
    context.user_data[USER_DATA_REGISTRATION_FORM].phone_number = user_phone_number
    context.user_data[USER_DATA_REGISTRATION_FORM].user_id = str(update.message.from_user.id)
    logging.info(context.user_data[USER_DATA_REGISTRATION_FORM])
    if context.user_data[USER_DATA_REGISTRATION_FORM].is_complete():
        save_or_update_user_information(context.user_data[USER_DATA_REGISTRATION_FORM])
    return ConversationHandler.END


# def address(update, context):
#     user = update.message.from_user
#     user_address = update.message.location
#
#     logger.info("Address of %s (id = %s): %s", user.first_name, user.id, user_address)
#     context.user_data[USER_DATA_REGISTRATION_FORM].address_longitude = user_address.longitude
#     context.user_data[USER_DATA_REGISTRATION_FORM].address_latitude = user_address.latitude
#     context.user_data[USER_DATA_REGISTRATION_FORM].user_id = str(update.message.from_user.id)
#     if context.user_data[USER_DATA_REGISTRATION_FORM].is_complete():
#         save_or_update_user_information(context.user_data[USER_DATA_REGISTRATION_FORM])
#     update.message.reply_text(
#         '')
#
#     logger.info(context.user_data[USER_DATA_REGISTRATION_FORM])
#
#     return ConversationHandler.END


def cancel_registration(update, context):
    update.message.reply_text(
        'Вы прервали регистрацию. Пока Вы не заполните все данные, Вы не сможете заполнять заявки. Начать регистрацию можно через команду /start',
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
