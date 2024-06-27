import os
import sys
from typing import List

import openai
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
# use bge embedding model
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from dotenv import load_dotenv, find_dotenv

# add env path
sys.path.append('../..')
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']
openai.base_url = os.environ['OPENAI_BASE_URL']

PROMPT_TEMPLATE = """
Human: You are an AI assistant, and provides answers to questions by using fact based and statistical information when possible.
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
<context>
{context}
</context>

<question>
{question}
</question>

The response should be specific and use statistics or numbers when possible.

Assistant:"""

rag_prompt = PromptTemplate(
    template=PROMPT_TEMPLATE, input_variables=["context", "question"]
)

model_name = "BAAI/bge-m3"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs, query_instruction=""
)

llm = ChatOpenAI(model_name="deepseek-chat", temperature=0)

vectorstore = Milvus(
    embedding_function=embeddings,
    connection_args={
        "uri": "./milvus_demo.db",
    },
    auto_id=True,
    drop_old=True,
)


def format_docs(docs: List[Document]):
    return "\n\n".join(doc.page_content for doc in docs)