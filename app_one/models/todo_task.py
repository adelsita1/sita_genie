from odoo import models, fields, api

class TodoTask(models.Model):
	_name = 'todo.task'
	_description = 'TodoTask'
	_rec_name = 'task_name'

	task_name = fields.Char(string='Task Name', required=True)
	assigned_to = fields.Many2one('res.partner', string='Assigned To')
	due_date = fields.Datetime(string='Date Due',store=1)
	status = fields.Selection([
		('new', 'New'),
		('in_progress', 'In Progress'),
		('completed', 'Completed'),
		('closed', 'Closed'),
	], string='Status', default='new')
	late_boolean = fields.Boolean(string='Late Boolean')
	active = fields.Boolean(default=True)
	expire_date = fields.Datetime(string='Expire Date')



	def action_closed(self):
		for rec in self:
			rec.status = 'closed'

	def action_confirm(self):
		for rec in self:
			rec.status = 'in_progress'

	def automated_expire_date(self):
		car_ids = self.search([])
		for rec in car_ids:
			if rec.expire_date and rec.expire_date < fields.Datetime.today():
				rec.status = 'in_progress'