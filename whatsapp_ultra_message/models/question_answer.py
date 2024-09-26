import json

from odoo import fields, models, api
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import requests

from ..tools.spacy_tool import SpacyTool


class QuestionAnswers(models.Model):
    _name = 'question_answer'
    _description = 'Description'
    _rec_name = 'question'
    question = fields.Text(required=True,string="Question")
    answer=fields.Text(required=True,string="Answer")
    similar_questions = fields.Text(default='')

    number_of_calls=fields.Integer()
    cost=fields.Float(string="Cost")

    # @api.model
    # def _load_nlp_model(self):
        # return spacy.load("en_core_web_md")  # Make sure to install this model
    #
    # @api.model
    # def preprocess_text(self, text):
    #     nlp = self._load_nlp_model()
    #     doc = nlp(text)
    #     return " ".join([token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct])

    # @api.model
    # def get_sentence_vector(self, text):
    #     nlp = self._load_nlp_model()
    #     doc = nlp(text)
    #     return doc.vector

    # @api.model
    # def train_model(self):
    #     questions = self.env['question_answer'].search([]).mapped('question')
    #     question_vectors = np.array([self.get_sentence_vector(self.preprocess_text(q)) for q in questions])
    #     return True
    @api.model
    def find_similar_question(self, asked_question: str='', similarity_threshold: float = 0.8):
        # asked_question ="how many pools?"


        faq=self.env['question_answer'].search([])
        if not len(faq):
            return None, None, None

        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(asked_question, convert_to_tensor=True)
        stored_questions = faq.mapped("question")


        stored_question_embeddings = model.encode(stored_questions, convert_to_tensor=True)

        # Compute cosine similarities
        similarities = util.pytorch_cos_sim(query_embedding, stored_question_embeddings)

        # Find the most similar question based on similarity threshold
        max_similarity, idx = torch.max(similarities, dim=1)
        if max_similarity.item() >= similarity_threshold:
            # faq[idx].write({
            #
            # })
            similar_question=faq[idx].question
            # print("similar_question", similar_question)
            answer=faq[idx].answer
            # print("answer", answer)
            # print("asked_question", asked_question)
            # print("faq[idx].similar_questions", faq[idx].similar_questions)
            faq[idx].write({
                "similar_questions":faq[idx].similar_questions+str(asked_question)+'\n' if  str(asked_question) not in faq[idx].similar_questions else faq[idx].similar_questions,
                "number_of_calls":faq[idx].number_of_calls+1
            })
            # self.env.cr.commit()
            # self.env.cr.savepoint()

            return asked_question, answer, 0.0

        return None, None, None

    @api.model
    def _get_vectorizer(self):
        return TfidfVectorizer()

    # @api.model
    # def train_model(self,questions):
    #     # questions = self.env['question_answer'].search([]).mapped('question')
    #     # vectorizer = self._get_vectorizer()
    #     question_vectors = np.array([self.get_sentence_vector(self.preprocess_text(q)) for q in questions])
    #     return question_vectors

    @api.model
    def find_most_similar(self, query, top_n=1):
        # hereee
        Spacytool = SpacyTool()
        questions = self.env['question_answer'].search([]).mapped('question')
        # vectorizer,question_vectors = self.train_model()  # This retrains the model each time. Consider caching for performance.
        question_vectors = Spacytool.train_model(questions)
        # query_vector = vectorizer.transform([query])
        query_vector = Spacytool.get_sentence_vector(Spacytool.preprocess_text(query))

        similarities = cosine_similarity([query_vector],question_vectors).flatten()
        top_indices = similarities.argsort()[-top_n:][::-1]

        qa_records = self.env['question_answer'].search([])
        results = []
        for i in top_indices:
            qa_record = qa_records[i]
            if similarities[i]<=0.8:
                continue
            results.append({
                'question': qa_record.question,
                'answer': qa_record.answer,
                'similarity': similarities[i],
            })
            # Increment the call count
            qa_record.number_of_calls += 1
            qa_record.similar_questions = qa_record.similar_questions + str(query)+'\n' if  str(query) not in qa_record.similar_questions else qa_record.similar_questions

        return results


    # @api.model
    def find_most_similar_spacy(self,query=None,top_n=1):
        if query is None:
            query="Hello"

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print(base_url)
        # url=f"{base_url}/spacy"
        url='http://127.0.0.1:5000/spacy'
        questions = self.env['question_answer'].search([]).mapped('question')
        answers=self.env['question_answer'].search([]).mapped('answer')





        print("url",url)
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
        res=req.json()
        # print("res",res)
        # result=res["result"]
        # print("result",result)
        # # print(req.raise_for_status())
        # # print(req)
        # print(req.json())
        return result