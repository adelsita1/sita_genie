import spacy
import numpy as np

class SpacyTool:
    def __init__(self):
        self.model=spacy.load('en_core_web_md')


    def get_sentence_vector(self, text):
        # nlp = self._load_nlp_model()
        doc = self.model(text)
        return doc.vector

    def train_model(self, questions):
        # questions = self.env['question_answer'].search([]).mapped('question')
        # vectorizer = self._get_vectorizer()
        question_vectors = np.array([self.get_sentence_vector(self.preprocess_text(q)) for q in questions])
        return question_vectors

    # @api.model
    def preprocess_text(self, text):
        # nlp = self._load_nlp_model()
        doc = self.model(text)
        return " ".join([token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct])
