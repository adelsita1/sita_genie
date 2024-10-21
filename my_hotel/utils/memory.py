from openai import OpenAI
from datetime import datetime


class HierarchicalChatbot:
	def __init__(self, api_key):
		self.client = OpenAI(api_key = api_key)
		self.conversation_context = {}  # Store contexts by user_id

	def process_message(self, user_id, message):
		"""Process a message while maintaining hierarchical context"""
		# Initialize user context if not exists
		if user_id not in self.conversation_context:
			self.conversation_context[user_id] = {
				'messages': [],
				'current_topic': None,
				'topic_hierarchy': {}
			}

		# Determine if this message relates to previous context
		context_analyzer_messages = [
			{
				"role": "system",
				"content": """You are a context analyzer. Determine if the current question is:
                1. A new independent topic (return: NEW_TOPIC)
                2. A follow-up to the current topic (return: FOLLOW_UP)
                3. A reference to a specific previous topic (return: REFERENCE)

                Respond with only one of these three options followed by the topic name in brackets.
                Example: 'FOLLOW_UP [room size]' or 'NEW_TOPIC [weather]'"""
			},
			{
				"role": "user",
				"content": f"""Current topic: {self.conversation_context[user_id]['current_topic']}
                Previous messages: {str(self.conversation_context[user_id]['messages'][-3:] if self.conversation_context[user_id]['messages'] else [])}
                New message: {message}"""
			}
		]

		context_analysis = self.client.chat.completions.create(
			model = "gpt-4",
			messages = context_analyzer_messages,
			temperature = 0.3,
			max_tokens = 50
		).choices[0].message.content

		# Parse the context analysis
		context_type, topic = self._parse_context_analysis(context_analysis)

		# Build the conversation messages with appropriate context
		conversation_messages = [
			{
				"role": "system",
				"content": """You are a helpful assistant that maintains context of conversations.
                Always reference relevant previous information in your responses when appropriate.
                Be concise but informative."""
			}
		]

		# Add relevant context based on the type
		if context_type == "FOLLOW_UP":
			# Add recent messages from current topic
			conversation_messages.extend(self._get_recent_topic_messages(user_id))

		elif context_type == "REFERENCE":
			# Add messages from the referenced topic
			referenced_messages = self._get_topic_messages(user_id, topic)
			if referenced_messages:
				conversation_messages.extend(referenced_messages)

		# Add the current message
		conversation_messages.append({"role": "user", "content": message})

		# Get response from OpenAI
		response = self.client.chat.completions.create(
			model = "gpt-4",
			messages = conversation_messages,
			temperature = 0.7,
			max_tokens = 500
		)

		# Update conversation context
		self._update_context(user_id, message, response.choices[0].message.content, topic, context_type)

		return response.choices[0].message.content

	def _parse_context_analysis(self, analysis):
		"""Parse the context analysis response"""
		parts = analysis.strip().split('[')
		context_type = parts[0].strip()
		topic = parts[1].rstrip(']').strip() if len(parts) > 1 else None
		return context_type, topic

	def _get_recent_topic_messages(self, user_id, limit=5):
		"""Get recent messages from the current topic"""
		context = self.conversation_context[user_id]
		current_topic = context['current_topic']
		if current_topic in context['topic_hierarchy']:
			return context['topic_hierarchy'][current_topic][-limit:]
		return []

	def _get_topic_messages(self, user_id, topic, limit=5):
		"""Get messages from a specific topic"""
		context = self.conversation_context[user_id]
		if topic in context['topic_hierarchy']:
			return context['topic_hierarchy'][topic][-limit:]
		return []

	def _update_context(self, user_id, message, response, topic, context_type):
		"""Update the conversation context with new message and response"""
		context = self.conversation_context[user_id]

		new_messages = [
			{"role": "user", "content": message},
			{"role": "assistant", "content": response}
		]

		# Update general message history
		context['messages'].extend(new_messages)

		# Update topic hierarchy
		if context_type == "NEW_TOPIC":
			context['current_topic'] = topic
			context['topic_hierarchy'][topic] = new_messages
		else:
			if topic not in context['topic_hierarchy']:
				context['topic_hierarchy'][topic] = []
			context['topic_hierarchy'][topic].extend(new_messages)
			context['current_topic'] = topic


# Example usage
def demo_hierarchical_chat():
	chatbot = HierarchicalChatbot('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')

	# Example conversation flow
	responses = [
		chatbot.process_message(1, " the sum of 3 and 4 ?"),
		chatbot.process_message(1, "what is the capital of egypt?"),
		# chatbot.process_message(1, "Goi"),
		chatbot.process_message(1, "add to the sum 5?"),
	]

	return responses


if __name__ == "__main__":
	responses = demo_hierarchical_chat()
	for i, response in enumerate(responses, 1):
		print(f"Response {i}: {response}\n")