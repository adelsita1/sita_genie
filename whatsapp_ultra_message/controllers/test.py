from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from langchain_core.load import dumpd, dumps, load, loads
# from langchain.serializers import JsonSerializer
import os
from langchain_community.callbacks.manager import get_openai_callback


# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"

# Load the PDF
loader = PyPDFLoader("/home/catherinr/Desktop/SITA/SITA-Hotel-Project/serenity-alpha-fact-sheet.pdf")
pages = loader.load_and_split()

# Split the text into chunks
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(pages)

# Create embeddings and store them in a FAISS index
embeddings = OpenAIEmbeddings()
docsearch = FAISS.from_documents(texts, embeddings)

# Create a retrieval-based question-answering chain
qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.as_retriever())

string_representation = dumps(qa, pretty=True)
print("string_representation",string_representation[:500])



# Function to ask questions
# def ask_question(question):
#     return qa.invoke(question)
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
        print(f"Answer: {answer}\n")
        print(f"Cost for this question: ${cost:.4f}")
        print(f"Total Cost so far: ${total_cost:.4f}\n")
print(f"Session ended. Total Cost: ${total_cost:.4f}")