# 🦙 My Local AI (RAG System)

A private, offline AI assistant that runs entirely on your local machine. It allows you to chat with your own documents (PDFs, Text files) using the power of Llama 3, without sending any data to the cloud.

## 🚀 Features
* **100% Private:** No data leaves your computer.
* **Dual Brains:** Switch between **Llama 3.2** (Speed) and **Llama 3** (Intelligence) instantly.
* **Custom Knowledge:** Learns from your specific documents.
* **User Friendly:** Simple web interface to chat with your data.

## 🛠️ Prerequisites

Before running this, you need two things installed on your computer:

1.  **[Python](https://www.python.org/downloads/)** (Make sure to check "Add Python to PATH" during installation).
2.  **[Ollama](https://ollama.com/download)** (The engine that runs the AI models).

## 📦 Installation

1.  **Clone this repository** (or download the zip).
2.  Open a terminal (CMD) in this folder.
3.  **Install Python dependencies:**
    ```bash
    pip install streamlit langchain-community langchain-ollama faiss-cpu pypdf langchain-text-splitters
    ```
4.  **Download the AI Models:**
    ```bash
    ollama pull llama3
    ollama pull llama3.2
    ollama pull all-minilm
    ```

## 📖 How to Use

### Step 1: Add Your Documents
Place your PDF or Text files into the **`Documentz`** folder.

### Step 2: Feed the AI (Ingest)
Double-click **`1_Update_Brain.bat`**.
* This reads your files and builds the local database.
* *You only need to run this when you add new files.*

### Step 3: Start Chatting
Double-click **`2_Start_Chatting.bat`**.
* This launches the Web Interface in your browser.
* Use the **sidebar** to switch between Fast (Llama 3.2) and Smart (Llama 3) models.

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Database not found** | You forgot to run `1_Update_Brain.bat`. |
| **Ollama connection refused** | Make sure the Ollama app is running in your taskbar. |
| **Streamlit not recognized** | You missed the `pip install` step in the installation guide. |

---
*Created for personal use. Powered by Llama 3 & LangChain.*