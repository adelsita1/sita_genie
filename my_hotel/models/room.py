from odoo import models, fields, api

class Room(models.Model):
	_name = 'room'
	_description = 'Room'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	name = fields.Char(string='Room Number')
	room_type = fields.Selection([
		('single_room', 'Single Room'),
		('double_room', 'Double Room'),
		('twin_room', 'Twin Room'),
		('triple_room', 'Triple Room'),
		('suite', 'Suite'),
		('studio_room', 'Studio Room'),
		('family_room', 'Family Room'),
		('deluxe_room', 'Deluxe Room'),
		('executive_room', 'Executive Room'),
		('connecting_room', 'Connecting Room'),
		('accessible_room', 'Accessible Room'),
	], string='Room Type',default='double_room')
	floor_number = fields.Integer(string='Floor Number')
	hotel_id = fields.Many2one('hotel', string='Hotel')
