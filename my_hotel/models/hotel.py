from odoo import models, fields, api

class Hotel(models.Model):
	_name = 'hotel'
	_description = 'Hotel'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	name = fields.Char(string='Hotel Name',required=True)
	address = fields.Char(string='Hotel Address')
	city = fields.Char(string='Hotel City')
	pdf_ids = fields.Many2many('pdf.file', 'hotel_id', string='PDF Files')



