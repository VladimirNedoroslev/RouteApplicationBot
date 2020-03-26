class ApplicationForm:

    def __init__(self):
        self.user_id = None
        self.reason = None
        self.start_time = None
        self.end_time = None
        self.start_location = None
        self.destination = None

    def is_complete(self) -> bool:
        return all([self.user_id, self.reason, self.start_time, self.end_time, self.start_location,
                    self.destination])

    def reset(self):
        self.__init__()

    def __str__(self):
        return 'user_id = {} reason={}, start_time={}, end_time={}, start_location = {} destination = {}'.format(
            self.user_id, self.reason,
            self.start_time, self.end_time,
            self.start_location,
            self.destination)
