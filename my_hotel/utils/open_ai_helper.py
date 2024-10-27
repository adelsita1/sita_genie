import gc
import os
import json
from typing import List, Tuple,Dict
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from langchain_openai import OpenAIEmbeddings
import torch

# from langchain.document_loaders import PyPDFLoader,PdfReader
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI
from langchain_community.callbacks import get_openai_callback
from dotenv import load_dotenv
import io
from openai import OpenAI as Openai
from io import BytesIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
models=["text-embedding-3-small","text-embedding-ada-002","text-embedding-3-large"]
class PDFQuestionAnswerer:
    # def __init__(self):


    def __init__(self, pdf_bytes: bytes = None,reservation_data=None,additional_context=None):
        print("laod_env",load_dotenv())
        self.pdf_bytes = pdf_bytes
        self.extra_data=reservation_data
        self.openai_api_key = os.getenv("openai_api_key")
        print("self.openai_api_key",self.openai_api_key)
        # self.client = OpenAI(self.openai_api_key)


        # client.api_key = self.openai_api_key
        # self.excel_path = excel_path
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key,model=models[1])
        self.vector_store = None
        self.qa_chain = None
        self.additional_context = additional_context

        # self.qa_data = self.load_qa_data()
        # Load SentenceTransformer model
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')


    def process_pdf(self):

        pdf_file = io.BytesIO(self.pdf_bytes)
        print("pdf_file",type(pdf_file))
        pdf = PdfReader(pdf_file)
        print("pdf_file",pdf)
        text = ""
        for _ in pdf.pages:
            text += _.extract_text()
            del _
            gc.collect()
        print("self.extra_data",self.extra_data)
        if self.extra_data is not None:
            text += "\n" + self.extra_data
        # if self.additional_context:
        #     text += "\n" + self.additional_context

        #     text = f"""
        #         Recent WhatsApp Conversation Context for this user use it to know the previous question answering:
        #         {self.additional_context}
        #
        #         PDF Content:
        #         {text}
        #         """
        # if self.extra_data is not None :
        #     text+=f"""
        #
        #     All reservation Data {self.extra_data}
        #
        #     """

        print("text of pdf",text)
        print("text_type",type(text))
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False
        )
        try:
            # Add error handling for text splitting
            texts = text_splitter.split_text(text)

            # Verify chunk sizes and log any that are too large
            for i, chunk in enumerate(texts):
                if len(chunk) > 500:
                    print(f"Warning: Chunk {i} has size {len(chunk)}")
                    # Optionally, you could further split large chunks:
                    if len(chunk) > 500:
                        subchunks = [chunk[i:i + 500] for i in range(0, len(chunk), 400)]
                        # Replace the large chunk with smaller subchunks
                        texts[i:i + 1] = subchunks

            print(texts)

        except Exception as e:
            print(f"Error during text splitting: {str(e)}")
        print("Text length: ",texts)
        print("type of text: ",type(texts))


        self.vector_store = FAISS.from_texts(texts, self.embeddings)
        print("vector store: ",self.vector_store)

        self.qa_chain = load_qa_chain(OpenAI(temperature=0, openai_api_key=self.openai_api_key),
                                      chain_type="stuff")
        print("qa chain: ",self.qa_chain)

    def extract_information(self, text: str, categories: List[str]) -> Dict:
        # Construct the prompt
        prompt = self._build_prompt(text, categories)
        try:
            # model_old="gpt-4o-mini
            client = Openai(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are a precise information extraction assistant. Extract only the specific information requested and respond in a structured format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            # Parse the response
            result = self._parse_response(response.choices[0].message.content)
            print("result extract info ",result,"===> and its type",type(result))
            return result

        except Exception as e:
            print(f"Error during extraction: {str(e)}")
            return {}

    def _parse_response(self, response_text: str) -> Dict:
        try:
            return json.loads(response_text)
        except:
            lines = response_text.split('\n')
            result = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
            return result

    def _build_prompt(self, text: str, categories: List[str]) -> str:
        """
        Build the prompt for GPT-4
        """
        categories_str = "\n".join([f"- {cat}" for cat in categories])
        prompt = f"""
        Extract the following information from the text below:

        {categories_str}

        Text to analyze:
        {text}

        Please respond in the following JSON format:
        {{
            "category1": "extracted_info1",
            "category2": "extracted_info2",
            ...
        }}

        If a category cannot be found in the text, use "Not found" as the value.
        """
        return prompt













    def answer_question(self, question: str) -> Tuple[str, float]:
        # similar_question, answer, cost = self.find_similar_question(question)
       # answer=False
        # if answer:

            # print(f"Similar question found: {similar_question}")
            # return answer, cost

        if not self.vector_store or not self.qa_chain:
            raise ValueError("PDF has not been processed. Call load_and_process_pdf() first.")

        docs = self.vector_store.similarity_search(question)

        with get_openai_callback() as cb:
            answer = self.qa_chain.run(input_documents=docs, question=question)
            cost = cb.total_cost







        # Create a new DataFrame for the new entry
        # new_entry = pd.DataFrame([{'Question': question, 'Answer': answer, 'Cost': cost}])
        # Concatenate the new entry with the existing DataFrame
        # self.qa_data = pd.concat([self.qa_data, new_entry], ignore_index=True)
        # self.save_qa_data()
        # self.clear_memory()

        data={'Question': question, 'Answer': answer, 'Cost': cost}
        print("data return from ai >>>>",data)
        return data

    def __del__(self):
        """Destructor to ensure cleanup"""
        if hasattr(self, 'pdf_bytes'):
            del self.pdf_bytes
            del self.vector_store
            del self.qa_chain
        gc.collect()
    # def clear_memory(self):
    #     del self.pdf_bytes
    #     del self.vector_store
    #     del self.qa_chain
    #     gc.collect()