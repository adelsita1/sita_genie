from odoo import models, fields, api

class CarRent(models.Model):
    _name = 'car.rent'
    _description = 'car description'
    name = fields.Char(string='Name', compute='_compute_name',store=True)
    address = fields.Char(string='Address')
    time = fields.Datetime(string='Time')
    number_of_persons = fields.Integer(string='Number of persons')
    state = fields.Selection([
        ('draft','Draft'),
        ('waiting','Waiting'),
        ('done','Done'),
    ],string='State')
    car_line_ids = fields.One2many('car','car_rent_id')

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_waiting(self):
        for rec in self:
            rec.state = 'waiting'
    def action_done(self):
        for rec in self:
            rec.state = 'done'

    @api.depends('time')
    def _compute_name(self):
        for record in self:
            if record.time:
                record.name = 'Rent' + ' - ' + record.time.strftime('%d-%m-%Y')

    def create_car(self):
        car = self.env['car'].create({
            'name' : 'toyota',
            'price': 1000,

        })


