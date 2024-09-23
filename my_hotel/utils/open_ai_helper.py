import os
from typing import List, Tuple
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
# from langchain.document_loaders import PyPDFLoader,PdfReader
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
from dotenv import load_dotenv
import io

class PDFQuestionAnswerer:
    def __init__(self, pdf_bytes: bytes):
        load_dotenv()
        self.pdf_bytes = pdf_bytes
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        # self.excel_path = excel_path
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.vector_store = None
        self.qa_chain = None
        self.qa_data = self.load_qa_data()
        # Load SentenceTransformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def process_pdf(self):
        pdf_file = io.BytesIO(self.pdf_bytes)
        pdf = PdfReader(pdf_file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_text(text)
        print("Text length: ",texts)
        print("type of text: ",type(texts))


        self.vector_store = FAISS.from_texts(texts, self.embeddings)
        self.qa_chain = load_qa_chain(OpenAI(temperature=0, openai_api_key=self.openai_api_key),
                                      chain_type="stuff")

    def find_similar_question(self, question: str, similarity_threshold: float = 0.8) -> Tuple[str, str, float]:
        if self.qa_data.empty:
            return None, None, None
        query_embedding = self.model.encode(question, convert_to_tensor=True)
        stored_questions = self.qa_data['Question'].tolist()
        stored_question_embeddings = self.model.encode(stored_questions, convert_to_tensor=True)

        # Compute cosine similarities
        similarities = util.pytorch_cos_sim(query_embedding, stored_question_embeddings)

        # Find the most similar question based on similarity threshold
        max_similarity, idx = torch.max(similarities, dim=1)
        if max_similarity.item() >= similarity_threshold:
            return self.qa_data.iloc[idx.item()]['Question'], self.qa_data.iloc[idx.item()]['Answer'], 0.0

        return None, None, None

    def answer_question(self, question: str) -> Tuple[str, float]:
        similar_question, answer, cost = self.find_similar_question(question)
        if answer:
            print(f"Similar question found: {similar_question}")
            return answer, cost

        if not self.vector_store or not self.qa_chain:
            raise ValueError("PDF has not been processed. Call load_and_process_pdf() first.")

        docs = self.vector_store.similarity_search(question)

        with get_openai_callback() as cb:
            answer = self.qa_chain.run(input_documents=docs, question=question)
            cost = cb.total_cost

        # Create a new DataFrame for the new entry
        new_entry = pd.DataFrame([{'Question': question, 'Answer': answer, 'Cost': cost}])
        # Concatenate the new entry with the existing DataFrame
        self.qa_data = pd.concat([self.qa_data, new_entry], ignore_index=True)
        self.save_qa_data()

        return answer, cost
