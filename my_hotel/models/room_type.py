from odoo import fields, models, api


class RoomType(models.Model):
    _name = 'hotel.room.type'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Room Description', required=True)
