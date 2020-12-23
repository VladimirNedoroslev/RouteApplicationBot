class RegistrationForm:
    PIN_LENGTH = 14
    FULL_NAME_MAX_LENGTH = 50

    def __init__(self):
        self.pin = None
        self.full_name = None
        self.phone_number = None

    def is_complete(self) -> bool:
        return all([self.pin, self.full_name, self.phone_number])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'pin = {}, name = {}, phone number = {}'.format(self.pin, self.full_name,
                                                               self.phone_number)