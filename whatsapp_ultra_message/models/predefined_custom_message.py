from odoo import fields, models, api


class UltraMessage(models.Model):
    _name = 'ultra_message.whatsapp_message'
    _description = 'Custom Whats App Message'

    name = fields.Char("Message Title", required=True)
    message_text=fields.Text("Message Text",required=False)
    message_type=fields.Selection([("text","Text"),("image","Image"),("document","Document")],required=True,default="text")
    caption=fields.Text("Caption")
    document=fields.Binary("Document")
    filename=fields.Char("File Name")
    image=fields.Image("Image")
    use_customer_name=fields.Boolean("Use Customer name?")
    predefined_initial_message=fields.Text("Predefined Message Before Name")
