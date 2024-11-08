from odoo import fields, models, api,_
import requests
from odoo.exceptions import ValidationError
import json
from datetime import datetime, timedelta

from ..tools.UltraMessageClass import ultraMessage
from ..tools.UltraMessageClass import phone_handler
class Partner(models.Model):
    _inherit= 'res.partner'
    whatsapp_message_ids=fields.One2many('whatsapp_message_log','partner_id',string="Whatsapp Messages")
    unsubscribe_from_whatsapp_messages=fields.Boolean(string="Unsubscribe from Whatsapp",default=False)
    unsubscription_datetime=fields.Datetime(string="Unsubscription Datetime")



    is_life_agent = fields.Boolean(string="Is Life Agent",default=False,store=True)
    life_agent_state = fields.Selection([
        ('busy','Busy'),
        ('free','Free'),
    ],string="Life Agent State")

    @api.constrains('life_agent_state')
    def _check_life_agent_state_change(self):
        for partner in self:
            if partner.is_life_agent and partner.life_agent_state == 'free':
                self.env['life.agent'].check_and_reassign_questions(partner)

    def send_message_partner(self, phone, message,answer_s=None):
        if self.unsubscribe_from_whatsapp_messages:
            return
        phone = phone_handler(phone)
        account=self.env['ultra_message.account'].search([],limit=1)

        if not account:
            raise ValidationError("No UltraMessage Account found")
        try:
            if phone:
                UltraMessageClass = ultraMessage(account,{})
                # ultramessgae = self.env['res.config.settings']
                instance_ready = UltraMessageClass.check_instance()
                if instance_ready:
                    message_state = UltraMessageClass.send_message(phone, message)
                    messages_return=UltraMessageClass.get_message_status()
                    print("messages_return",messages_return)
                    self.handel_sent_message_life_agent(messages_return,account,answer_s)
                    return message_state
                # print("message send state", message_state)
            else:
                raise ValidationError(_("Mobile Number %s is wrong and message can't be sent", phone))
        except Exception as e:
            print("error sending message status",e)

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
        self.sudo().unsubscription_datetime=lambda self:datetime.now()


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
    def handel_sent_message_life_agent(self,messages,account, answer_s):
        messages_to_create=[]
        print("answer_s",answer_s)
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
                    message_exist.with_context(prefetch_fields=False).write({
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
                    'message_body': mess['body'],
                    'answer_status': answer_s
                })
        self.env['whatsapp_message_log'].with_context(prefetch_fields=False).create(messages_to_create)


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
                    message_exist.with_context(prefetch_fields=False).write({
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
        self.env['whatsapp_message_log'].with_context(prefetch_fields=False).create(messages_to_create)



    def create_lead(self,data=None):
        lead_obj=self.env['crm.lead']
        datetime_limit=datetime.now()-timedelta(days=31)
        existance_lead=lead_obj.search([('partner_id', '=', self.id),("create_date",">=",datetime_limit)])
        if existance_lead:
            if data:
                pre_data=existance_lead.reservation_data or ""
                existance_lead.write({
                    "reservation_data":pre_data+"\n" + data
                })
        else:
            lead_obj.create({
                'partner_id': self.id,
                 "name": self.name,
                "phone":self.mobile or self.phone,

                "nationality":self.country_id.id,
                "type":"opportunity",
                "reservation_data":data if data else None
            })




    def action_view_chat(self):
        return{
            'type':'ir.actions.act_url',
            'target':self, #to be viewed in the same page,
            'url':self.env.company.get_base_url() + '/view/chat/{}'.format(self.id)}