import os
from typing import List, Tuple
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback


class PDFQuestionAnswerer:
    def __init__(self, pdf_path: str, openai_api_key: str, excel_path: str):
        self.pdf_path = pdf_path
        self.openai_api_key = openai_api_key
        self.excel_path = excel_path
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.vector_store = None
        self.qa_chain = None
        self.qa_data = self.load_qa_data()
        # Load SentenceTransformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_qa_data(self):
        if os.path.exists(self.excel_path):
            return pd.read_excel(self.excel_path)
        return pd.DataFrame(columns=['Question', 'Answer', 'Cost'])

    def save_qa_data(self):
        self.qa_data.to_excel(self.excel_path, index=False)

    def load_and_process_pdf(self):
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()
        print("documents",documents)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
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


def main():
    # pdf_path = "/home/catherine/Desktop/youssefModules/GenerativeAI/Day 4 LangChain -Agent-Chain/serenity-alpha-fact-sheet.pdf"
    pdf_path= "/home/catherinr/Desktop/SITA/SITA-Hotel-Project/serenity-alpha-fact-sheet.pdf"

    excel_path = "/home/catherinr/Desktop/SITA/odoo/odoo17/custom_community/whatsapp_ultra_message/controllers/qa_database.xlsx"

    # os.environ["OPENAI_API_KEY"] = openai_api_key

    # qa_system = PDFQuestionAnswerer(pdf_path, self.openai_api_key,),
    # qa_system.load_and_process_pdf()

    total_cost = 0.0

    while True:
        question = input("Enter your question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        answer, cost = qa_system.answer_question(question)
        total_cost += cost
        print(f"Answer: {answer}")
        print(f"Cost for this question: ${cost:.4f}")
        print(f"Total cost so far: ${total_cost:.4f}\n")

    print(f"Total cost for all questions: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
