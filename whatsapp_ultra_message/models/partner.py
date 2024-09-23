from odoo import fields, models, api,_
import requests
from odoo.exceptions import ValidationError
import json
from datetime import datetime


from ..tools.UltraMessageClass import ultraMessage
from ..tools.UltraMessageClass import phone_handler
class Partner(models.Model):
    _inherit= 'res.partner'
    whatsapp_message_ids=fields.One2many('whatsapp_message_log','partner_id',string="Whatsapp Messages")
    unsubscribe_from_whatsapp_messages=fields.Boolean(string="Unsubscribe from Whatsapp",default=False)


    def send_message_partner(self, phone, message):
        if self.unsubscribe_from_whatsapp_messages:
            return

        phone = phone_handler(phone)
        account=self.env['ultra_message.account'].search([],limit=1)

        if not account:
            raise ValidationError("No UltraMessage Account found")

        if phone:
            UltraMessageClass = ultraMessage(account,{})
            # ultramessgae = self.env['res.config.settings']
            instance_ready = UltraMessageClass.check_instance()
            if instance_ready:
                message_state = UltraMessageClass.send_message(phone, message)
                messages_return=UltraMessageClass.get_message_status()
                print("messages_return",messages_return)
                self.handel_sent_message(messages_return,account)
                return message_state

            # print("message send state", message_state)


        else:
            raise ValidationError(_("Mobile Number %s is wrong and message can't be sent", phone))


    def send_image_partner(self, phone, caption,imagebase64):
        if self.unsubscribe_from_whatsapp_messages:
            return
        phone = phone_handler(phone)
        print('phone',phone)
        if phone:

            phone = phone_handler(phone)
            account = self.env['ultra_message.account'].search([], limit=1)

            if not account:
                raise ValidationError("No UltraMessage Account found")
            UltraMessageClass = ultraMessage(account, {})

            instance_ready = UltraMessageClass.check_instance()
            if instance_ready:
                message_state = UltraMessageClass.send_image( phone, imagebase64, caption)

                print("message_state",message_state)
                messages_return = UltraMessageClass.get_message_status()
                self.handel_sent_message(messages_return,account)
                return message_state
            else:
                print("Document is not ready")

    def send_document_partner(self, phone, caption,doc_base64,filename):
        if self.unsubscribe_from_whatsapp_messages:
            return
        phone = phone_handler(phone)
        print('phone', phone)
        if phone:

            phone = phone_handler(phone)
            account = self.env['ultra_message.account'].search([], limit=1)

            if not account:
                raise ValidationError("No UltraMessage Account found")
            UltraMessageClass = ultraMessage(account, {})

            instance_ready = UltraMessageClass.check_instance()
            if instance_ready:
                message_state = UltraMessageClass.send_document( phone, doc_base64, caption,filename)
                print('message_state',message_state)
            messages_return = UltraMessageClass.get_message_status()
            self.handel_sent_message(messages_return,account)


    def unsubscribe_form_whatsapp(self):
        self.sudo().unsubscribe_from_whatsapp_messages=True


    def send_custom_message(self):
        ctx = {

            "default_partner_ids": self.ids
        }
        return {
            'name': _('Send Custom Message'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'whatsapp_ultra_message.send_whatsapp_message',
            'target': 'new',
            'context': ctx,
        }

        return action

    @api.model
    def handel_sent_message(self,messages,account):
        messages_to_create=[]
        print("in  handel_sent_message")
        for mess in messages:

            message_exist = self.env['whatsapp_message_log'].search([('message_id', '=', mess['id'])], limit=1)
            mobile = mess['to'][:-5]
            mobile2 = mess['to'][1:-5]
            partner_id = self.env['res.partner'].sudo().search(
                [('mobile', 'in', [mobile, mobile2, '2' + mobile, '2' + mobile2])])
            if partner_id:

                partner_id = partner_id[0].id
            else:
                partner_id = False

            if message_exist:

                if message_exist.status not in ['sent', 'invalid'] or message_exist.partner_id == False:
                    message_exist.write({
                        "status": mess['status'],
                        'partner_id': partner_id,
                        'sent_datetime': datetime.fromtimestamp(mess['sent_at']) if 'sent_at' in mess and mess[
                            'sent_at'] != None else False,
                        'account_id':account.id,
                    })
                else:
                    pass
                    # existing_mess += 1

            else:

                messages_to_create.append({
                    'mobile': mobile,
                    "message_id": mess['id'],
                    "status": mess['status'],
                    'partner_id': partner_id,
                    'sent_datetime': datetime.fromtimestamp(mess['sent_at']) if 'sent_at' in mess and mess[
                        'sent_at'] != None else False,
                    'message_body': mess['body']
                })
        self.env['whatsapp_message_log'].create(messages_to_create)