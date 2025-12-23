import streamlit as st
import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- CONFIGURATION ---
DB_PATH = "./my_local_db"
EMBEDDING_MODEL = "all-minilm"

# --- PAGE SETUP ---
st.set_page_config(page_title="My Local AI", page_icon="🤖", layout="wide")
st.title("🤖 My Local AI Assistant")

# --- SIDEBAR: THE CONTROL CENTER ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("---")
    
    # THE SWITCHER: Choose your Brain
    model_choice = st.radio(
        "Choose Model:", 
        ("Llama 3.2 (Fast)", "Llama 3 (Smart)")
    )
    
    # Map the choice to the actual computer name
    if model_choice == "Llama 3.2 (Fast)":
        active_model = "llama3.2"
        st.caption("🚀 Optimized for speed. Best for quick summaries.")
    else:
        active_model = "llama3"
        st.caption("🧠 Optimized for intelligence. Best for complex reasoning.")
    
    st.markdown("---")
    
    # Clear Chat Button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- LOAD RESOURCES ---
@st.cache_resource(show_spinner=False)
def load_resources(model_name):
    # 1. Load Database
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    retriever = None
    if os.path.exists(DB_PATH):
        try:
            vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        except:
            pass

    # 2. Setup the Brain (Dynamic Model Name)
    llm = ChatOllama(model=model_name, keep_alive="5m")
    
    # 3. Setup Prompt
    template = """You are a helpful assistant. Answer based ONLY on the context below.
If you don't know, say so.

Context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    return retriever, chain

# Load the model selected in the sidebar
retriever, chain = load_resources(active_model)

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Input
if query := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    if retriever:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(f"*Thinking using {active_model}...*")
            
            try:
                docs = retriever.invoke(query)
                context_text = "\n\n".join([d.page_content for d in docs])
                response = chain.invoke({"context": context_text, "question": query})
                
                message_placeholder.markdown(response)
                
                with st.expander("📚 View Sources"):
                    for d in docs:
                        source = os.path.basename(d.metadata.get('source', 'Unknown'))
                        st.write(f"- {source}")
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                message_placeholder.error(f"Error: {e}")
    else:
        st.error("Database not found! Run Ingest first.")