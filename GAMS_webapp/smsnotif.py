# # # # # # # # # # USING TWILIO # # # # # # # # # #
#
# from twilio.rest import Client
#
#
# def send_sms(msg, phone_number):
#     account_sid = 'xxx'
#     auth_token = 'xxx'
#     client = Client(account_sid, auth_token)
#
#     try:
#         message = client.messages.create(
#             body=msg,
#             from_='+19738741526',
#             to='+63' + phone_number
#         )
#         return True
#     except Exception as ex:
#         print(ex)
#         return False
#
# # # # # # # # # # USING TWILIO # # # # # # # # # #



# # # # # # # # # # USING NEXMO # # # # # # # # # #

# import nexmo
#
# def send_sms(msg, phone_number):
#     client = nexmo.Client(key='xxx', secret='xxxx')
#
#     try:
#         client.send_message({
#             'from': 'Academia Project',
#             'to': '63' + phone_number,
#             'text': msg,
#         })
#         return True
#     except Exception as ex:
#         print(ex)
#         return False

# # # # # # # # # # USING NEXMO # # # # # # # # # #


# # # # # # # # # # USING SELENIUM # # # # # # # # # #
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import pytesseract
# from PIL import Image
# import requests
#
# def send_sms(msg, phone_number):
#     webpage = r"http://www.afreesms.com/intl/philippines"
#     options = Options()
#     options.add_argument("--headless")
#     driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=options)
#     driver.get(webpage)
#     driver.set_window_size(1400, 100)
#
#     captcha_img = driver.find_element_by_id("captcha")
#     src = captcha_img.get_attribute("src")
#     img = Image.open(requests.get(src, stream=True).raw)
#     v_code = pytesseract.image_to_string(img).split('\n')[0]
#     print(v_code)
#
#
#
#
#
#     input_v = driver.find_element_by_xpath("//input[@type='text']")
#     input_v.send_keys(v_code)
#
#     input_number = driver.find_element_by_xpath("//input[@type='text'][1]")
#     input_number.send_keys(phone_number)
#
#     input_msg = driver.find_element_by_xpath("//textarea")
#     input_msg.send_keys(msg)
#
#     submit_btn = driver.find_element_by_id("submit")
#     submit_btn.click()
#     print("sms was Sent")
#
#
# # # # # # # # # # USING SELENIUM # # # # # # # # # #


# # # # # # # # # # USING ITEXMO # # # # # # # # # # #
import requests

def send_sms(msg, phone_number):
    data = {
        '1': '0' + phone_number,
        '2': msg,
        '3': 'xxxx',
    }

    header = {'content-type': 'application/x-www-form-urlencoded'}
    url = 'https://www.itexmo.com/php_api/api.php'

    try:
        send = requests.post(url=url, data=data, headers=header)
        print(send.json())
        return True
    except:
        print('something went wrong')
        return False




# # # # # # # # # # USING ITEXMO # # # # # # # # # # #


# x = send_sms("hi there", '9198601070')
# print(x)