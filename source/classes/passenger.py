class Passenger:
    FULL_NAME_MAX_LENGTH = 100

    def __init__(self, full_name):
        self.full_name = full_name
        self.pin = None

    def __str__(self):
        return '{} {}'.format(self.full_name, self.pin)

    def __repr__(self):
        return '{} {}'.format(self.full_name, self.pin)

    def is_complete(self):
        return all([self.full_name, self.pin])
