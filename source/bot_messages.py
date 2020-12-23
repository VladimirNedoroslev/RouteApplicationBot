from classes.application_form import ApplicationForm
from classes.application_organization_form import ApplicationOrganizationForm
from classes.passenger import Passenger
from classes.registration_form import RegistrationForm

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

COMMANDS = "commands"
HELLO = "hello"
ERROR = "error"
APP_START = "app_start"
APP_START_NO_REGISTER = "app_start_no_register"
REASON_LENGTH_ERROR = "reason_length_error"
CURRENT_ADDRESS_PROMPT = "current_address"
DESTINATION_ADDRESS_PROMPT = "destination_address"
ADDRESS_LENGTH_ERROR = "address_length_error"
START_TIME_PROMPT = "start_time"
START_TIME_LESS_ERROR = "time_less_error"
END_TIME_PROMPT = "end_time"
END_TIME_LESS_ERROR = "end_time_less_error"
END_TIME_EQUALS_ERROR = "end_time_equals_error"
APP_READY = "app_ready"
IS_CORRECT = "is_correct"
TIME_FORMAT_ERROR = "time_format"
APP_AGAIN = "app_again"
APP_CANCEL = "app_cancel"
CHANGE_INFO_START = "change_info_start"
REGISTER_START = "register_start"
NAME_PROMPT = "name_prompt"
NAME_LENGTH_ERROR = "name_length_error"
REGISTER_PIN = "register_pin"
PIN_LENGTH_ERROR = "pin_length_error"
PIN_FORMAT_ERROR = "pin_format_error"
SEND_PHONE = "send_phone"
PHONE_PROMPT = "phone_prompt"
REGISTER_FINISH = "register_finish"
REGISTER_ERROR = "register_error"
CHANGE_INFO_INTERRUPTED = "change_info_interrupted"
REGISTER_INTERRUPTED = "register_interrupted"
GENERATING_QR_CODE = "generating_qr_code"
QR_CODE_CAPTION = "qr_code"
QR_CODE_API_ERROR = "qr_code_api_error"
QR_CODE_BOT_ERROR = "qr_code_bot_error"
BOT_HELP = "bot_help"
BOT_VIDEO_HELP = "bot_video_help"
ORGANIZATION_APP_START = "organization_app_start"
NOT_REGISTERED_ERROR = "not_registered_error"
ORGANIZATION_NAME_PROMPT = "organization_name"
ORGANIZATION_NAME_LENGTH_ERROR = "organization_name_length_error"
ORGANIZATION_TIN_PROMPT = "organization_tin_prompt"
TIN_LENGTH_ERROR = "tin_length_error"
TIN_FORMAT_ERROR = "tin_format_error"
CAR_NUMBER_PROMPT = "car_number_prompt"
CAR_NUMBER_LENGTH_ERROR = "car_number_length_error"
CAR_TYPE_PROMPT = "car_type_prompt"
CAR_TYPE_LENGTH_ERROR = "car_type_length_error"
PASSENGERS_PROMPT = "passengers_prompt"
PASSENGER_NAME_LENGTH_ERROR = "passenger_name_length_error"
PASSENGER_PIN_PROMPT = "passenger_pin_prompt"
PASSENGER_ADDED = "passenger_added"
ORGANIZATION_APP_READY = "organization_app_ready"
NO_PASSENGERS = "no_passengers"
ORGANIZATION_APP_AGAIN = "organization_app_again"
ORGANIZATION_APP_CANCEL = "organization_app_cancel"
LANGUAGE_CHOSEN = 'language_chosen'
CHOOSE_LANGUAGE_PROMPT = 'choose_language_prompt'
YES_NO_REPLY_KEYBOARD = 'yes_no_reply_keyboard',
LANGUAGE_NOT_SUPPORTED = "language_not_supported"
APP_REASONS = "app_reasons"

