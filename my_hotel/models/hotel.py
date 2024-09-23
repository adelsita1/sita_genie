from odoo import models, fields, api
from ..utils.open_ai_helper import PDFQuestionAnswerer
import base64
import ast
import pickle
chatbot_ai=None
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

	@api.model
	def create(self, vals):
		if 'object_field' in vals:
			vals['object_field'] = self.object_field.convert_to_column(vals['object_field'], self)
		return super(Hotel, self).create(vals)

	def process_pdf(self,question=None):
		if not question:
			question = "how many pools"
		bytes_list=[]
		# for pdf in self.pdf_ids:
		# 	print("pdf",type(pdf.read()))
		# 	# for j in pdf.read():
		# 	# 	bytes_list.append(j["pdf_file"])
		pdf_file=self.pdf_ids[0]["pdf_file"]
		pdf_bytes = base64.b64decode(pdf_file)
		# pdf_bytes = ast.literal_eval(pdf_file)

		# all_bytes=b''.join(bytes_list)
		# call ai/
		global chatbot_ai
		chatbot_ai=PDFQuestionAnswerer(pdf_bytes)
		chatbot_ai.process_pdf()
		data=chatbot_ai.answer_question(question)
		print("data",data)
		self.env["question_answer"].create({
			"question":data["Question"],
			"answer":data["Answer"],
			"cost":data["Cost"],
			"number_of_calls":1,
		})
		return data["Answer"]

		# self.answer_question(question,chatbot_ai)

	# (chatbot_ai)


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






