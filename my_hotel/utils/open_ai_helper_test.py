
import gc
import os
import json
from typing import List, Tuple,Dict
import pandas as pd
from langchain.docstore import InMemoryDocstore
from langchain.agents import initialize_agent, AgentType
from langchain.chains.conversation.base import ConversationChain
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import ChatPromptTemplate
from sentence_transformers import SentenceTransformer, util
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
import torch
import faiss
from ..utils.format_dict_to_text import json_to_short_text
from memory_profiler import profile
log_file=open("/home/catherinr/Desktop/SITA/odoo/odoo17/memory.log","w+")
# from langchain.document_loaders import PyPDFLoader,PdfReader
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI

from langchain_community.callbacks import get_openai_callback
from langchain.tools import Tool
from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
    
import io
from openai import OpenAI as Openai
from langchain.memory import ConversationBufferMemory,ConversationSummaryMemory,CombinedMemory
from langchain.docstore.document import Document
from langchain.chains import create_retrieval_chain,ConversationalRetrievalChain
from io import BytesIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
models=["text-embedding-3-small","text-embedding-ada-002","text-embedding-3-large"]
class PDFQuestionAnswerer:
    # def __init__(self):

    # @profile
    def __init__(self, pdf_bytes: bytes = None,reservation_data=None,additional_context=None):
        self.faiss_index = None
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
        self.memory=None
        self.tools=None
        self.llm=None
        self.Prompt=None
        self.Prompt_Template=None


        # self.qa_data = self.load_qa_data()
        # Load SentenceTransformer model
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')

    @profile
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
        self.llm=OpenAI(temperature=0, openai_api_key=self.openai_api_key)

        #
        # for message in self.memory.chat_memory.messages:
        #     print("message",message)
        #     print("type(message)",type(message))
            # print("Memoryyyyy>>>",f"{message['type'].capitalize()}: {message['data']['content']}")
        self.vector_store = FAISS.from_texts(texts, self.embeddings)
        print("vector store: ",self.vector_store)
        prompt_template = """
                Summary of Chat Conversation:
                {chat_history}

                Current Question: {question}

                Please provide an answer based on both the context and the summary of chat conversation:
                """
        self.Prompt = PromptTemplate(
            input_variables=["chat_history", "context", "question"],
            template=prompt_template
        )
        # self.qa_chain = load_qa_chain(llm=self.llm,
        #                       chain_type="stuff")

        doc_embeddings = self.embeddings.embed_documents(texts)
        print("doc_embeddings",doc_embeddings)
        dimension = len(doc_embeddings[0])  # Get the dimensionality of the embeddings
        index = faiss.IndexFlatL2(dimension)  # Using L2 (Euclidean distance) for similarity

        # Create the document store (stores the texts and links them to the FAISS vectors)
        docstore = InMemoryDocstore({
            i: Document(page_content=texts[i]) for i in range(len(texts))
        })
        print("docstore", docstore)
        index_to_docstore_id = {i: i for i in range(len(texts))}
        print("index_to_docstore_id", index_to_docstore_id)
        self.faiss_index = FAISS(embedding_function=self.embeddings,
                                 index=index,
                                 docstore=docstore,
                                 index_to_docstore_id=index_to_docstore_id)
        # self.faiss_index=FAISS(doc_embeddings, index)
        self.faiss_index.add_texts(texts)


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

    def answer_question_new_not(self, question: str) -> Tuple[str, float]:
        if not self.vector_store or not self.qa_chain:
            raise ValueError("PDF has not been processed. Call load_and_process_pdf() first.")

        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key=question,
        )

        # Add previous context to memory
        for message in self.additional_context:
            if message['direction'] == "sent":
                if message['body'] == "please wait for life agent will reply to you":
                    continue
                self.memory.chat_memory.add_ai_message(message['body'])
            else:
                self.memory.chat_memory.add_user_message(message['body'])

        # Create summary memory
        summary_memory = ConversationSummaryMemory(
            llm=self.llm,
            memory_key="chat_summary",
            input_key=question,

        )

        # Combine memories
        combined_memory = CombinedMemory(
            memories=[self.memory, summary_memory],
        )

        # Context
        # from documents: {context}
        # Create proper prompt template with all required variables
        prompt_template = """
        
        Chat History: {chat_history}
        Chat Summary: {chat_summary}
        Human: {question}
        Assistant: Let me help you with that.
        """

        # prompt = PromptTemplate(
        #     input_variables=["context", "chat_history", "chat_summary", "input"],
        #     template=prompt_template
        # )
        prompt = PromptTemplate(
            input_variables=[ "chat_history", "chat_summary", "question", "question"],
            template=prompt_template
        )

        # Initialize conversation chain with correct memory and prompt
        # conversation = ConversationChain(
        #     llm=self.llm,
        #     prompt=prompt,
        #     memory=combined_memory,
        #     verbose=True,
        #
        # )

        # Get relevant documents
        docs = self.vector_store.similarity_search(question)
        context = "\n".join([doc.page_content for doc in docs])

        # Create tools with proper input handling
        self.tools = [
            Tool(
                name="FAISS",
                func=lambda q: self.qa_chain.run(input_documents=docs, question=q),
                description="Use this to search from FAISS if answer is not available from the conversation summary"
            ),
            # Tool(
            #     name="ConversationHistory",
            #     func=lambda q: conversation.run(
            #         question=q,
            #         context=context
            #     ),
            #     description="Use this when the answer is available from the conversation summary"
            # )
        ]

        # Initialize agent with updated tools
        agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

        # Run agent with the question
        answer = agent.run(question)

        return {
            'Question': question,
            'Answer': answer,
            'Cost': 0.00001  # Consider implementing actual cost tracking
        }

    def answer_question(self, question):
        print("answer_question answer_question")

        condense_question_system_template = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )

        condense_question_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", condense_question_system_template),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.faiss_index.as_retriever(), condense_question_prompt
        )

        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
            ]
        )
        qa_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        convo_qa_chain = create_retrieval_chain(history_aware_retriever, qa_chain)
        answer=convo_qa_chain.invoke(
            {
                "input": question,
                "chat_history": [],
            }
        )
        print("Answer: ", answer)
        # memory = ConversationBufferMemory(
        #     memory_key="chat_history", return_messages=True
        # )
        # retriever_chain = ConversationalRetrievalChain(
        #     retriever=self.faiss_index.as_retriever(),
        #     memory=memory,
        #
        # )
        # retriever_chain=create_retrieval_chain(retriever=retriever)

        # answer = retriever_chain.run(input=question)
        print("answer in qa fasis",answer)
        data = {'Question': question, 'Answer': answer["answer"], 'Cost': 0.00001}
        return data

    def answer_question_old(self, question: str) -> Tuple[str, float]:
        # similar_question, answer, cost = self.find_similar_question(question)
       # answer=False
        # if answer:

            # print(f"Similar question found: {similar_question}")
            # return answer, cost

        if not self.vector_store or not self.qa_chain:
            raise ValueError("PDF has not been processed. Call load_and_process_pdf() first.")
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key="input", question="question")
        for message in self.additional_context:
            if message['direction'] == "sent":  # ai
                if message['body'] == "please wait for life agent will reply to you":
                    continue
                self.memory.chat_memory.add_ai_message(message['body'])
            else:
                self.memory.chat_memory.add_user_message(message['body'])
        docs = self.vector_store.similarity_search(question)
        print("type of docs", type(docs))

        summary_memory = ConversationSummaryMemory(llm=self.llm, input_key="input")
        combined_memory = CombinedMemory(memories=[self.memory, summary_memory])
        formatted_context_history=json_to_short_text(self.additional_context)
        prompt = self.Prompt.format(question=question, chat_history=formatted_context_history)
        conversation = ConversationChain(llm=self.llm, prompt=prompt, verbose=True, memory=combined_memory)
        self.tools = [
            Tool(name="FAISS", func=self.qa_chain.run,
                 description="Use this to Search From FAISS if answer is not available from the summary of the "
                             "conversation"),
            Tool(name="ConversationHistory", func=conversation.run,
                 description="Use this when the answer is available from the summary of the conversation")

        ]

        print("qa chain: ", self.qa_chain)





        agent = initialize_agent(self.tools, self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

        answer=agent.run(question)
        # with get_openai_callback() as cb:

            # chat_history=self.memory.load_memory_variables({})
            # inputs = {
            #     'input_documents': docs,  # List of documents
            #     'question': question,  # Question to be answered
            #     "chat_history": chat_history.get("chat_history")
            #
            # }
            # answer = self.qa_chain.run(inputs)
            # cost = cb.total_cost







        # Create a new DataFrame for the new entry
        # new_entry = pd.DataFrame([{'Question': question, 'Answer': answer, 'Cost': cost}])
        # Concatenate the new entry with the existing DataFrame
        # self.qa_data = pd.concat([self.qa_data, new_entry], ignore_index=True)
        # self.save_qa_data()
        # self.clear_memory()

        # data={'Question': question, 'Answer': answer, 'Cost': 0.00001}
        # print("data return from ai >>>>",data)
        # return data

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