from odoo import fields, models, api,_



class UltraMessageAccount(models.Model):
    _name = 'ultra_message.account'

    instance_id=fields.Char('Instance ID',required=True)

    token = fields.Char(string="Token ID", required=True)
