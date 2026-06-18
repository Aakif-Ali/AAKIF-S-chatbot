import streamlit as st
import faiss
import numpy as np
import PyPDF2
from langchain_ollama import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document

llm = OllamaLLM(model="mistral")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

index = faiss.IndexFlatL2(384)
vector_store = {}

def extract_text_from_pdf(uploaded_pdf):
    pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def store_in_faiss(text, filename):
    global index, vector_store

    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    texts = splitter.split_text(text)

    vectors = embeddings.embed_documents(texts)
    vectors = np.array(vectors, dtype=np.float32)

    start_idx = len(vector_store)

    for i, chunk in enumerate(texts):
        vector_store[start_idx + i] = (filename, chunk)

    index.add(vectors)

    return "Document stored successfully."

def retrieve_and_answer(query):
    global index, vector_store

    query_vector = np.array(embeddings.embed_query(query), dtype=np.float32).reshape(1, -1)

    D, I = index.search(query_vector, k=2)

    context = ""
    for idx in I[0]:
        if idx in vector_store:
            context += " ".join(vector_store[idx][1]) + "\n\n"

    if not context:
        return "No relevant documents found."
    
    return llm.invoke(f"based on the following document context, answer the question:\n\n {context}\n\nQuestion: {query}\nAnswer:")

st.title("AI Document Reader")
st.write("Upload a PDF document and ask questions about its content.")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    store_message = store_in_faiss(text, uploaded_file.name)
    st.write(store_message)

query = st.text_input("Ask a question about the document:")
if query:
    answer = retrieve_and_answer(query)
    st.subheader("AI response:")
    st.write(answer)