import requests
import uuid
import os
from dotenv import load_dotenv
class Translator:
	def __init__(self):
		print("laod_env", load_dotenv())
		self.key = os.getenv("microsoft_api_key")
		self.endpoint = "https://api.cognitive.microsofttranslator.com/"
		self.server_location =  "westeurope"
		self.path = '/translate'
		self.constructed_url = self.endpoint + self.path

	def detect_language(self, text):
		print("in detect_language")
		endpoint = "https://api.cognitive.microsofttranslator.com/detect?api-version=3.0"
		headers = {
			'Content-Type': 'application/json',
			'Ocp-Apim-Subscription-Key': self.key,
			'Ocp-Apim-Subscription-Region': self.server_location,
		}
		body = [{
			'text': text
		}]
		try:
			response = requests.post(endpoint, headers = headers, json = body)
			response.raise_for_status()
			results = response.json()
			return results[0]
		except requests.exceptions.RequestException as e:
			print(f"Error occurred: {e}")
			return None
	def translate(self, question, language,flag):
		headers = {
			'Ocp-Apim-Subscription-Key': self.key,
			'Ocp-Apim-Subscription-Region': self.server_location,
			'Content-type': 'application/json',
			'X-ClientTraceId': str(uuid.uuid4())
		}

		if flag:
			params = {
				'api-version': '3.0',
				'from': 'en',
				'to': language
			}
		else:
			params = {
				'api-version': '3.0',
				'from': language,
				'to': 'en'
			}

		body = [{
			'text': question
		}]
		try:
			response = requests.post(self.constructed_url, params = params, headers = headers, json = body)
			response.raise_for_status()
			translation_result = response.json()
			# print('response', translation_result)
			# score = translation_result[0]['detectedLanguage']['score']
			# print("score", score)
			if translation_result and len(translation_result) > 0:
				return translation_result[0]['translations'][0]['text']
			else:
				return "Translation failed: No result returned"

		except requests.exceptions.RequestException as e:
			return f"Translation failed: {str(e)}"


# Example usage
# if __name__ == "__main__":
# 	key = "c47234bc98e7480c846781b49a014aa7"
# 	endpoint = "https://api.cognitive.microsofttranslator.com/"
# 	server_location = "westeurope"
#
# 	translator = Translator(key, endpoint, server_location)
#
# 	# Example: translate from Spanish to English
# 	spanish_question = "¿Cómo estás?"
# 	result = translator.translate(spanish_question, 'es')
# 	print(f"Original: {spanish_question}")
# 	print(f"Translated: {result}")