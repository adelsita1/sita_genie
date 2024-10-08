from odoo import models, fields, api
from ..utils.open_ai_helper import PDFQuestionAnswerer
from ..utils.translator import Translator
import base64
import ast
import pickle
from langdetect import detect, DetectorFactory
import langcodes

DetectorFactory.seed = 0

# chatbot_ai=None
# from sentence_transformers import SentenceTransformer, util
class PickleField(fields.Binary):
    def convert_to_column(self, value, record, values=None, validate=True):
        if value:
            return base64.b64encode(pickle.dumps(value))
        return None

    def convert_to_cache(self, value, record, validate=True):
        if value:
            return pickle.loads(base64.b64decode(value))
        return None
class Hotel(models.Model):
	_name = 'hotel'
	_description = 'Hotel'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	name = fields.Char(string='Hotel Name',required=True)
	address = fields.Char(string='Hotel Address')
	city = fields.Char(string='Hotel City')
	pdf_ids = fields.Many2many('pdf.file', 'hotel_id', string='PDF Files')
	account_id = fields.Many2one('ultra_message.account', string='Account ID')

	object_field = PickleField(string='Python Object')

	def write(self, vals):
		if 'object_field' in vals:
			vals['object_field'] = self.object_field.convert_to_column(vals['object_field'], self)
		return super(Hotel, self).write(vals)

	# @api.model_
	# def create(self, vals):
	# 	if 'object_field' in vals:
	# 		vals['object_field'] = self.object_field.convert_to_column(vals['object_field'], self)
	# 	return super(Hotel, self).create(vals)
	def process_pdf(self,asked_question=None):
		if not asked_question:
			asked_question = "how many pools"
		print("asked_question", asked_question)
		translator = Translator()
		lang= translator.detect_language(text=asked_question)
		print("lang",lang)
		# lang, confidence = langid.classify(asked_question)
		# lang = detect(asked_question)

		print("language:", lang['language'])
		print("score:", lang['score'])
		if lang['language'] !='en':
			translated_text = translator.translate(asked_question, lang['language'],False)
		else:
			translated_text = asked_question
		print("translated_text before spacy", translated_text)
		result = self.env['question_answer'].find_most_similar_spacy(query=translated_text)
		print("result after", result)
		if result:
			if lang['language'] != 'en':
				print("in if not english if")
				translator = Translator()
				translated_text_answer = translator.translate(result[0]["answer"], lang['language'],True)
				print("translated_text_answer",translated_text_answer)
			else:
				translated_text_answer=result[0]["answer"]
				print("result_answer",translated_text_answer)
		else:

			pdf_file=self.pdf_ids[0]["pdf_file"]
			pdf_bytes = base64.b64decode(pdf_file)


			print("in ai ")

			chatbot_ai = PDFQuestionAnswerer(pdf_bytes)
			chatbot_ai.process_pdf()
			data=chatbot_ai.answer_question(translated_text)
			if lang['language'] != 'en':
				print("in if not english else")
				translator = Translator()
				translated_text_answer = translator.translate(data["Answer"], lang['language'],True)
				print("translated_text_answer",translated_text_answer)
			else:
				translated_text_answer = data["Answer"]
				print("translated_text_answer", translated_text_answer)

			self.env["question_answer"].create({
				"question":data["Question"],
				"answer":data["Answer"],
				"cost":data["Cost"],
				"number_of_calls":1,
			})
		return translated_text_answer
	# def process_pdf(self,asked_question=None):
	#
	# 	if not asked_question:
	# 		asked_question = "how many pools"
	# 	question, answer, cost = self.env['question_answer'].find_similar_question(asked_question=asked_question)
	# 	# result = self.env['question_answer'].find_most_similar(query=asked_question)
	# 	# print("result",result)
	# 	pdf_file=self.pdf_ids[0]["pdf_file"]
	# 	pdf_bytes = base64.b64decode(pdf_file)
	# #
	# 	result_answer=answer
	# 	print("question before ai:",question)
	# 	print("answer before ai:",answer)
	# 	print("cost before ai:",cost)
	# 	if question is None and answer is None and cost is None:
	# 		print("in ai ")
	# 		# question = self.env['question_answer']
	# 		chatbot_ai = PDFQuestionAnswerer(pdf_bytes)
	# 		chatbot_ai.process_pdf()
	# 		data=chatbot_ai.answer_question(asked_question)
	# 		result_answer=data["Answer"]
	#
	# 		self.env["question_answer"].create({
	# 			"question":data["Question"],
	# 			"answer":data["Answer"],
	# 			"cost":data["Cost"],
	# 			"number_of_calls":1,
	# 		})
	# 	return result_answer
	#
	#
	#
	# 	# self.answer_question(question,chatbot_ai)
	#
	# # (chatbot_ai)


	# 	todo separate
	# def answer_question(self,question,chatbot_ai):
	# 	faq = self.env["question_answer"].search([])
	# 	print("faq",faq.read())
	# 	print("question",question)
	# 	chatbot_ai.find_similar_question(question,faq)
	#



	# def find_similar_question(self, question: str, similarity_threshold: float = 0.8) :
	# 	# if self.qa_data.empty:
	# 	# 	return None, None, None
	# 	query_embedding = self.model.encode(question, convert_to_tensor=True)
	# 	faq=self.env["question_answer"].search([])
	# 	stored_questions = faq.mapped('question')
	# 	stored_question_embeddings = self.model.encode(stored_questions, convert_to_tensor=True)
	#
	# 	# Compute cosine similarities
	# 	similarities = util.pytorch_cos_sim(query_embedding, stored_question_embeddings)
	#
	# 	# Find the most similar question based on similarity threshold
	# 	max_similarity, idx = torch.max(similarities, dim=1)
	# 	if max_similarity.item() >= similarity_threshold:
	# 		return self.qa_data.iloc[idx.item()]['Question'], self.qa_data.iloc[idx.item()]['Answer'], 0.0
	#
	# 	return None, None, None






