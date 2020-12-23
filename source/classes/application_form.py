class ApplicationForm:
    REASON_MAX_LENGTH = 500
    LOCATION_MAX_LENGTH = 100

    def __init__(self):
        self.reason = None
        self.start_location = None
        self.destination = None
        self.start_time = None
        self.end_time = None

    def is_complete(self) -> bool:
        return all([self.reason, self.start_time, self.end_time, self.start_location,
                    self.destination])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'reason={}, start_time={}, end_time={}, start_location = {} destination = {}'.format(
            self.reason, self.start_time, self.end_time, self.start_location, self.destination)