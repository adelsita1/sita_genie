from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime

from ..tools.UltraMessageClass import ultraMessage

class WhatsApp(models.Model):
    _name = 'whatsapp_message_log'
    _description = 'WhatsApp Message Log'
    _order='sent_datetime desc'

    partner_id=fields.Many2one('res.partner',string='Contact')
    mobile=fields.Char(string='Mobile Number',compute='adjust_phone_number',store=1)

    message_body=fields.Text("Message Body")

    message_id=fields.Char(string="Message Id")

    status=fields.Char(string="Message State")

    sent_datetime=fields.Datetime(string="Send Date Time")
    direction=fields.Selection([("sent","Sent"),("received","Received")],default="sent",string="Direction")
    sent_from=fields.Char(string="From")
    account_id=fields.Many2one('ultra_message.account')
    push_name=fields.Char(string="Push Name")

    @api.model
    def create_message_received(self,message_received):
        try:
            account=self.env["ultra_message.account"].search([("instance_id","=",message_received["instanceId"])])
            data = message_received["data"]
            mobile = data['from'][:-5]
            mobile2 = data['from'][1:-5]
            partner_id = self.env['res.partner'].sudo().search(
                [('mobile', 'in', [mobile, mobile2, '2' + mobile, '2' + mobile2])])
            if partner_id:

                partner_id = partner_id[0].id
            else:
                partner=self.env['res.partner'].sudo().create({
                    'name':data["push_name"],
                    "mobile":data["mobile"],
                })

                partner_id = partner.id
            vals={
                'message_body':data["body"],
                "direction":"received",
                "sent_datetime":datetime.fromtimestamp(data['time']) if 'time' in data and data['time'] is not  None else False,
                "sent_from":mobile,
                "account_id":account.id,
                "status":"Received",
                "partner_id":partner_id,
                'mobile': mobile,
                "push_name":data["pushname"],

            }
            self.env["whatsapp_message_log"].sudo().create(vals)
        except Exception as e:
            print("exception in create received",e)
            return False
        return True


    # datetime_rcv_state=fields.Datetime('Receiving State Datetime')

    @api.model
    def get_message_status(self):


        account = self.env['ultra_message.account'].search([], limit=1)

        if not account:
            raise ValidationError("No UltraMessage Account found")

        UltraMessageClass = ultraMessage(account, {})
        instance_ready = UltraMessageClass.check_instance()
        if instance_ready:
            messages=UltraMessageClass.get_message_status()
            self.env['res.partner'].handel_sent_message(messages,account)



    
