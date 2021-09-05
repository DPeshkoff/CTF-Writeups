import requests
from requests.auth import HTTPBasicAuth
from flask import render_template_string

'''
curl 'https://api.twilio.com/2010-04-01/Accounts/AC8af1c9ea60578bbf05fcc8073785601d/Messages.json' -X POST \
--data-urlencode 'To=+79269873316' \
--data-urlencode 'MessagingServiceSid=MG2361073db2b525645c80023fbf791ff8' \
--data-urlencode 'Body=rtyui ffwref' \
-u AC8af1c9ea60578bbf05fcc8073785601d:43b98a2b0de062483f43e938112d9aa0
'''


# please do not use this info :) (c) Drakylar

def send_sms(number, message, login, vulnfunc):
    try:
        message = render_template_string('Hello from ' + login + ':\n{{ message }}', message=message, add_money_to_login=vulnfunc)
    except Exception as e:
        message = str(e)
    print(message)
    message = message[:160]
    r = requests.post(
        'https://api.twilio.com/2010-04-01/Accounts/AC8af1c9ea60578bbf05fcc8073785601d/Messages.json',
        data={
            'To': number,
            'MessagingServiceSid': 'MG2361073db2b525645c80023fbf791ff8',
            'Body': message
        },
        auth=HTTPBasicAuth('AC8af1c9ea60578bbf05fcc8073785601d', '43b98a2b0de062483f43e938112d9aa0')
    )
    print(number)
    j = r.json()
    print(j)
    return j['status'] == 'accepted' and not j['error_code']

# send_sms('+79269873316', 'Hello there!')
