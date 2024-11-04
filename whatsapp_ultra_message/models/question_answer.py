import json


from odoo import fields, models, api


import requests




class QuestionAnswers(models.Model):
    _name = 'question_answer'
    _description = 'Description'
    _rec_name = 'question'
    question = fields.Text(required=True,string="Question")
    answer=fields.Text(required=True,string="Answer")
    similar_questions = fields.Text(default='')
    number_of_calls=fields.Integer()
    cost=fields.Float(string="Cost")
    answer_status = fields.Selection(string="Status Answer", selection=[
        ('ai','AI'),
        ('life_agent','Life Agent'),
    ])
    check_life_agent = fields.Boolean(string="Check Life_Agent",default=False)


    def find_most_similar_spacy(self,query=None,top_n=1):
        if query is None:
            query="Hello"

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print(base_url)
        url=f"{base_url}/spacy"


        questions = self.env['question_answer'].search([]).mapped('question')
        answers=self.env['question_answer'].search([]).mapped('answer')
        print("len of questions",len(questions))
        print("type of questions", type(questions))
        print("url",url)
        if not questions:
            return
        header={
            'Content-Type': 'application/json'
        }
        data={
            'query': query,
            "questions":questions,
            "answers":answers,
        }
        print("data",data)
        print("data_json",json.dumps(data))

        req=requests.post(url,headers=header,data=json.dumps(data))
        print("req",req)
        print("req",req.status_code)
        result=req.json()
        print("result",result)
        res=req.json()

        return result