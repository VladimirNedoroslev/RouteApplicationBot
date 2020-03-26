class ApplicationOrganizationForm:
    def __init__(self):
        self.reason = None
        self.organization_name = None
        self.organization_tin = None
        self.car_number = None,
        self.car_info = None
        self.passengers = []
        self.start_location = None
        self.destination = None
        self.start_time = None
        self.end_time = None

    def is_complete(self) -> bool:
        return all([self.reason, self.organization_name, self.organization_tin, self.car_number, self.car_info,
                    self.passengers, self.start_location, self.destination, self.start_time, self.end_time])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'reason = {}, organization = {} {}, car = {} {}, passengers = {} start_location = {}, destination = {}, start_time = {}, end_time = {}'.format(
            self.reason,
            self.organization_name,
            self.organization_tin, self.car_number, self.car_info, self.passengers, self.start_location,
            self.destination,
            self.start_time,
            self.end_time)


class Passenger:

    def __init__(self):
        self.full_name = None
        self.pin = None

    def __str__(self):
        return 'Passenger: {} {}'.format(self.full_name, self.pin)
