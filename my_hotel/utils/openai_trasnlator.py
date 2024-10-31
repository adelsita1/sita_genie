import ast
import json
import re

from openai import OpenAI

# Set up your OpenAI API key
api_key = "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"
client = OpenAI(api_key=api_key)
def detect_and_translate(text, target_language="English"):
    # Create a prompt for language detection and translation
    prompt = f"Detect the language of the following text, and translate it to {target_language}:\n\n{text}\n\nRespond with the detected language, followed by the translation."

    response = client.chat.completions.create(
        model="gpt-4o",
        # engine="text-davinci-004",  # You can use other engines as well, like gpt-4 if available.
        messages=[
            {"role": "system",
             "content": "You are a perfect translator Detect the language of the following text, and translate it to {target_language}:\n\n{text}\n\n Respond in JSON format with the detected language and translation"},
            {"role": "user", "content": prompt}
        ],

    )

    # Get the response text
    print("response",response)


    result = response.choices[0].message.content.strip().replace("'", "").replace("\n","")
    cleaned_text = re.sub(r"^```json|```$", "", result.strip(), flags = re.MULTILINE)
    print("cleaned_text",ast.literal_eval(cleaned_text))
    return result

# Example usage
text = "please wait for life agent will reply to you"
target_language = "Arabic"
translation = detect_and_translate(text, target_language)
# print(translation)
