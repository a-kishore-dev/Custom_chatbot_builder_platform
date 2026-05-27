
from operator import itemgetter
from streamlit import session_state as ss
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.chat_history import InMemoryChatMessageHistory
from components.prompt_template import create_chatprompt_template


def get_by_session_id(session_id: str):
    if session_id not in ss.store:
        ss.store[session_id] = InMemoryChatMessageHistory()
    return ss.store[session_id]

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_rag_chain():
    prompt_template = create_chatprompt_template()
    gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", streaming=True)
    groq_llm = ChatGroq(model="llama-3.1-8b-instant", streaming=True)
    if ss.chats[ss.current_chat].get("vector_store"):
        retriever = ss.chats[ss.current_chat]["vector_store"].as_retriever(search_kwargs={"k": 3})
        chain = (
            RunnablePassthrough.assign(
                context=itemgetter("input") | retriever | format_docs
            )
            | prompt_template
            | groq_llm
        )
    else:
        chain = (
            RunnablePassthrough.assign(
                context= lambda _:"No context"
            )
            | prompt_template
            | groq_llm
        )
    chain_with_history = RunnableWithMessageHistory(
        chain,
        input_messages_key="input",
        history_messages_key="history",
        get_session_history=get_by_session_id,
    )
    return chain_with_history

        
        