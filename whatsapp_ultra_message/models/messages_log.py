from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime

from ..tools.UltraMessageClass import ultraMessage
import phonenumbers
from phonenumbers import geocoder
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
    message_hash=fields.Char(string="Hash")
    answer_status = fields.Selection(string = "Answer Status", selection = [
        ('ai', 'AI'),
        ('life_agent', 'Life Agent'),
    ])

    def asked_life_agent(self, question, partner_id):
        print("in asked_life_agent")
        life_agent = self.env['life.agent'].create({
            'partner_id': partner_id,
            'question': question,
            'state': 'waiting',
            'time_created': fields.Datetime.now(),
        })
        self.env['life.agent'].check_and_reassign_questions()

    @api.model
    def auto_check_and_reassign(self):
        self.env['life.agent'].check_and_reassign_questions()
    # def asked_life_agent(self, question,partner_id):
    #     life_agent = self.env['life.agent'].search([('question','=',question)])
    #     if not life_agent:
    #         life_agent = self.env['life.agent'].create({
    #             'partner_id':partner_id,
    #             'question': question,
    #             'state': 'waiting',
    #             'time_created': datetime.now(),
    #         })
    #     print("in life agent")
    #     partner = self.env['res.partner'].search([('is_life_agent', '=', True),('life_agent_state','=','free')], limit = 1)
    #     print("partner", partner)
    #     if partner:
    #         print("partner.mobile",partner.mobile)
    #         partner.send_message_partner(phone=partner.mobile, message =question,answer_s='life_agent')
    #         life_agent.write({'state': 'inprogress','life_Agent_name': partner.id,'time_read': datetime.now()})
    #         partner.write({'life_agent_state':'busy'})

    @api.model
    def create_message_received(self,message_received):
        # try:
            print("message_received",message_received)
            print("message_received",message_received["instanceId"])
            instance_id="instance"+message_received["instanceId"]
            account=self.env["ultra_message.account"].search([("instance_id","=",instance_id)])
            print("account",account)
            hotel=self.env["hotel"].search([("account_id","=",account.id)])
            data = message_received["data"]
            print("data in recive",data)
            mobile = data['from'][:-5]
            mobile2 = data['from'][1:-5]
            partner = self.env['res.partner'].sudo().search(
                [('mobile', 'in', [mobile, mobile2, '2' + mobile, '2' + mobile2]),],limit=1)
            if partner:
                partner_id = partner[0].id
            else:
                try:
                    phone_number = mobile
                    if phone_number.startswith("00"):
                        phone_number = phone_number[2:]
                    if not phone_number.startswith("+"):
                        phone_number = "+" + phone_number
                    pn = phonenumbers.parse(phone_number)
                    country_name = geocoder.description_for_number(pn, "en")
                    country_id = self.env['res.country'].search([('name','ilike',country_name)])
                    partner=self.env['res.partner'].with_context(prefetch_fields=False).sudo().create({
                        'name':data["pushname"],
                        "mobile":mobile,
                        "country_id":country_id.id
                    })
                    partner_id = partner.id
                except Exception as e:
                    print("error in package phone Numbers",e)
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
                "message_hash":message_received["hash"],
            }
            self.env["whatsapp_message_log"].with_context(prefetch_fields=False).sudo().create(vals)
            self.env.cr.commit()
            self.env.cr.savepoint()
            if   data["body"] in ["stop","quit","unsubscribe"]:
                partner.unsubscribe_from_whatsapp_messages=True

            if partner.is_life_agent:
                life_agent  = self.env['life.agent'].search([('life_Agent_name','=',partner.id),('state','=','inprogress')], limit=1)
                if life_agent:
                    partner_send = self.env['res.partner'].search([('id','=',life_agent.partner_id.id)])
                    message_answer = f"As you asked the question: '{life_agent.question}', the answer is: '{data['body']}'"
                    print("partner_send",partner_send)
                    print("partner_send.mobile",partner_send.mobile)
                    partner.send_message_partner(phone=partner_send.mobile, message=message_answer, answer_s ='life_agent')
                    faq = self.env['question_answer'].search([('question','=',life_agent.question)])
                    if not faq.check_life_agent:
                        faq.write({'answer':data['body']})
                    life_agent.write({'state':'done','time_done':datetime.now(),'answer':data['body']})
                    partner.write({'life_agent_state':'free'})
                else:
                    print("no life agent line")
            else:
                answer,answer_s=hotel.process_pdf(asked_question=data["body"])
                if answer_s == 'life_agent':
                    self.asked_life_agent(question=data["body"],partner_id=partner_id)
                partner.send_message_partner(mobile,answer,answer_s)



        # except Exception as e:
        #     print("exception in create received",e)
        #     return False
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



    
