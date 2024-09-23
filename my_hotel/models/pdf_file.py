from odoo import models, fields, api

class MyPdf(models.Model):
	_name = 'pdf.file'
	_description = 'Pdf file'
	name = fields.Char(string='PDF Name')
	pdf_file = fields.Binary(string='PDF File')
	hotel_id = fields.Many2one('hotel', string='Hotel')
