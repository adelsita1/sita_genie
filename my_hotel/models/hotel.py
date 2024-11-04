from odoo import models, fields, api
from ..utils.open_ai_helper import PDFQuestionAnswerer
from ..utils.translator import Translator
from ..utils.format_dict_to_text import format_row, json_to_short_text, format_phone_number
import base64
import ast
import pickle
import re
from langdetect import detect, DetectorFactory
import langcodes
import gc
# from arabic_reshaper import reshape
# from bidi.algorithm import get_display

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
    name = fields.Char(string='Hotel Name', required=True)
    address = fields.Char(string='Hotel Address')
    city = fields.Char(string='Hotel City')
    pdf_ids = fields.Many2many('pdf.file', 'hotel_id', string='PDF Files')
    account_id = fields.Many2one('ultra_message.account', string='Account ID')

    object_field = PickleField(string='Python Object')
    question_answer_id = fields.Many2one('question_answer', string='Question Answer')
    answer_status = fields.Selection(
        related='question_answer_id.answer_status',
        string="Answer Status",
        readonly=True
    )


    def write(self, vals):
        if 'object_field' in vals:
            vals['object_field'] = self.object_field.convert_to_column(vals['object_field'], self)
        return super(Hotel, self).write(vals)

    # @api.model_
    # def create(self, vals):
    # 	if 'object_field' in vals:
    # 		vals['object_field'] = self.object_field.convert_to_column(vals['object_field'], self)
    # 	return super(Hotel, self).create(vals)

    def process_pdf(self, asked_question=None, partner_id=None):
        chatbot_ai = PDFQuestionAnswerer()

        print("partner_id ----", partner_id)
        if partner_id:
            partner_obj = self.env['res.partner'].search([('id', '=', partner_id)])
        else:
            partner_obj = None
        answer_stat = None
        is_life_agent = False
        if not asked_question:
            asked_question = "payment policy"
        print("asked_question", asked_question)
        #
        # translator = Translator()
        # lang = translator.detect_language(text=asked_question)
        lang = chatbot_ai.detect_language(text=asked_question)
        print("lang", lang)
        # lang, confidence = langid.classify(asked_question)
        # lang = detect(asked_question)
        # reservation = self.check_reservation_text(asked_question)
        # print("language:", lang['language'])
        # print("score:", lang['score'])
        if lang != 'en':
            # translated_text = translator.translate(asked_question, lang['language'], False)
            translated_text_answer = self.env["hotel.translation.rules"].replace_words(asked_question,lang)
            print(" after translated_text_answer in ", translated_text_answer)
            translated_text = chatbot_ai.detect_and_translate(translated_text_answer, target_language="English")


        else:
            translated_text = asked_question
        print("translated_text before spacy", translated_text)
        reservation = self.check_reservation_text(translated_text)
        if not reservation:

            result = self.env['question_answer'].find_most_similar_spacy(query=translated_text)
            if result:
                result = result["result"]  # for spacy controller
            # result = self.env['question_answer'].find_similar_question(asked_question=translated_text)

            print("result after", result)
        else:
            result = False
            if partner_obj:
                partner_obj.create_lead()

        if result:
            if lang != 'en':
                print("in if not english if")
                # translator = Translator()
                # translated_text_answer = translator.translate(result[0]["answer"], lang['language'], True)
                translated_text_answer = chatbot_ai.detect_and_translate(result[0]["answer"], target_language=lang)
                translated_text_answer = self.env["hotel.translation.rules"].replace_words(translated_text_answer,
                                                                                           lang)
                print("translated_text_answer", translated_text_answer)
            else:
                translated_text_answer = result[0]["answer"]
                translated_text_answer = self.env["hotel.translation.rules"].replace_words(translated_text_answer, "en")
                print("result_answer", translated_text_answer)
            answer_stat = self.answer_status = 'ai'
        else:
            pdf_bytes = "".encode("utf-8")
            for file in self.pdf_ids:
                pdf_file = file["pdf_file"]
                print("pdf_file", type(pdf_file))
                pdf_bytes += base64.b64decode(pdf_file)
                print("pdf_bytes", type(pdf_bytes))
            reservation_data = self.get_rooms_data()
            # pdf_bytes+=reservation_data
            # source_data=pdf_bytes.decode("utf-8")
            # print("source_data",source_data)
            whatsapp_context = self.get_recent_whatsapp_context(partner_id)


            chatbot_ai.process_pdf(pdf_bytes, additional_context=whatsapp_context,
                                             reservation_data=reservation_data)
            data = chatbot_ai.answer_question(translated_text)
            if lang=='ar':
                print("in lang arabic ",lang)
                answer = self.enforce_ltr_numbers(data)
                data = answer
            print("answer", data)
            gc.collect()
            print("data---after gc", chatbot_ai)
            # field_info = self.fields_get(['answer_status'])
            # print("field_info",field_info)
            # selection_options = field_info['selection']
            # for option in selection_options:
            # 	if option[0] == 'ai':
            # 		answer_status = option[1]
            answer_s = self.answer_status = 'ai'
            uncertain_phrases = ["I'm sorry", "I don't know", "don't know", "I'm not sure",
                                 "That information is not available",
                                 "Not mentioned in context", "I can't answer that", "I'm not sure",
                                 "it's not mentioned in the document.",
                                 "I don't have that information.", "I can't answer that",
                                 "I don't have enough context to answer",
                                 "I don’t have access to that knowledge", "don't have enough information", "I am an AI"]
            for sentence in uncertain_phrases:
                sentence_lower = sentence.lower()
                if data.lower() == sentence_lower or data.lower() in sentence_lower or sentence_lower in data.lower():
                    # life_agent = self.env['life.agent'].create({
                    # 	'question': asked_question,
                    # 	'state': 'waiting'
                    # })
                    # self.asked_life_agent(asked_question)
                    data = "please wait for life agent will reply to you"

                    answer_s = self.answer_status = 'life_agent'
                    is_life_agent = True

            # if any(phrase in data['Answer'] for phrase in uncertain_phrases):

            print("in if any")
            answer_stat = answer_s
            print("answer_stat", answer_stat)
            if lang != 'en':
                print("in if not english else")
                # translator = Translator()
                # translated_text_answer = translator.translate(data["Answer"], lang['language'], True)
                translated_text_answer = chatbot_ai.detect_and_translate(data,
                                                                         target_language=lang)

                print("translated_text_answer before", translated_text_answer)
                translated_text_answer = self.env["hotel.translation.rules"].replace_words(translated_text_answer,
                                                                                           lang)
                print("translated_text_answer after", translated_text_answer)
                if "+20" in  translated_text_answer:
                    format_phone_number(translated_text_answer)
            else:
                translated_text_answer = data
                translated_text_answer = self.env["hotel.translation.rules"].replace_words(translated_text_answer, "en")

                print("translated_text_answer", translated_text_answer)
            self.env["question_answer"].create({
                "question": translated_text,
                "answer": data,
                "cost": 0.03,
                "number_of_calls": 1,
                "answer_status": answer_s,
                "check_life_agent": is_life_agent
            })
            if reservation:
                data = translated_text + " -> " + data
                if partner_obj:
                    partner_obj.create_lead(data)

        return translated_text_answer, answer_stat

    def enforce_ltr_numbers(self,text):
        phone_pattern = r"(\(\+\d{1,3}\)\s?\d+(\s?\d+)*)"
        def add_ltr_marks(match):
            return f"\u200E{match.group(0)}\u200E"

        formatted_text = re.sub(phone_pattern, add_ltr_marks, text)

        return formatted_text
    def get_rooms_data(self):
        fields = ["display_name", "occupancy", "meal_type", "date_from", "date_to", "rate_egp", "rate_usd"]
        rates = self.env["hotel.room.rate"].search([]).read(fields)
        # reservation_text = "\n".join([format_row(item) for item in rates])
        rules = self.env["hotel.rate.rule"].search([]).read(["name"])
        # rules_text="\n".join([rule for rule in rules])
        rooms = self.env["hotel.room.type"].search([]).read(["name", "description"])
        dic_all = rates + rules + rooms
        text_return = json_to_short_text(dic_all)

        # rooms_text="\n".join([format_row(room) for room in rooms])
        # all_text= reservation_text  + "\n" + rules_text + "\n" + rooms_text
        # print("all_text", text_return)
        return text_return

    def check_reservation_text(self, given_text):
        keywords = self.env["hotel.reservation.keywords"].sudo().search([]).mapped("name")
        existence = [True if word.lower() in given_text.lower() else False for word in keywords]
        return any(existence)

    def get_recent_whatsapp_context(self, partner_id):
        WhatsAppMessage = self.env['whatsapp_message_log']
        recent_messages = WhatsAppMessage.search(
            [("partner_id", "=", partner_id)],
            order='sent_datetime desc',
            limit=10
        )
        context_messages = []
        for msg in recent_messages:
            context_messages.append({
                "direction": msg.direction,
                "body": msg.message_body
            })

        return context_messages
