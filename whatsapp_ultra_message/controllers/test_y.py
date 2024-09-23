import os
import json
import faiss
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
# from langchain.llms import OpenAI
# from langchain.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_openai_callback

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
def deserialize_vectors_data(filename="vectors.json"):
	with open(filename, "r") as f:
		data = json.load(f)
	vectors = np.array(data["vectors"], dtype = np.float32)
	documents = data["documents"]

	return vectors, documents


# Function to serialize FAISS index
def serialize_vectors_from_qa(qa, filename="vectors.json"):
    # Extract FAISS retriever from qa chain
    docsearch = qa.retriever.vectorstore

    # Extract document vectors and metadata (text and ids)
    vectors = docsearch.index.reconstruct_n(0, docsearch.index.ntotal).tolist()  # Extract vectors
    documents = [{"text": doc.page_content, "metadata": doc.metadata} for doc in docsearch.docstore._dict.values()]

    # Store everything in a dictionary
    data = {
        "vectors": vectors,
        "documents": documents
    }

    # Save to JSON file
    with open(filename, "w") as f:
        json.dump(data, f)


# Load the PDF
# loader = PyPDFLoader("/home/catherine/Desktop/youssefModules/GenerativeAI/Day 4 LangChain -Agent-Chain/serenity-alpha-fact-sheet.pdf")
loader = PyPDFLoader("/home/catherinr/Desktop/SITA/SITA-Hotel-Project/serenity-alpha-fact-sheet.pdf")
pages = loader.load_and_split()

# Split the text into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(pages)

# Create embeddings and store them in a FAISS index
embeddings = OpenAIEmbeddings()
docsearch = FAISS.from_documents(texts, embeddings)

# Create a retrieval-based question-answering chain
qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.as_retriever())
print("qa",qa)
# Serialize the FAISS index to a JSON file
serialize_vectors_from_qa(qa, "vectors.json")
# Function to ask questions

def ask_question(qa, question):
    with get_openai_callback() as cb:
        answer = qa.invoke(question)
        return answer, cb.total_cost


total_cost = 0
# Example usage
if __name__ == "__main__":
    while True:
        user_question = input("Enter your question (or 'quit' to exit): ")
        if user_question.lower() == 'quit':
            break
        answer, cost = ask_question(qa, user_question)
        total_cost += cost

        print(f"Answer: {answer}\n")
        print(f"Cost for this question: ${cost:.4f}")
        print(f"Total Cost so far: ${total_cost:.4f}\n")
print(f"Session ended. Total Cost: ${total_cost:.4f}")