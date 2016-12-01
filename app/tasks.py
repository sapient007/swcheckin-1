import requests

checkin_url = 'https://www.southwest.com/flight/retrieveCheckinDoc.html'


def checkin(last_name, first_name, code):
    session = requests.session()
    data = {
        'lastName': last_name,
        'firstName': first_name,
        'confirmationNumber': code,
    }
    print("checking in for {}".format(data))
    response = session.post(checkin_url, data)
    print("Response: {}".format(response.content))
