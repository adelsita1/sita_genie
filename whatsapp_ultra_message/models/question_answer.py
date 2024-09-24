from odoo import fields, models, api
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
class QuestionAnswers(models.Model):
    _name = 'question_answer'
    _description = 'Description'
    _rec_name = 'question'
    question = fields.Text(required=True,string="Question")
    answer=fields.Text(required=True,string="Answer")
    similar_questions = fields.Text(default='')

    number_of_calls=fields.Integer()
    cost=fields.Float(string="Cost")


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

    @api.model
    def train_model(self):
        questions = self.env['question_answer'].search([]).mapped('question')
        vectorizer = self._get_vectorizer()
        question_vectors = vectorizer.fit_transform(questions)
        return vectorizer,question_vectors

    @api.model
    def find_most_similar(self, query, top_n=1):
        vectorizer,question_vectors = self.train_model()  # This retrains the model each time. Consider caching for performance.
        query_vector = vectorizer.transform([query])

        similarities = cosine_similarity(query_vector,question_vectors).flatten()
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

        return results