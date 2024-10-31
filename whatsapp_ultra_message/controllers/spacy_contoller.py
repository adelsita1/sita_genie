import json

from odoo import http
from odoo.http import request
import spacy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class SPacyController(http.Controller):
    model = spacy.load('en_core_web_md')
    # model = spacy.load('en_core_web_lg')
    print("here")
    @http.route('/spacy', type="json", auth="public", website=True, method=['POST', 'GET'])
    def spacy_contoller_silimlarity(self):
        data = json.loads(request.httprequest.data.decode('utf-8'))
        print(data)
        query = data['query']
        questions = data['questions']
        print("query", query)
        print("questions", questions)
        input_doc = self.model(query)
        list_docs = [self.model(text) for text in questions]
        similarities = np.array([input_doc.similarity(doc) for doc in list_docs])
        print("similarities", similarities)

        most_similar_index = np.argmax(similarities)
        print("most_similar_index", most_similar_index)
        print(f"Most similar string: {questions[most_similar_index]}")
        print(f"Similarity score: {similarities[most_similar_index]}")
        qa_records = request.env['question_answer'].sudo().search([])
        result = []

        if similarities[most_similar_index] == 1:
            result.append({
                'question': qa_records[most_similar_index].question,
                'answer': qa_records[most_similar_index].answer,
                'similarity': most_similar_index,
            })
            # Increment the call count
            # qa_records[most_similar_index].number_of_calls += 1
            # qa_records[most_similar_index].similar_questions = qa_records[most_similar_index].similar_questions + str(query) + '\n' if str(
            #     query) not in qa_records[most_similar_index].similar_questions else qa_records[most_similar_index].similar_questions

        return result


def get_sentence_vector(self, text):
    doc = self.model(text)
    return doc.vector


def train_model(self, questions):
    question_vectors = np.array([self.get_sentence_vector(self.preprocess_text(q)) for q in questions])
    return question_vectors


def preprocess_text(self, text):
    doc = self.model(text)
    return " ".join([token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct])

