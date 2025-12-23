import os
import shutil
import time
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# --- CONFIGURATION ---
# AUTOMATIC PATH: Finds 'Documentz' relative to this script file
current_dir = os.path.dirname(os.path.abspath(__file__))
DIRECTORY_PATH = os.path.join(current_dir, "Documentz")

DB_PATH = "./my_local_db"
EMBEDDING_MODEL = "all-minilm"

def main():
    print(f"--- Processing files from: {DIRECTORY_PATH} ---")
    
    # Check if the folder actually exists
    if not os.path.exists(DIRECTORY_PATH):
        print(f"ERROR: Could not find folder: '{DIRECTORY_PATH}'")
        print("Please check that the path is correct and the folder exists.")
        return

    # 1. Load Documents
    # silent_errors=True ensures one bad file doesn't crash the scanning
    pdf_loader = DirectoryLoader(DIRECTORY_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader, silent_errors=True)
    txt_loader = DirectoryLoader(DIRECTORY_PATH, glob="**/*.txt", loader_cls=TextLoader, silent_errors=True)

    docs = []
    try:
        print(" -> Scanning for PDFs...")
        docs.extend(pdf_loader.load())
        print(" -> Scanning for Text files...")
        docs.extend(txt_loader.load())
    except Exception as e:
        print(f"Error reading files: {e}")

    if not docs:
        print(f"ERROR: No compatible files (PDF/TXT) found in '{DIRECTORY_PATH}'!")
        return

    print(f" -> Loaded {len(docs)} documents.")

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    total_splits = len(splits)
    print(f" -> Created {total_splits} chunks of text.")

    # 3. Create FAISS Database (Bulletproof Mode)
    print(f"--- Generating Database (using {EMBEDDING_MODEL})... ---")
    
    # Clean up old DB if it exists so we start fresh
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
        except:
            pass

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = None
    
    # Process 1 by 1 with Retries
    for i, chunk in enumerate(splits):
        retry_count = 0
        max_retries = 3
        success = False
        
        while not success and retry_count < max_retries:
            try:
                print(f" -> Processing chunk {i+1}/{total_splits} (Attempt {retry_count+1})...", end="\r")
                
                if vectorstore is None:
                    vectorstore = FAISS.from_documents([chunk], embeddings)
                else:
                    vectorstore.add_documents([chunk])
                    
                success = True
                # Tiny pause to be gentle on CPU
                time.sleep(0.01) 
                
            except Exception as e:
                retry_count += 1
                print(f"\n   ! Error on chunk {i+1}: {e}")
                print(f"   ! Waiting 5 seconds before retrying...")
                time.sleep(5) # Give Ollama time to recover
        
        if not success:
            print(f"\nCRITICAL FAILURE on chunk {i+1}. Skipping it.")

    # Save final result
    print("\n--- Saving to disk... ---")
    if vectorstore:
        vectorstore.save_local(DB_PATH)
        print(f"SUCCESS: Database saved to '{DB_PATH}'")

if __name__ == "__main__":
    main()