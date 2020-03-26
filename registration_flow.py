import logging

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from db_operations import save_or_update_user_information, user_exists_in_users
from settings import USER_DATA_REGISTRATION_FORM


class UserInfo:
    def __init__(self):
        self.user_id = None
        self.pin = None
        self.full_name = None
        self.phone_number = None

    def is_complete(self) -> bool:
        return all([self.user_id, self.pin, self.full_name, self.phone_number])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'id = {}, pin = {}, name = {}, phone number = {}'.format(self.user_id, self.pin, self.full_name,
                                                                        self.phone_number)

    def initialize_with_list(self, string_list):
        self.pin = string_list[1]
        self.full_name = string_list[2]
        self.phone_number = string_list[3]


PIN = 1
FULL_NAME = 2
PHONE_NUMBER = 3


def start_registration(update, context):
    if user_exists_in_users(str(update.message.from_user.id)):
        update.message.reply_text(
            'Вы начали процесс изменения своих данных. Для отмены используйте команду /cancel')
    else:
        update.message.reply_text(
            'Вы начали процесс регистрации. Для отмены используйте команду /cancel.')

    update.message.reply_text('Пожалуйста введите Ваше ФИО.')
    context.user_data[USER_DATA_REGISTRATION_FORM] = UserInfo()

    return FULL_NAME


def full_name(update, context):
    if update.message.text == '/cancel':
        return cancel(update, context)
    user = update.message.from_user
    logging.info("Full name of %s (id = %s): %s", user.first_name, user.id, update.message.text)

    name = update.message.text
    context.user_data[USER_DATA_REGISTRATION_FORM].full_name = name

    update.message.reply_text(
        'Хорошо, {}, Теперь введите ваш ПИН (персональный идентификационный номер) он указан в паспорте (14 цифр)'.format(
            name))

    return PIN


def pin(update, context):
    message_text = update.message.text
    if message_text == '/cancel':
        return cancel(update, context)
    if len(message_text) != 14:
        update.message.reply_text('Персональный номер должен быть длиной 14 символов. Попробуйте ещё раз')
        return PIN
    if not message_text.isnumeric():
        update.message.reply_text('Ваш персональный номер содержит недопустимые символы. Попробуйте ещё раз ')
        return PIN

    user = update.message.from_user
    context.user_data[USER_DATA_REGISTRATION_FORM].pin = message_text
    logging.info("Pin of %s (id = %s): %s", user.first_name, user.id, message_text)

    send_contact_button = KeyboardButton(text="Отправить свой номер телефона", request_contact=True)
    update.message.reply_text(
        'Мне осталось узнать Ваш номер телефона - для этого нажмите на кнопку "Отправить свой номер телефона".',
        reply_markup=ReplyKeyboardMarkup([[send_contact_button]], one_time_keyboard=True))

    return PHONE_NUMBER


def phone_number(update, context):
    user = update.message.from_user
    user_phone_number = update.effective_message.contact.phone_number

    logging.info("Phone number of %s (id = %s): %s", user.first_name, user.id, user_phone_number)
    update.message.reply_text(
        'Отлично, всё готово! Теперь Вы можете создавать заявки через команду /create_app и /create_org_app', )
    context.user_data[USER_DATA_REGISTRATION_FORM].phone_number = user_phone_number
    context.user_data[USER_DATA_REGISTRATION_FORM].user_id = str(update.message.from_user.id)

    logging.info(context.user_data[USER_DATA_REGISTRATION_FORM])
    if context.user_data[USER_DATA_REGISTRATION_FORM].is_complete():
        save_or_update_user_information(context.user_data[USER_DATA_REGISTRATION_FORM])
    return ConversationHandler.END


def cancel(update, context):
    if user_exists_in_users(str(update.message.from_user.id)):
        update.message.reply_text(
            'Вы прервали процесс изменения своих данных. Запустить его снова можно через команду /change_info',
            reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(
            'Вы прервали регистрацию. Пока Вы не заполните все данные, Вы не сможете заполнять заявки. Начать регистрацию можно через команду /register',
            reply_markup=ReplyKeyboardRemove())
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
