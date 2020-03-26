from create_application_flow import ApplicationForm
from create_application_organization_flow import ApplicationOrganizationForm
from db_operations import get_user_info
from registration_flow import UserInfo


def send_organization_application(user_id: str, application: ApplicationOrganizationForm):
    user_info = UserInfo().initialize_with_list(get_user_info(user_id))


def send_application(user_id: str, application: ApplicationForm):
    user_info = UserInfo().initialize_with_list(get_user_info(user_id))
