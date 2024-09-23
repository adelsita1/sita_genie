import logging
import requests
import threading
import json
import http.client
from odoo import _
from odoo.exceptions import ValidationError
from datetime import datetime
DEFAULT_ENDPOINT="https://api.ultramsg.com/"
from .utils import *
# from odoo.addons.whatsapp_ultra_message.tools import utils
from .utils import phone_handler

class ultraMessage():

    def __init__(self, Account,json):
        self.json = json
        # self.instance_id = json['instance_id']
        self.instance_id = Account.instance_id
        # self.token = json['token']
        self.ultraAPIUrl = DEFAULT_ENDPOINT + self.instance_id + '/'

        self.token = Account.token

    def check_instance(self):

        url = f"{self.ultraAPIUrl}instance/status/?token={self.token}"


        headers = {'content-type': 'application/json',
                   'token': self.token}

        response = requests.get(url, headers = headers)
        try:
            response_json = response.json()
        except Exception as e:
            return False
        else:
            try:
                if response_json["status"]["accountStatus"]["status"] == "authenticated":
                    return True
                else:
                    return response_json["status"]["accountStatus"]["status"]
            except Exception as e:
                raise ValidationError(_("response_json is %s and error is %s",response_json,e))

    def send_requests(self, type, data):
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data = json.dumps(data), headers = headers)
        # print('send')
        return answer.json()

    def send_message(self, chatID, text):
        data = {"to": phone_handler(chatID),
                "body": text}

        answer = self.send_requests('messages/chat', data)
        return answer

    def send_image(self, chatID, img_bas64, caption):
        payload = "token="+self.token+"&to="+phone_handler(chatID)+"&image=" + img_bas64 + "&caption=" + caption
        conn = http.client.HTTPSConnection("api.ultramsg.com")
        headers = {'content-type': "application/x-www-form-urlencoded"}
        conn.request("POST", "/{}/messages/image?token={}".format(self.instance_id,self.token), payload, headers)
        res = conn.getresponse()
        try:
            data = json.loads(res.read().decode('utf-8'))

            if data['sent'] == 'true':

                return data
        except Exception:
            return False


    def send_link(self, chatID, media_url, message):
        data = {"to": phone_handler(chatID),
                "link": media_url,
                'caption': message}
        answer = self.send_requests('messages/link', data)
        return answer

    def send_document(self, chatID, document_bas64, caption,file_name):
        # instance_id = self.env['ir.config_parameter'].sudo().get_param('whatsapp_ultra_message.instance_id')
        # token = self.env['ir.config_parameter'].sudo().get_param('whatsapp_ultra_message.token')

        payload = "token="+self.token+"&to="+phone_handler(chatID)+"&filename="+file_name+"&document=" + document_bas64 + "&caption=" + caption
        conn = http.client.HTTPSConnection("api.ultramsg.com")
        headers = {'content-type': "application/x-www-form-urlencoded"}
        conn.request("POST", "/{}/messages/document?token={}".format(self.instance_id,self.token), payload, headers)
        res = conn.getresponse()
        try:
            data = json.loads(res.read().decode('utf-8'))
            print("data", data)

            if data['sent'] == 'true':

                return data
        except Exception as e:
            print("Exception ", e)
            return False

    def get_message_status(self,total=2):

        url = f"{self.ultraAPIUrl}messages"

        headers = {'content-type': 'application/json'}
        existing_mess = 0

        for p in range(1,total):
            if existing_mess==20:
                break
            data = {
                "token": self.token,
                "page": p,
                "limit": 100,
                "status": "",
                "sort": "desc"
            }
            response = requests.request("GET", url, headers = headers, params = data).json()
            print("response",response)

            total=response['total']//100 +2
            messages_to_create=[]
            if 'messages' not in response or len(response['messages'])==0:
                return None
            else:
                return  response['messages']