RUSSIAN_MESSAGES = {
    COMMANDS: """Мне доступны следующие команды:\n/{} - зарегистрироваться\n/{} - изменить язык \n/{} - изменить информацию о себе\n/{} - составить маршрутный лист для физического лица\n/{} - составить маршрутный лист для ридических лиц\n/{} - как работать с этим чат ботом\n/{} - видео-инструкция\n/{} - посмотреть список команд\n/{} - отменить текущую операцию\n/{} - пропустить шаг, если возможно""".format(
        REGISTRATION_COMMAND,
        CHANGE_LANGUAGE_COMMAND,
        CHANGE_INFO_COMMAND,
        CREATE_APPLICATION_COMMAND,
        CREATE_ORGANIZATION_APPLICATION_COMMAND,
        HELP_COMMAND,
        HELP_VIDEO_COMMAND,
        VIEW_COMMANDS_COMMAND,
        CANCEL_COMMAND,
        SKIP_COMMAND),
    HELLO: """Привет, я могу помочь вам с сотавлением электронных маршрутных листов.\n{}""",
    ERROR: """Я наткнулся на небольшую техническую неполадку, когда хотел ответить на эту команду. Извиняюсь, но я не смогу её обработать.""",
    APP_START: """Вы начали составление маршрутного листа. Выберите причину выхода. Если Вашей причины нет в списке, то укажите её самостоятельно. Для отмены используйте команду /{}""".format(
        CANCEL_COMMAND),
    APP_START_NO_REGISTER: """Вы не можете составлять маршрутные листы пока не закончите регистрацию. Для этого выполните команду /{}.""".format(
        REGISTRATION_COMMAND),
    REASON_LENGTH_ERROR: """Описывая причину вы превысили допустимое количество символов (не более {} символов)""".format(
        ApplicationForm.REASON_MAX_LENGTH),
    CURRENT_ADDRESS_PROMPT: """Напишите ваш текущий адрес""",
    DESTINATION_ADDRESS_PROMPT: """Теперь напишите адрес, куда вы направляетесь""",
    ADDRESS_LENGTH_ERROR: """Пожалуйста напишите адрес в пределах {} символов""".format(
        ApplicationForm.LOCATION_MAX_LENGTH),
    START_TIME_PROMPT: """Когда вы планируете выйти? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>""",
    START_TIME_LESS_ERROR: """Вы указали время меньше текущего""",
    END_TIME_PROMPT: """Когда вы планируете вернуться? (Укажите в формате ЧЧ.ММ, например <b>23.45</b> или <b>15.20</b>)""",
    END_TIME_LESS_ERROR: """Время прибытия не может быть меньше времени выхода""",
    END_TIME_EQUALS_ERROR: """Время прибытия не может быть равным времени выхода""",
    APP_READY: """Ваш маршрутный лист почти готов. Проверьте ваши данные.\n<b>Причина</b>: {},\n<b>Место нахождения</b>: {},\n<b>Пункт назначения</b>: {},\n<b>Дата выхода</b>: {},\n<b>Дата возвращения</b>: {}""",
    IS_CORRECT: """Всё ли верно? (да / нет)""",
    TIME_FORMAT_ERROR: """Пожалуйста укажите время в формате ЧЧ.ММ (например <b>23.45</b> или <b>15.20</b>)""",
    APP_AGAIN: """Вы можете снова составить маршрутный лист через команду /{}""".format(CREATE_APPLICATION_COMMAND),
    APP_CANCEL: """Вы отменили составление маршрутного листа. Вы можете составить маршрутный лист через команду /{}""".format(
        CREATE_APPLICATION_COMMAND),
    CHANGE_INFO_START: """Вы начали процесс изменения своих данных. Для отмены используйте команду /{}""".format(
        CANCEL_COMMAND),
    REGISTER_START: """Вы начали процесс регистрации. Для отмены используйте команду /{}""".format(CANCEL_COMMAND),
    NAME_PROMPT: """Пожалуйста введите ваше ФИО.""",
    NAME_LENGTH_ERROR: """Если Ваше ФИО длиннее {} символов, то напишите его сокращённо""".format(
        RegistrationForm.FULL_NAME_MAX_LENGTH),
    REGISTER_PIN: """Хорошо, {}, Теперь введите ваш ПИН (персональный идентификационный номер) он указан в паспорте (14 цифр)""",
    PIN_LENGTH_ERROR: """Персональный номер должен быть длиной 14 цифр. Попробуйте ещё раз""",
    PIN_FORMAT_ERROR: """Персональный номер содержит недопустимые символы. Попробуйте ещё раз""",
    SEND_PHONE: """Отправить свой номер телефона""",
    PHONE_PROMPT: """Мне осталось узнать ваш номер телефона - для этого нажмите на кнопку "Отправить свой номер телефона".
\nЕсли вы не видите кнопку, то нажмите на иконку слева от скрепки в поле ввода сообщений. """,
    REGISTER_FINISH: """Отлично, всё готово! Теперь Вы можете создавать маршрутные листы через команды:\n/{} - для физических лиц\n/{} - для юридических лиц""".format(
        CREATE_APPLICATION_COMMAND,
        CREATE_ORGANIZATION_APPLICATION_COMMAND),
    REGISTER_ERROR: """При Вашей регистрации произошла ошибка. Попробуйте позже.""",
    CHANGE_INFO_INTERRUPTED: """Вы прервали процесс изменения своих данных. Запустить его снова можно через команду /{}""".format(
        CHANGE_INFO_COMMAND),
    REGISTER_INTERRUPTED: """Вы прервали регистрацию. Пока вы не заполните все данные, Вы не сможете заполнять заявки. Начать регистрацию можно через команду /{}""".format(
        REGISTRATION_COMMAND),
    GENERATING_QR_CODE: """Ваш маршрутный лист составлен! Генерирую QR-код...""",
    QR_CODE_CAPTION: """Ваш QR-код для проверки маршуртного листа""",
    QR_CODE_API_ERROR: """Извините, сейчас я не могу сгенерировать Ваш QR-код, попробуйте позже""",
    QR_CODE_BOT_ERROR: """Извините, у меня не получается сгенерировать QR-код. Но я исправлюсь!""",
    BOT_HELP: """Тут будет инструкция по работе с ботом.""",
    BOT_VIDEO_HELP: """Тут будет видео-инструкция по работе с ботом.""",
    ORGANIZATION_APP_START: """Вы начали составление маршрутного листа для организации. Выберите причину выхода. Если вашей причины нет в списке, то укажите её самостоятельно. Для отмены используйте команду /{}""".format(CANCEL_COMMAND),
    NOT_REGISTERED_ERROR: """Вы не можете составлять маршрутные листы пока не закончите регистрацию. Для этого выполните команду /{}.""".format(REGISTRATION_COMMAND),
    ORGANIZATION_NAME_PROMPT: """Напишите наименование вашей организации""",
    ORGANIZATION_NAME_LENGTH_ERROR: """Если название Вашей организации превышает {} символов, то напишите его в краткой форме.""".format(
                ApplicationOrganizationForm.ORGANIZATION_NAME_MAX_LENGTH),
    ORGANIZATION_TIN_PROMPT: """Теперь напишите ИНН Вашей организации (14 цифр)""",
    TIN_LENGTH_ERROR: """ИНН должен быть длиной 14 цифр. Попробуйте ещё раз""",
    TIN_FORMAT_ERROR: """ИНН содержит недопустимые символы. Попробуйте ещё раз""",
    CAR_NUMBER_PROMPT: """Хорошо, теперь введите номер вашей машины""",
    CAR_NUMBER_LENGTH_ERROR: """Номер машины должен быть в пределах {} символов""".format(ApplicationOrganizationForm.CAR_NUMBER_MAX_LENGTH),
    CAR_TYPE_PROMPT: """Супер! Какая у Вашей машины марка и модель?""",
    CAR_TYPE_LENGTH_ERROR: """Если марка и модель Вашей машины превышает {} символов, то напишите их в краткой форме""".format(
                ApplicationOrganizationForm.CAR_INFO_MAX_LENGTH),
    PASSENGERS_PROMPT: """Теперь нужно ввести данные граждан, которые будут с вами следовать на машине (пассажиры).\nНапишите ФИО пасскажира\nЕсли у вас не будет пассажиров или вы уже всех указали, то используйте команду /{}""".format(SKIP_COMMAND),
    PASSENGER_NAME_LENGTH_ERROR: """Если ФИО пассажира превышает {} символов, то напишите его сокращенно""".format(
            Passenger.FULL_NAME_MAX_LENGTH),
    PASSENGER_PIN_PROMPT: """Напишите ПИН пассажира (персональный идентификационный номер) он указан в паспорте (14 цифр)""",
    PASSENGER_ADDED: """Отлично! Вы добавили пассажира к маршрутному листу.\nНапишите ФИО следующего пассажира.\nЕсли у Вас больше не будет пассажиров, то используйте команду /{}""".format(SKIP_COMMAND),
    ORGANIZATION_APP_READY: """Ваш маршрутный лист почти готов. Проверьте Ваши данные.\n<b>Причина</b>: {},\n<b>Название организации</b>: {},\n<b>ИНН организации</b>: {},\n<b>Номер машины</b>: {},\n<b>Марка и модель машины</b>: {},\n<b>Пассажиры</b>: {},\n<b>Место нахождения</b>: {},\n<b>Пункт назначения</b>: {},\n<b>Время выхода</b>: {},\n<b>Время возвращения</b>: {}""",
    NO_PASSENGERS: """<i>нет пассажиров</i>""",
    ORGANIZATION_APP_AGAIN: """Вы можете снова составить маршрутный лист для юридического лица через команду /{}""".format(
            CREATE_ORGANIZATION_APPLICATION_COMMAND),
    ORGANIZATION_APP_CANCEL: """Вы отменили составления маршрутного листа для юридического лица. Вы можете составить маршрутный лист для юридического лица через команду /{}""".format(CREATE_ORGANIZATION_APPLICATION_COMMAND),
    CHOOSE_LANGUAGE_PROMPT: "Выберите язык",
    LANGUAGE_CHOSEN: "Ваш язык русский",
    YES_NO_REPLY_KEYBOARD: [["Да", "Нет"]],
    LANGUAGE_NOT_SUPPORTED: "Такой язык не поддерживается",
    APP_REASONS: [["Перевозка лекарственных средств"],
                  ["Оказание медицинских услуг"],
                  ["Перевозка товаров первой необходимости"],
                  ["Транспортировка граждан"],
                  ["Осуществление охранных функций"],
                  ["Коммунальные услуги"],
                  ["Личные дела"],
                  ]
}

