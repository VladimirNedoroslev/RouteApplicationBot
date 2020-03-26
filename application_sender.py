import json

from pip._vendor import requests

from db_operations import get_user_info
from registration_flow import UserInfo
from settings import REASON_ID, API_ADDRESS


def send_organization_application_and_get_url(user_id: str, application):
    json_body = json.dumps(get_application_organization_query_body(user_id, application))
    headers = {'Content-type': "application/json"}
    response = requests.post(API_ADDRESS, data=json_body, headers=headers)
    print(response.content)
    return response.content


def send_application_and_get_url(user_id: str, application):
    json_body = json.dumps(get_application_query_body(user_id, application))
    headers = {'Content-type': "application/json"}
    response = requests.post(API_ADDRESS, data=json_body, headers=headers)
    print(response.content)
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
        'tripPurposeId': REASON_ID[application.reason],
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
#
# {
#   "pin":"20205199401330",
#   "fullName":"Galiev Bekx",
#   "address":"sadfasdf",
#   "phoneNumber":"0700 670 146",
#   "destinationAddressesList": ["another adress"],
#   "startTime":"2020-06-06",
#   "endTime":"2020-06-07",
#   "tripPurposeId": 1
# }
