from odoo import fields, models, api


class RatesRules(models.Model):
    _name = 'hotel.rate.rule'
    _description = 'Rate Rule'

    name = fields.Text(string="Rates Rules",required=True)
