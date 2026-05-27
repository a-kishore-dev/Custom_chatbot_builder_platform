import json
import uuid
import streamlit as st
from dotenv import load_dotenv
from streamlit import session_state as ss
from components.config import load_config, config_form, download_config, load_document
from components.rag_chain import create_rag_chain

load_dotenv()

def config_buttons():
    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("Config"):
            config_form()
        if st.button("Load Config"):
                load_config()
        download_config()
        if st.button("Upload Document"):
            load_document()

def page():
    with st.container(horizontal=True, horizontal_alignment="right"):
        delete_current_chat()

    chat = get_current_chat()

    for message in chat["messages"]:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"], text_alignment="right")
            else:
                st.markdown(message["content"])
    
    if input_msg := st.chat_input("What is up?"):
        with st.chat_message("user"):
            st.markdown(input_msg, text_alignment="right")
        chat["messages"].append({"role":"user", "content": input_msg})
        config = {"configurable": {"session_id":chat["session_id"]}}
        chain = create_rag_chain()
        ai_response = chain.stream({"input": input_msg, **chat["config"]}, config=config)
        with st.chat_message("assistant"):
            response = st.write_stream(ai_response)
        chat["messages"].append({"role":"assistant", "content": response})

def init_state():
    if "store" not in ss:
        ss.store = {}
    if "chats" not in ss:
        first_chat_id = str(uuid.uuid4())
        
        ss.chats = {
            first_chat_id:{
                "session_id": first_chat_id,
                "messages": [],
                "config": {
                    "chatbot_name": "Default Bot",
                    "description": "Answer to the user query",
                    "tone": "Professional",
                    "domain_expertise": "Tech",
                    "forbidden_topics": "No Topics",
                    "length_preference": "short",
                },
                "vector_store": None
            }
        }

        ss.current_chat = first_chat_id

def get_current_chat():
    return ss.chats[ss.current_chat]

def create_new_chat():
    chat_id = str(uuid.uuid4())
    ss.chats[chat_id] = {
        "session_id": chat_id,
        "messages": [],
        "config": {
            "chatbot_name": "Default Bot",
            "description": "Answer to the user query",
            "tone": "Professional",
            "domain_expertise": "Tech",
            "forbidden_topics": "No Topics",
            "length_preference": "short",
        },
        "vector_store": None
    }
    ss.current_chat = chat_id

def delete_current_chat():
    if st.button("Delete"):
        current_chat_id = ss.current_chat
        del ss.chats[current_chat_id]
        if ss.chats:
            ss.current_chat = next(iter(ss.chats))
        else:
            create_new_chat()
        st.rerun()

def draw_sidebar():
    with st.sidebar:
        if st.button("+ New Page"):
            create_new_chat()
            st.rerun()
        
        st.divider()

        for chat_id, chat_data in ss.chats.items():
            first_msg = (
                chat_data["messages"][0]["content"][:10]
                if chat_data["messages"]
                else "New Chat"
            )
            if st.button(first_msg, key=chat_id):
                ss.current_chat = chat_id
                st.rerun()

init_state()
config_buttons()
page()

draw_sidebar()



# ss.chat_history = get_chat_history()
# ss.vectorstore = get_vectorstore()
# ss.chain = get_chain()