KYRGYZ_MESSAGES = {
    COMMANDS: """Мага төмөнкү буйруктар жеткиликтүү:\n/{} - тилди өзгөртүү\n/{} - катталуу\n/{} - өзү жөнүндө маалыматты өзгөртүү\n/{} - жеке жактар үчүн маршруттук баракты түзүү\n/{} - юридикалык жактар үчүн маршруттук баракты түзүү\n/{} - бул чат бот менен кантип иштөө керек\n/{} - видео-нускама\n/{} - катышуучулардын тизмесин көрүү\n/{} - учурдагы операцияны токтотуу\n/{} - эгер мүмкүн болсо, кадамды өткөрүп жиберүү""".format(
        REGISTRATION_COMMAND,
        CHANGE_LANGUAGE_COMMAND,
        CHANGE_INFO_COMMAND,
        CREATE_APPLICATION_COMMAND,
        CREATE_ORGANIZATION_APPLICATION_COMMAND,
        HELP_COMMAND,
        HELP_VIDEO_COMMAND,
        VIEW_COMMANDS_COMMAND,
        CANCEL_COMMAND,
        SKIP_COMMAND),
    HELLO: """Саламатсызбы, мен сизге электрондук маршруттук баракчаларын даярдоодо жардам бере алам.\n{}""",
    ERROR: """Бул буйрукка жооп берээр алдында бир аз техникалык көйгөйгө туш болдум. Кечиресиз, бирок мен аны иштете албайм.""",
    APP_START: """Сиз маршруттук баракты түзүүнү баштадыңыз. Чыгуунун себебин тандаңыз. Сиздин себебиңиз тизмеде жок болсо, анда аны өз алдынча көрсөтүүңүз. Жокко чыгаруу үчүн /{} командасын колдонуңуз""".format(
        CANCEL_COMMAND),
    APP_START_NO_REGISTER: """Катталууну аягына чыкмайынча, сиз маршрут баракчаларын түзө албайсыз. Ал үчүн /{} буйругун аткарыңыз.""".format(
        REGISTRATION_COMMAND),
    REASON_LENGTH_ERROR: """Себебин сүрөттөп жатып сиз символдордун мүмкүн болгон санынан ашып кеттиңиз ({} символдон көп эмес)""".format(
        ApplicationForm.REASON_MAX_LENGTH),
    CURRENT_ADDRESS_PROMPT: """Учурдагы дарегиңизди жазыңыз""",
    DESTINATION_ADDRESS_PROMPT: """Эми бара турган дарегиңизди жазыңыз""",
    ADDRESS_LENGTH_ERROR: """Сураныч, даректи {} символдон ашпай жазыңыз""".format(
        ApplicationForm.LOCATION_MAX_LENGTH),
    START_TIME_PROMPT: """Кетүүнү качан пландап жатасыз? (КК.АА форматында көрсөтүңүз, мисалы <b>23.45</b> же <b>15.20</b>""",
    START_TIME_LESS_ERROR: """Сиз учурдагыдан аз убакытты көрсөттүңүз""",
    END_TIME_PROMPT: """Кайтып келүүнү качан пландап жатасыз? (Сураныч, КК.АА форматында киргизиңиз, мисалы <b>23.45</b> же <b>15.20</b> )""",
    END_TIME_LESS_ERROR: """Келүү убактысы чыгуу убактысынан аз болушу мүмкүн эмес""",
    END_TIME_EQUALS_ERROR: """Келүү убактысы чыгуу убактысына барабар болушу мүмкүн эмес""",
    APP_READY: """Сиздин маршруттук баракчаңыз дээрлик даяр. Маалыматтарыңызды текшериңиз.\n<b>Себеби</b>: {},\n<b>Жайгашкан жери</b>: {},\n<b>Көздөлгөн жери</b>: {},\n<b>Чыгуу датасы</b>: {},\n<b>Кайтып келүү датасы</b>: {}""",
    IS_CORRECT: """Баары туура бы? (ооба / жок)""",
    TIME_FORMAT_ERROR: """КК.АА форматындагы убакытты көрсөтүңүз (мисалы <b>23.45</b> же <b>15.20</b>)""",
    APP_AGAIN: """Сиз маршруттук баракчаны кайрадан /{} команда аркылуу түзө аласыз""".format(
        CREATE_APPLICATION_COMMAND),
    APP_CANCEL: """Сиз маршруттук баракчаны түзүүнү жокко чыгардыңыз. Сиз /{} команда аркылуу маршруттук баракчасын түзө аласыз """.format(
        CREATE_APPLICATION_COMMAND),
    CHANGE_INFO_START: """Сиз маалыматтарды өзгөртүү процессин баштадыңыз. Жокко чыгаруу үчүн /{} буйругун колдонуңуз""".format(
        CANCEL_COMMAND),
    REGISTER_START: """Сиз каттоо процессин баштадыңыз. Жокко чыгаруу үчүн /{} буйругун колдонуңуз""".format(
        CANCEL_COMMAND),
    NAME_PROMPT: """Сураныч, аты-жөнүңүздү жазыңыз""",
    NAME_LENGTH_ERROR: """Эгер сиздин аты-жөнүңүз {} символдон узак  болсо, анда кыскартылган түрдө жазыңыз""".format(
        RegistrationForm.FULL_NAME_MAX_LENGTH),
    REGISTER_PIN: """Жакшы, {}, эми сиздин ИЖН (идентификациялык жеке номер) киргизиңиз ал паспортто (14 сандуу) көрсөтүлгөн""",
    PIN_LENGTH_ERROR: """Жеке номер 14 сандан турушу керек. Кайрадан аракет кылыңыз""",
    PIN_FORMAT_ERROR: """Жеке номерде жараксыз белгилер камтылган. Кайрадан аракет кылыңыз""",
    SEND_PHONE: """Өз телефон номеримди жөнөтүү""",
    PHONE_PROMPT: """Мага сиздин телефон номериңизди билип алуу калды -бул үчүн "Өз телефон номеримди жөнөтүү" баскычын басыңыз.\nСиз баскычты көрбөй жатсаңыз, анда билдирүү киргизүү талаасындагы кыстырманын сол жагындагы сүрөтчөнү басыңыз""",
    REGISTER_FINISH: """Абдан жакшы, баардыгы даяр! Эми сиз буйрук аркылуу маршруттук баракчаларды түзө аласыз:\n/{} - жеке жактар үчүн\n/{} - юридикалык жактар үчүн""".format(
        CREATE_APPLICATION_COMMAND,
        CREATE_ORGANIZATION_APPLICATION_COMMAND),
    REGISTER_ERROR: """Катталып жатканда ката кетти. Кийинчерээк аракет кылыңыз.""",
    CHANGE_INFO_INTERRUPTED: """Дайындарыңызды өзгөртүү процессин үзгүлтүккө учураттыңыз. / {} Буйругу аркылуу аны кайрадан баштасаңыз болот.""".format(
        CHANGE_INFO_COMMAND),
    REGISTER_INTERRUPTED: """Сиз каттоону жокко чыгардыңыз. Бардык маалыматтарды толтурмайынча, арыздарды толтура албайсыз. / {} Буйругу аркылуу каттоону баштасаңыз болот""".format(
        REGISTRATION_COMMAND),
    GENERATING_QR_CODE: """Сиздин маршруттук баракчаңыз түзүлдү! QR-код жасалууда...""",
    QR_CODE_CAPTION: """Маршруттук баракчаны текшерүү үчүн сиздин QR кодуңуз""",
    QR_CODE_API_ERROR: """""",
    QR_CODE_BOT_ERROR: """""",
    BOT_HELP: """Бул жерде бот менен иштөө боюнча нускама болот.""",
    BOT_VIDEO_HELP: """Бул жерде бот менен иштөө боюнча видео-нускама болот.""",
    ORGANIZATION_APP_START: """Уюм үчүн маршрут баракчасын түзүп баштадыңыз. Кетүүнүн себебин тандаңыз. Эгер сиздин себебиңиз тизмеде жок болсо, анда өзүңүз көрсөтүңүз. Жокко чыгаруу үчүн /{} командасын колдонуңуз""".format(CANCEL_COMMAND),
    NOT_REGISTERED_ERROR: """Катталууну бүткүчө маршрут баракчаларын түзө албайсыз. Ал үчүн /{} буйругун аткарыңыз.""".format(REGISTRATION_COMMAND),
    ORGANIZATION_NAME_PROMPT: """Уюмуңуздун атын жазыңыз""",
    ORGANIZATION_NAME_LENGTH_ERROR: """Эгер уюмуңуздун аталышы {} белгиден ашса, анда аны кыска түрүндө жазыңыз.""".format(
                ApplicationOrganizationForm.ORGANIZATION_NAME_MAX_LENGTH),
    ORGANIZATION_TIN_PROMPT: """Эми уюмуңуздун ИСН жазыңыз (14 сандуу)""",
    TIN_LENGTH_ERROR: """ИСН 14 сандуу болушу керек. Кайра аракет кылыңыз""",
    TIN_FORMAT_ERROR: """ИСН жараксыз белгилерди камтыйт. Кайра аракет кылыңыз""",
    CAR_NUMBER_PROMPT: """Жакшы, эми унаанын номерин киргизиңиз""",
    CAR_NUMBER_LENGTH_ERROR: """Унаанын номери {} белгиден турушу керек""".format(ApplicationOrganizationForm.CAR_NUMBER_MAX_LENGTH),
    CAR_TYPE_PROMPT: """Эң сонун! Сиздин унааңыздын маркасы жана модели кандай?""",
    CAR_TYPE_LENGTH_ERROR: """Эгерде сиздин унааңыздын маркасы жана модели {} белгиден ашса, анда аларды кыска түрүндө жазыңыз""".format(
                ApplicationOrganizationForm.CAR_INFO_MAX_LENGTH),
    PASSENGERS_PROMPT: """Эми сизди унаа менен ээрчиген жарандардын (жүргүнчүлөрдүн) маалыматтарын киргизүү керек.\nЖүргүнчүнүн аты-жөнүн жазыңыз.\nЭгер жүргүнчүңүз жок болсо же алардын бардыгын көрсөткөн болсоңуз, анда /{} буйругун колдонуңуз.""".format(SKIP_COMMAND),
    PASSENGER_NAME_LENGTH_ERROR: """Эгерде жүргүнчүнүн толук аты-жөнү {} белгиден ашса, анда аны кыскартылган түрүндө жазыңыз""",
    PASSENGER_PIN_PROMPT: """Паспортто көрсөтүлгөн жүргүнчүнүн ИЖН кодун ( идентификациялык  жеке номерин) жазыңыз (14 сандуу)""",
    PASSENGER_ADDED: """Сонун! Сиз маршруттук баракчага жүргүнчүнү коштуңуз.\nКийинки жүргүнчүнүн атын толук жазыңыз.\nЭгер жүргүнчү жок болсоңуз, /{} буйругун колдонуңуз""".format(SKIP_COMMAND),
    ORGANIZATION_APP_READY: """Сиздин маршруттук баракчаңыз даяр. Өзүңүздүн маалыматтарыңызды текшерип алыңыз.\n<b>Себеби</b>: {},\n<b>Уюмдун аталышы</b>: {},\n<b>Суюмдун ИСНи</b>: {},\n<b>Машинанын номери</b>: {},\n<b>Машина маркасы жана модели</b>: {}\n<b>Жүргүнчүлөр</b>: {},\n<b>Жайгашкан жери</b>: {},\n<b>Көздөлгөн жери</b>: {},\n<b>Чыгуу убакыты</b>: {},\n<b>Кайтып келүү убакыты</b>: {}""",
    NO_PASSENGERS: """<i>жүргүнчү жок</i>""",
    ORGANIZATION_APP_AGAIN: """/{} Буйругу аркылуу юридикалык жак үчүн маршрут баракчасын дагы түзсөңүз болот""".format(
            CREATE_ORGANIZATION_APPLICATION_COMMAND),
    ORGANIZATION_APP_CANCEL: """Юридикалык жак үчүн каттам баракчасын даярдоону жокко чыгардыңыз. /{} Буйругу аркылуу юридикалык жак үчүн маршрут баракчасын түзсөңүз болот""".format(CREATE_ORGANIZATION_APPLICATION_COMMAND),
    LANGUAGE_CHOSEN: "Сиздин тилиңиз кыргызча",
    CHOOSE_LANGUAGE_PROMPT: "Тил тандаңыз",
    YES_NO_REPLY_KEYBOARD: [["Ооба", "Жок"]],
    LANGUAGE_NOT_SUPPORTED: "Бул тил колдоодо жок",
    APP_REASONS: [["Дары-дармек каражаттарын ташуу"],
                  ["Медициналык кызмат көрсөтүү"],
                  ["Биринчи зарылдыктагы товарларды ташуу"],
                  ["Жарандарды жеткирүү"],
                  ["Коргоо иш-милдеттерин жүзөгө ашыруу"],
                  ["Коммуналдык кызмат көрсөтүүлөр"],
                  ["Жеке иштер"],
                  ]
}

AVAILABLE_LANGUAGES = {
    'ru': RUSSIAN_MESSAGES,
    'kg': KYRGYZ_MESSAGES
}
