DB_SETTINGS = {
    'dbname': 'route_app_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432',
}
LOG_FORMAT = '%(levelname) -5s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s'
LOG_TIME_FORMAT = '%d/%m/%Y %H:%M:%S'

API_ADDRESS = 'https://ml.tunduk.kg/Applications/Create'

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
           ["Другое"],
           ]

REASON_ID = {
    "Перевозка лекарственных средств": 0,
    "Оказание медицинских услуг": 1,
    "Перевозка товаров первой необходимости": 2,
    "Транспортировка граждан": 3,
    "Осуществление охранных функций": 4,
    "Коммунальные услуги": 5,
    "Личные дела": 6,
    "Другое": 7,
}
