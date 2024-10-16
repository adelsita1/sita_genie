from datetime import datetime
from odoo import models, fields, api

class Car(models.Model):
	_name = 'car'
	_description = 'car description'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	ref = fields.Char(string='Ref', readonly=True,default='New')
	name = fields.Selection([('toyota', 'Toyota'),
	                         ('marcedius', 'Marcedius'),
	                         ('hyndai', 'Hyndai'),
	                         ], string = 'Car Name', required = True)
	price = fields.Float(string = 'Rent Price')
	description = fields.Text(string = 'Description')
	model = fields.Integer(string = 'Year')
	color_name = fields.Char(string = 'Color')
	car_friend = fields.Char(string = 'Car Friend')
	car_phone_number = fields.Char(string = 'Car Phone Number')
	number_of_places = fields.Selection([
		('two_place', 'Two Places'),
		('four_place', 'Four Places'),
		('van', 'Van'),
		('bus', 'Bus'),
	], string = 'Car places', default = 'two_place')
	car_driver = fields.Many2one('driver', string = 'Driver')
	car_rent_id = fields.Many2one('car.rent')

	@api.model
	def create(self, vals):
		res = super(Car , self).create(vals)
		if res.ref == 'New':
			res.ref = self.env['ir.sequence'].next_by_code('car_seq')
		return res

