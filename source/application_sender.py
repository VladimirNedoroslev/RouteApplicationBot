import json
import logging

from pip._vendor import requests

from db_operations import get_user_info
from settings import API_ADDRESS


def send_organization_application_and_get_response(user_id: str, application):
    json_body = json.dumps(get_application_organization_query_body(user_id, application))
    headers = {'Content-type': "application/json"}
    logging.info('sending organization_application({}) to {}'.format(json_body, API_ADDRESS))
    response = requests.post(API_ADDRESS, data=json_body, headers=headers)
    logging.info(
        'response: status_code = {}, content = {}'.format(response.status_code, response.content.decode("utf-8")))
    return response


def send_application_and_get_response(user_id: str, application):
    json_body = json.dumps(get_application_query_body(user_id, application))
    headers = {'Content-type': "application/json"}
    logging.info('sending application({}) to {}'.format(json_body, API_ADDRESS))
    response = requests.post(API_ADDRESS, data=json_body, headers=headers)
    logging.info(
        'response: status_code = {}, content = {}'.format(response.status_code, response.content.decode("utf-8")))
    return response


def get_application_query_body(user_id, application):
    user_info = get_user_info(user_id)
    return {
        'pin': user_info[1],
        'fullName': user_info[2],
        'phoneNumber': user_info[3],
        'address': application.start_location,
        'destinationAddressesList': [application.destination],
        'startTime': application.start_time.isoformat(),
        'endTime': application.end_time.isoformat(),
        'tripPurpose': application.reason,
    }


def get_application_organization_query_body(user_id, application):
    result = get_application_query_body(user_id, application)
    result['organizationTin'] = application.organization_tin
    result['organizationName'] = application.organization_name
    result['carStateNumber'] = application.car_number
    result['carInformation'] = application.car_info
    result['passengersList'] = []
    for passenger in application.passengers:
        result['passengersList'].append(passenger.__dict__)
    return result
