import json
import logging

from pip._vendor import requests

from db_operations import get_user
from settings import API_ADDRESS

PIN_REQUEST_FIELD = 'pin'
FULLNAME_REQUEST_FIELD = 'fullName'
PHONE_NUMBER_REQUEST_FIELD = 'phoneNumber'
ADDRESS_REQUEST_FIELD = 'address'
DESTINATION_REQUEST_FIELD = 'destinationAddressesList'
START_TIME_REQUEST_FIELD = 'startTime'
END_TIME_REQUEST_FIELD = 'endTime'
REASON_REQUEST_FIELD = 'tripPurpose'
ORGANIZATION_TIN_REQUEST_FIELD = 'organizationTin'
ORGANIZATION_NAME_REQUEST_FIELD = 'organizationName'
CAR_STATE_NUMBER_REQUEST_FIELD = 'carStateNumber'
CAR_INFORMATION_REQUEST_FIELD = 'carInformation'
PASSENGERS_REQUEST_FIELD = 'passengersList'

REQUEST_HEADERS = {'Content-type': 'application/json'}


def send_organization_application_and_get_response(user_id: str, application):
    json_body = json.dumps(get_application_organization_query_body(user_id, application))
    logging.info('sending organization_application({}) to {}'.format(json_body, API_ADDRESS))
    response = requests.post(API_ADDRESS, data=json_body, headers=REQUEST_HEADERS)
    logging.info(
        'response: status_code = {}, content = {}'.format(response.status_code, response.content.decode("utf-8")))
    return response


def send_application_and_get_response(user_id: str, application):
    json_body = json.dumps(get_application_query_body(user_id, application))
    logging.info('sending application({}) to {}'.format(json_body, API_ADDRESS))
    response = requests.post(API_ADDRESS, data=json_body, headers=REQUEST_HEADERS)
    logging.info(
        'response: status_code = {}, content = {}'.format(response.status_code, response.content.decode("utf-8")))
    return response


def get_application_query_body(user_id, application):
    user_info = get_user(user_id)
    return {
        PIN_REQUEST_FIELD: user_info[0],
        FULLNAME_REQUEST_FIELD: user_info[1],
        PHONE_NUMBER_REQUEST_FIELD: user_info[2],
        REASON_REQUEST_FIELD: application.reason,
        ADDRESS_REQUEST_FIELD: application.start_location,
        DESTINATION_REQUEST_FIELD: [application.destination],
        START_TIME_REQUEST_FIELD: application.start_time.isoformat(),
        END_TIME_REQUEST_FIELD: application.end_time.isoformat(),
    }


def get_application_organization_query_body(user_id, application):
    result = get_application_query_body(user_id, application)
    result[ORGANIZATION_TIN_REQUEST_FIELD] = application.organization_tin
    result[ORGANIZATION_NAME_REQUEST_FIELD] = application.organization_name
    result[CAR_STATE_NUMBER_REQUEST_FIELD] = application.car_number
    result[CAR_INFORMATION_REQUEST_FIELD] = application.car_info
    result[PASSENGERS_REQUEST_FIELD] = []
    for passenger in application.passengers:
        result[PASSENGERS_REQUEST_FIELD].append(passenger_to_query_dict(passenger))
    return result


def passenger_to_query_dict(passenger):
    return {PIN_REQUEST_FIELD: passenger.pin,
            FULLNAME_REQUEST_FIELD: passenger.full_name}
