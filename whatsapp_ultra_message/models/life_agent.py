from odoo import models, fields, api

class LifeAgent(models.Model):
	_name = 'life.agent'
	_description = 'LifeAgent Model'
	name = fields.Char(string='Name')
	time_created = fields.Datetime(string='Time created')
	time_read =fields.Datetime(string='Time read')
	time_done =fields.Datetime(string='Time done')
	partner_id = fields.Many2one('res.partner', string='Partner')
	life_Agent_name = fields.Many2one('res.partner', string='Life Agent Name')
	question = fields.Char(string='Question')
	answer = fields.Char(string='Answer')
	state = fields.Selection(string='State',selection=[
		('inprogress', 'In progress'),
		('waiting', 'Waiting'),
		('done', 'Done'),
	])

	@api.constrains('state')
	def _check_state_change(self):
		print("in _check_state_change")
		for record in self:
			if record.state == 'done':
				if record.life_Agent_name:
					record.life_Agent_name.life_agent_state = 'free'
				self.check_and_reassign_questions()

	@api.model
	def check_and_reassign_questions(self, specific_agent=None):
		print("in check_and_reassign_questions")
		domain = [('state', '=', 'waiting')]
		if specific_agent:
			domain.append(('life_Agent_name', '=', False))

		waiting_questions = self.search(domain, order = 'time_created asc')

		for question in waiting_questions:
			if specific_agent and specific_agent.life_agent_state == 'free':
				free_agent = specific_agent
			else:
				free_agent = self.env['res.partner'].search([
					('is_life_agent', '=', True),
					('life_agent_state', '=', 'free')
				], limit = 1)

			if free_agent:
				question.write({
					'state': 'inprogress',
					'life_Agent_name': free_agent.id,
					'time_read': fields.Datetime.now()
				})
				free_agent.life_agent_state = 'busy'
				partner = self.env['res.partner'].search([('id', '=', free_agent.id)])
				# Send message to the life agent
				partner.send_message_partner(
					free_agent.mobile, question.question,'life_agent')

				if specific_agent:
					break
