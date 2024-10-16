from odoo import models, fields, api

class Driver(models.Model):
	_name = 'driver'
	_description = 'driver'

	name = fields.Char(string='Driver Name', required=True)
	age = fields.Integer(string='Age', required=True)
	license = fields.Boolean(string='License', default=False)

	_sql_constraints = [
		('name_unique','unique(name)', 'Driver name must be unique'),
	]


