from odoo import fields, models, api
from odoo.exceptions import ValidationError
import time
import base64
import urllib
# from ..models.ultra_message_class import *
from ..tools.UltraMessageClass import ultraMessage
from ..tools.UltraMessageClass import phone_handler
class SendCustomMessage(models.TransientModel):
    _name = 'whatsapp_ultra_message.send_whatsapp_message'
    _description = 'Whats APP Message custom'
    message_name=fields.Many2one("ultra_message.whatsapp_message",string="Message Title")
    message_text=fields.Text(related='message_name.message_text')
    message_type = fields.Selection(related='message_name.message_type')
    caption = fields.Text(related='message_name.caption')
    document = fields.Binary(related='message_name.document',store=1)
    image = fields.Image(related='message_name.image',store=1)
    use_customer_name = fields.Boolean(related='message_name.use_customer_name')
    predefined_initial_message = fields.Text(related='message_name.predefined_initial_message')
    filename = fields.Char(related='message_name.filename')

    partner_ids=fields.Many2many("res.partner")


    def send_custom_whatsapp_message(self):

        account = self.env['ultra_message.account'].search([], limit=1)
        if not account:
            raise ValidationError("No UltraMessage Account found")


        UltraMessageClass = ultraMessage(account,{})
        # ultramessgae = self.env['res.config.settings']
        instance_ready = UltraMessageClass.check_instance()
        if instance_ready:
            for r in self.partner_ids:
                # print('mobile',r.mobile)
                if self.message_type=='text':
                    if self.use_customer_name and self.predefined_initial_message:
                        if r.title:
                            message = (self.predefined_initial_message + ' {}{} ').format(r.title.shortcut,r.name)
                        else:
                            message = (self.predefined_initial_message + ' {} ').format(r.name)
                    else:
                        message = ''
                    message_2=message +self.message_text
                    r.send_message_partner(r.mobile,message_2)
                    r.message_post(body=message_2)
                    time.sleep(0.5)
                elif self.message_type=='image':
                    if self.use_customer_name and self.predefined_initial_message:
                        if r.title:
                            caption = ('{} {}  '+ self.predefined_initial_message).format(r.title.shortcut,r.name) + ' '
                        else:
                            caption = ( '{} '+self.predefined_initial_message ).format(r.name)+ ' '
                    else:
                        caption = ''
                    caption=caption+' '+self.caption or ''
                    img_bas64 = urllib.parse.quote_plus(self.image)

                    r.send_image_partner(r.mobile, caption,img_bas64)
                elif self.message_type=='document':

                    documentbase64 = urllib.parse.quote_plus(self.document)
                    if self.use_customer_name and self.predefined_initial_message:
                        if r.title:
                            caption = ('{} {} ' +self.predefined_initial_message ).format(r.title.shortcut,r.name) + ' '
                        else:
                            caption = ('{} ' + self.predefined_initial_message ).format(r.name)+ ' '
                    else:
                        caption = ''
                    caption=caption+' '+self.caption or ''


                    r.send_document_partner(r.mobile, caption,documentbase64,self.filename)
                    time.sleep(10)
                messages_return = UltraMessageClass.get_message_status()
                self.partner_ids.handel_sent_message(messages_return)






            # ultramessgae.get_message_status()
