from classes.application_form import ApplicationForm


class ApplicationOrganizationForm(ApplicationForm):
    ORGANIZATION_NAME_MAX_LENGTH = 200
    CAR_NUMBER_MAX_LENGTH = 10
    CAR_INFO_MAX_LENGTH = 50

    def __init__(self):
        super().__init__()
        self.organization_name = None
        self.organization_tin = None
        self.car_number = None,
        self.car_info = None
        self.passengers = []

    def is_complete(self) -> bool:
        return all([super().is_complete(), self.organization_name, self.organization_tin, self.car_number,
                    self.car_info, self.passengers])

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