import json
import logging

from pip._vendor import requests

from db_operations import get_user_info
from settings import API_ADDRESS


def send_organization_application_and_get_url(user_id: str, application):
    json_body = json.dumps(get_application_organization_query_body(user_id, application))
    headers = {'Content-type': "application/json"}
    logging.info('sending organization_application({}) to {}'.format(json_body, API_ADDRESS))
    response = requests.post(API_ADDRESS, data=json_body, headers=headers)
    logging.info('response: status_code = {}, content = {}'.format(response.status_code, response.content))
    return response.content


def send_application_and_get_url(user_id: str, application):
    json_body = json.dumps(get_application_query_body(user_id, application))
    headers = {'Content-type': "application/json"}
    logging.info('sending application({}) to {}'.format(json_body, API_ADDRESS))
    response = requests.post(API_ADDRESS, data=json_body, headers=headers)
    logging.info('response: status_code = {}, content = {}'.format(response.status_code, response.content))
    return response.content


def get_application_query_body(user_id, application):
    user_info = get_user_info(user_id)
    return {
        'pin': user_info[1],
        'fullName': user_info[2],
        'phoneNumber': user_info[3],
        'address': location_to_str(application.start_location),
        'destinationAddressesList': [location_to_str(application.destination)],
        'startTime': application.start_time,
        'endTime': application.end_time,
        'tripPurpose': [application.reason],
    }


def get_application_organization_query_body(user_id, application):
    result = get_application_query_body(user_id, application)
    result['organizationTin'] = application.organization_tin
    result['organizationName'] = application.organization_name
    result['carStateNumber'] = application.car_number
    result['carInformation'] = application.car_info
    result['passengers'] = []
    for passenger in application.passengers:
        result['passengers'].append(passenger.__dict__)
    return result


def location_to_str(location):
    return '{} {}'.format(location.longitude, location.latitude)
