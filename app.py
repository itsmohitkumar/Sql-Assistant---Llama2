import warnings
import psycopg2
from psycopg2 import Error
import streamlit as st
from streamlit_chat import message
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import CTransformers
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress specific warning
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")

DB_FAISS_PATH = 'vectorstore/db_faiss'

hostname = "localhost"
database = "llama"
port = 5432
username = "postgres"
password = "password"

# Cross-platform path handling
MODEL_PATH = os.path.join('models', 'llama-2-7b-chat.ggmlv3.q4_0.bin')

@st.cache_resource
def load_llm():
    try:
        if not os.path.exists(MODEL_PATH):
            st.error(f"Model file does not exist at the specified path: {MODEL_PATH}")
            return None
        logging.info(f"Loading model from {MODEL_PATH}")
        llm = CTransformers(
            model=MODEL_PATH,
            model_type="llama",
            config={"max_new_tokens": 2048, "context_length": 4096},
            temperature=0.5
        )
        logging.info("Model loaded successfully")
        return llm
    except Exception as e:
        logging.error(f"Error loading LLM: {e}")
        st.error(f"Error loading LLM: {e}")
        return None

def chunk_text(text, max_length):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def split_into_chunks(data, chunk_size=512):
    chunks = []
    current_chunk = []
    current_length = 0
    
    for item in data:
        item_length = len(str(item))
        if current_length + item_length <= chunk_size:
            current_chunk.append(item)
            current_length += item_length
        else:
            chunks.append(Document(page_content=" ".join(map(str, current_chunk))))
            current_chunk = [item]
            current_length = item_length
    
    if current_chunk:
        chunks.append(Document(page_content=" ".join(map(str, current_chunk))))
    
    return chunks

def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=hostname,
            database=database,
            user=username,
            password=password,
            port=port
        )
        return connection
    except Error as e:
        logging.error(f"Error while connecting to PostgreSQL: {e}")
        st.error(f"Error while connecting to PostgreSQL: {e}")
        return None

def fetch_data(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM world_happiness_report")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        data = [dict(zip(column_names, row)) for row in rows]
        logging.info(f"Fetched {len(data)} rows from the database")
        return data, column_names
    except Error as e:
        logging.error(f"Error fetching data: {e}")
        st.error(f"Error fetching data: {e}")
        return [], []
    finally:
        if cursor:
            cursor.close()

st.title("SQL Assistant 🦙")
st.write("Welcome to the SQL Assistant! Ask me anything about the uploaded data.")

connection = connect_to_db()
if connection:
    try:
        db_info = connection.get_dsn_parameters()
        st.write(f"Connected to PostgreSQL Server: {db_info['dbname']}")

        data, column_names = fetch_data(connection)
        
        if data:
            with st.expander("Column Names", expanded=False):
                st.write(column_names)

            chunked_data = split_into_chunks(data)
            embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})
            db = FAISS.from_documents(chunked_data, embeddings)
            db.save_local(DB_FAISS_PATH)
            
            llm = load_llm()
            if llm:
                chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever())
                
                def conversational_chat(query):
                    max_length = 400
                    chunks = chunk_text(query, max_length)
                    answers = []
                    for chunk in chunks:
                        result = chain.invoke({"question": chunk, "chat_history": st.session_state['history']})
                        answers.append(result["answer"])
                        st.session_state['history'].append((chunk, result["answer"]))
                    return " ".join(answers)

                if 'history' not in st.session_state:
                    st.session_state['history'] = []

                if 'generated' not in st.session_state:
                    st.session_state['generated'] = ["Hello! Ask me anything about the SQL data 🤗"]

                if 'past' not in st.session_state:
                    st.session_state['past'] = ["Hey! 👋"]

                response_container = st.container()
                container = st.container()

                with container:
                    with st.form(key='my_form', clear_on_submit=True):
                        user_input = st.text_input("Query:", placeholder="Ask me about the SQL data here (:", key='input')
                        submit_button = st.form_submit_button(label='Send')

                    if submit_button and user_input:
                        output = conversational_chat(user_input)
                        st.session_state['past'].append(user_input)
                        st.session_state['generated'].append(output)

                if st.session_state['generated']:
                    with response_container:
                        for i in range(len(st.session_state['generated'])):
                            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")
                            message(st.session_state["generated"][i], key=str(i), avatar_style="thumbs")
    finally:
        if connection:
            connection.close()
