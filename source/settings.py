DB_SETTINGS = {
    'dbname': 'route_app_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432',
}
LOG_FORMAT = '%(levelname) -5s %(asctime)s %(name) -15s %(funcName) -15s %(lineno) -5d: %(message)s'
LOG_TIME_FORMAT = '%d/%m/%Y %H:%M:%S'

API_ADDRESS = 'https://ml.tunduk.kg/Applications/Create'

CHECK_RESPONSE_REGEX = r'^(да|нет|da|net|ооба|ooba|жок|jok)$'

TELEGRAM_BOT_TOKEN = '1464220430:AAFh8gbv7hk8teZJB8U3hkYRSs_akwXvShs'

HELP_COMMAND = 'help'
HELP_VIDEO_COMMAND = 'help_video'
CREATE_APPLICATION_COMMAND = 'create_app'
CREATE_ORGANIZATION_APPLICATION_COMMAND = 'create_org_app'
CHANGE_LANGUAGE_COMMAND = 'change_lang'
REGISTRATION_COMMAND = 'register'
CHANGE_INFO_COMMAND = 'change_info'
CANCEL_COMMAND = 'cancel'
SKIP_COMMAND = 'skip'
VIEW_COMMANDS_COMMAND = 'commands'

USER_DATA_REGISTRATION_FORM = 'registration_form'
USER_DATA_APPLICATION_FORM = 'application_form'
USER_DATA_APPLICATION_ORGANIZATION_FORM = 'application_organization_form'
USER_DATA_PASSENGERS = 'passengers'
