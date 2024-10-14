from odoo import fields, models, api


class WhatsApp(models.Model):
    _inherit = 'whatsapp_message_log'
    @api.model
    def get_message_log(self, vals):
        messages_obj=self.env['whatsapp_message_log']
        messages=messages_obj.read_group(
            domain=[],
            fields=['partner_id','message_id:count'],
            groupby=["partner_id"]
        )

        partner_messages={
            message['partner_id'][1]:message['partner_id_count']
            for message in messages if message["partner_id"]}
        partner_names=[p_name for p_name in partner_messages.keys()]
        messages_count=[counts for counts in partner_messages.values()]
        return[messages_count,partner_names]
