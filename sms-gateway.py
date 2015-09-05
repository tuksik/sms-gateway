from flask import Flask, Response, request
from twilio import twiml
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import requests
from pprint import pformat
from talon import quotations
from twilio.rest import TwilioRestClient

app = Flask(__name__)

MAIL_ADDRESS="postmaster@example.org"
MAILGUN_DOMAIN="example.org"
MAILGUN_AUTH="key-c0d3"
TWILIO_AUTH1="c0d31"
TWILIO_AUTH2="c0d32"
FROM_NUMBER="+123456789"

@app.route('/receive', methods=['GET', 'POST'])
def receive():
    r = twiml.Response()
    from_number = request.values.get('From', None)
    body = request.values.get('Body')
    if from_number is not None and body is not None:
        try:
            mail(MAIL_ADDRESS, from_number, body)
        except Exception, e:
            r.message("[Delivery failed, contact {}: {}]"
                .format(MAIL_ADDRESS, str(e)[:80]))
    return Response(str(r), mimetype='application/xml')

@app.route('/send', methods=['GET', 'POST'])
def send():
    body = quotations.extract_from_plain(request.values.get('body-plain'))
    subject = request.values.get('subject')
    number = '+{}'.format(request.values.get('number'))

    client = TwilioRestClient(TWILIO_AUTH1, TWILIO_AUTH2)

    is_reply = subject.startswith("Re: ")
    has_subject = subject != "" and not is_reply

    if not has_subject and body == '':
        return
    elif has_subject and body == '':
        body = subject
    elif has_subject and body != '':
        body = subject + ': ' + body
    app.logger.debug("Received mail, sending SMS to %s: %s", number, body)
    client.messages.create(to=number, from_=FROM_NUMBER,
                           body=body)
    return ('', 204)
    

def mail(to, from_number, body):
    from_number = "".join(_ for _ in from_number if _ in "1234567890")
    app.logger.debug("Received SMS from %s, mailing to %s: %s", from_number, to, body)
    requests.post("https://api.mailgun.net/v3/{}/messages".format(MAILGUN_DOMAIN),
        auth=("api", MAILGUN_AUTH),
        data={"from": "{}@{}".format(from_number, MAILGUN_DOMAIN),
              "to": [to],
              "subject": body[:23],
              "text": body})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
