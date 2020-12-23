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
