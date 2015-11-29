# sms-gateway

A small webserver which bridges SMS and email. Requires a Twilio and a Mailgun account.
SMS sent to a Twilio phone number should perform a HTTP request to `/receive`, 
which forwards the message as an email to a given address using Mailgun. 
Emails sent to a Mailgun email address should perform a HTTP request to `/send`, 
which forwards the message as a SMS to the given phone number using Twilio.
