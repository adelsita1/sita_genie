from odoo import fields, models, api


class ModelName(models.TransientModel):
    _inherit = 'res.config.settings'
    instance_id = fields.Char(string="Instance ID",config_parameter='whatsapp_ultra_message.instance_id')
    token = fields.Char(string="Token ID",config_parameter='whatsapp_ultra_message.token')
    # ultramessageurl=fields.Char(config_parameter='whatsapp_ultra_message.token',compute='_compute_url',store=1)

    # @api.depends('instance_id')
    # def _compute_url(self):
    #     for r in self:
    #         r.ultramessageurl='https://api.ultramsg.com/' + r.instance_id + '/'



