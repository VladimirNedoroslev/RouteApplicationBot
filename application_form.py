class ApplicationForm:

    def __init__(self):
        self.reason = None
        self.start_time = None
        self.end_time = None
        self.destination_longitude = None
        self.destination_latitude = None

    def is_complete(self) -> bool:
        return  all([self.reason, self.start_time, self.end_time, self.destination_longitude, self.destination_latitude])

    def __str__(self):
        return 'reason={}, start_time={}, end_time={}, destination'.format(self.reason, self.start_time, self.end_time,
                                                                           self.destination_longitude,
                                                                           self.destination_latitude)
