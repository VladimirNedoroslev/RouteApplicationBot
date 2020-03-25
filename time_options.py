from datetime import datetime, timedelta


class TimeOptions:
    LESS_THAN_HOUR = "до 1 часа"
    ONE_TO_THREE_HOURS = "до 1-3 часа"
    THREE_TO_SIX_HOURS = "3-6 часов"
    MORE_THAN_SIX_HOURS = "более 6 часов"

    OPTIONS = [LESS_THAN_HOUR, ONE_TO_THREE_HOURS, THREE_TO_SIX_HOURS, MORE_THAN_SIX_HOURS]
