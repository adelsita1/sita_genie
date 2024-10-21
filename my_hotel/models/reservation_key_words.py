from odoo import fields, models, api


class ReservationKeyWords(models.Model):
    _name = 'hotel.reservation.keywords'

    name = fields.Char(required=True)

