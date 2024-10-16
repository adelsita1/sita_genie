from odoo import models, fields, api

class FagQuestion(models.Model):
	_name = 'faq.question'
	_description = 'FAQ Question'
	question = fields.Text(string='Question')
	answer = fields.Text(string='Answer')
	number_of_calls = fields.Integer(string='Number of Calls')
