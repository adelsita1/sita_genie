from odoo import fields, models, api


class QuestionAnswers(models.Model):
    _name = 'question_answer'
    _description = 'Description'

    question = fields.Text(required=True,string="Question")
    answer=fields.Text(required=True,string="Answer")

    number_of_calls=fields.Integer()
