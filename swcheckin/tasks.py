import requests
import logging

logger = logging.getLogger(__name__)


checkin_url = 'https://www.southwest.com/flight/retrieveCheckinDoc.html'


def reminder(last_name, first_name, code):
    # TODO: send a reminder via text or slack msg
    logger.info("This is a reminder")


def checkin(last_name, first_name, code):
    session = requests.session()
    data = {
        'lastName': last_name,
        'firstName': first_name,
        'confirmationNumber': code,
    }
    logger.info("checking in for {}".format(data))
    response = session.post(checkin_url, data)
    logger.info("Response: {}".format(response.content))
