from twilio.rest import Client


def send_sms(msg, phone_number):
    account_sid = 'AC27b79fdb06ff102feffb8286ec937a3b'
    auth_token = '74a434ed861f43edc962f701894877ec'
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            body=msg,
            from_='+19738741526',
            to='+63' + phone_number
        )
        return True
    except Exception as ex:
        print(ex)
        return False

# x = send_sms("hi there", '+639064096430')
# print(x)