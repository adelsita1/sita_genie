from odoo import fields, models, api

import re
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

    message_template = fields.Text(string="Message Template")
    use_partner_name = fields.Boolean(string="Use Partner Name")
    use_partner_mobile = fields.Boolean(string="Use Partner Mobile")
    use_partner_job_description = fields.Boolean(string="Use Partner Job Description")

    @api.onchange('use_partner_name', 'use_partner_mobile', 'use_partner_job_description')
    def _onchange_partner_fields(self):
        template = self.message_template or ''

        fields_to_placeholders = {
            'use_partner_name': '${partner.name}',
            'use_partner_mobile': '${partner.mobile}',
            'use_partner_job_description': '${partner.function}'
        }

        for field, placeholder in fields_to_placeholders.items():
            if getattr(self, field):
                if placeholder not in template:
                    template += f" {placeholder}"
            else:
                template = template.replace(placeholder, '')

        self.message_template = template.strip()

    def render_partner_message(self, partner):
        if not self.message_template:
            return ""
        print("message_template", self.message_template)

        def replace_field(match):
            field_name = match.group(1)
            if hasattr(partner, field_name):
                return str(getattr(partner, field_name))
            return match.group(0)

        pattern = r'\$\{partner\.(\w+)\}'
        rendered_message = re.sub(pattern, replace_field, self.message_template)
        print("rendered_message", rendered_message)
        return rendered_message
