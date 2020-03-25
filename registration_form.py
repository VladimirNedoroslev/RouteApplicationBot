class RegistrationForm:
    def __init__(self):
        self.user_id = None
        self.family_name = None
        self.given_name = None
        self.middle_name = None
        self.phone_number = None
        self.address_longitude = None
        self.address_latitude = None

    def is_complete(self) -> bool:
        return all([self.user_id, self.family_name, self.middle_name, self.given_name, self.phone_number,
                    self.address_longitude,
                    self.address_latitude])

    def reset(self):
        self.user_id = None
        self.family_name = None
        self.given_name = None
        self.middle_name = None
        self.phone_number = None
        self.address_longitude = None
        self.address_latitude = None

    def __str__(self):
        return 'id = {}, name = {} {} {}, phone number = {}, address = {} {}'.format(self.user_id, self.family_name,
                                                                                     self.given_name, self.middle_name,
                                                                                     self.phone_number,
                                                                                     self.address_longitude,
                                                                                     self.address_latitude)
