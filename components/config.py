import json
import tempfile
import streamlit as st
from streamlit import session_state as ss
from components.document_ingestion import load_documents_into_vectordb

@st.dialog("Config")
def config_form():
    st.markdown("<h3>Config form</h3>", unsafe_allow_html=True)
    chatbot_name = st.text_input(label="Chatbot Name")
    description = st.text_area(label="Description")
    tone = st.selectbox(label="Tone", options=("Professional", "Casual", "Technical", "Empathetic", "Funny"))
    domain_expertise = st.text_input(label="Domain Expertise")
    forbidden_topics = st.text_area(label="Forbidden Topics")
    length_preference = st.radio(label="Response Length Preference", options=["short","medium","long"])
    if st.button("Save Config"):
        ss.chats[ss.current_chat]["config"] = {
            "chatbot_name": chatbot_name,
            "description": description,
            "tone": tone,
            "domain_expertise": domain_expertise,
            "forbidden_topics": forbidden_topics,
            "length_preference": length_preference,
        }
    return

def download_config():
    configuration_file = json.dumps(ss.chats[ss.current_chat]["config"], indent=4)
    st.download_button("Download Config", file_name="config.json", mime="application/json", data=configuration_file)
    return 

@st.dialog("Load Config")
def load_config():
    uploaded_config = st.file_uploader("Upload a config json file")
    if uploaded_config is not None:
        ss.chats[ss.current_chat]["config"] = json.load(uploaded_config)

@st.dialog("Add document")
def load_document():
    uploaded_file = st.file_uploader("Upload a Document to a Chatbot")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        load_documents_into_vectordb(temp_file_path, str(ss.chats[ss.current_chat]["session_id"]))
        st.success("File uploaded successfully")
        st.rerun()