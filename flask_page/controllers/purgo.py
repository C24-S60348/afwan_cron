from flask import Blueprint, request, jsonify
import variables
import requests
from twilio.rest import Client

purgo_bp = Blueprint('purgo_bp', __name__)

# PURGO ------------------------------------
@purgo_bp.route('/api/sendemailbrevotest', methods=['GET', 'POST'])
async def send_email_brevo_test():
    BREVO_API_KEY = variables.brevo_api_key
    BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    required_fields = ['to_email', 'subject', 'html_content', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    to_email = data['to_email']
    subject = data['subject']
    html_content = data['html_content']
    password = data['password']

    if password == variables.website_pass:

        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }

        payload = {
            "sender": {
                "name": "Afwan Test",
                "email": "afwanhaziq987@gmail.com"  # Make sure this sender is verified in Brevo
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content
        }

        response = requests.post(BREVO_API_URL, json=payload, headers=headers)

        try:
            response.raise_for_status()
            return jsonify({"message": "Email sent successfully"}), 201
        except requests.exceptions.HTTPError:
            return jsonify({
                "error": response.json(),
                "status_code": response.status_code
            }), response.status_code
    else:
        return jsonify({"error": "password is required"}), 400

@purgo_bp.route('/api/sendemail', methods=['POST'])  # Remove GET if not needed
async def send_email():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    # Get data from the request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    required_fields = ['to_email', 'subject', 'html_body', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if data['password'] != variables.website_pass:
        return jsonify({"error": "Invalid password"}), 403

    TO_EMAIL = data['to_email']
    SUBJECT = data['subject']
    BODY = data['html_body']

    # SMTP settings
    SMTP_SERVER = variables.purgo_server
    SMTP_PORT = 587  # try 465 for SSL if 553 fails
    SMTP_USERNAME = variables.purgo_email
    SMTP_PASSWORD = variables.purgo_password

    FROM_EMAIL = variables.purgo_email

    # Compose the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg.attach(MIMEText(BODY, "html"))

    # Send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        server.quit()
        return jsonify({"message": "✅ Email sent successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@purgo_bp.route('/api/sendsms', methods=['POST'])
async def send_sms():
    BREVO_SMS_API_KEY = variables.brevo_sms_api_key
    BREVO_SMS_API_URL = "https://api.brevo.com/v3/transactionalSMS/sms"

    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    required_fields = ['to_number', 'content', 'sender', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    to_number = data['to_number']        # Must be in E.164 format, e.g. +60123456789
    content = data['content']
    sender = data['sender']              # Must be a validated sender in Brevo
    password = data['password']

    if password == variables.website_pass:

        headers = {
            "accept": "application/json",
            "api-key": BREVO_SMS_API_KEY,
            "content-type": "application/json"
        }

        payload = {
            "sender": sender,
            "recipient": to_number,
            "content": content,
            "type": "transactional"
        }

        response = requests.post(BREVO_SMS_API_URL, json=payload, headers=headers)

        try:
            response.raise_for_status()
            return jsonify({"message": "SMS sent successfully", "response": response.json()}), 201
        except requests.exceptions.HTTPError:
            return jsonify({
                "error": response.json(),
                "status_code": response.status_code
            }), response.status_code
    else:
        return jsonify({"error": "password is required"}), 400



@purgo_bp.route('/api/sendsmstwiliomahal', methods=['GET', 'POST'])
async def send_sms_twilio():
    TWILIO_ACCOUNT_SID = variables.twilio_account_sid
    TWILIO_AUTH_TOKEN = variables.twilio_auth_token
    TWILIO_PHONE_NUMBER = variables.twilio_phone_number

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    if 'number' not in data:
        return jsonify({"error": "number parameter is required"}), 400

    if 'password' not in data:
        return jsonify({"error": "password parameter is required"}), 400

    if 'text' not in data:
        return jsonify({"error": "text parameter is required"}), 400

    number = data['number']
    password = data['password']
    text = data['text']

    if password == variables.website_pass:
        try:
            message = client.messages.create(
                to=number,
                from_=TWILIO_PHONE_NUMBER,
                body=text
            )
            return jsonify({"message_sid": message.sid}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "password parameter is invalid"}), 400

#PURGO -----------------------------------