from bot_messages import AVAILABLE_LANGUAGES
from settings import CANCEL_COMMAND, SKIP_COMMAND


def is_cancel_command(message_text):
    if message_text == '/{}'.format(CANCEL_COMMAND):
        return True
    return False


def is_skip_command(message_text):
    if message_text == '/{}'.format(SKIP_COMMAND):
        return True
    return False


def exceeds_max_length(message_text, max_length):
    return len(message_text) > max_length


def set_language_dict_for_user(context, lang='ru'):
    context.user_data['lang'] = AVAILABLE_LANGUAGES[lang]
