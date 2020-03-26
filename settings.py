DB_SETTINGS = {
    'dbname': 'route_app_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432',
}
LOG_FORMAT = '%(levelname) -5s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s'
LOG_TIME_FORMAT = '%d/%m/%Y %H:%M:%S'

INPUT_TIME_REGEX = '^([0-9][0-9])\.([0-9][0-9])$'

API_ADDRESS = 'https://ml.tunduk.kg/Applications/Create'

REVERSE_GEOCODING_API_KEY = ''
REVERSE_GEOCODING_API_ADDRESS = ''

TELEGRAM_BOT_TOKEN = '1064566811:AAHsSkqPK7Sc4G8xUJursc099BO2YH52pdA'

USER_DATA_REGISTRATION_FORM = 'registration_form'
USER_DATA_APPLICATION_FORM = 'application_form'
USER_DATA_APPLICATION_ORGANIZATION_FORM = 'application_organization_form'
USER_DATA_PASSENGERS = 'passengers'

REASONS = [["Перевозка лекарственных средств"],
           ["Оказание медицинских услуг"],
           ["Перевозка товаров первой необходимости"],
           ["Транспортировка граждан"],
           ["Осуществление охранных функций"],
           ["Коммунальные услуги"],
           ["Личные дела"],
           ]