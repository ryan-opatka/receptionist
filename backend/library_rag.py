# library_rag.py
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from typing import List, Dict, Any
import json
from pathlib import Path
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

class LibraryRAG:
    def __init__(
        self,
        data_dir: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the Library RAG system
        
        Args:
            data_dir: Directory containing scraped library data
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """
        # Load environment variables
        load_dotenv()
        
        # Verify API key is available
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
            
        self.data_dir = Path(data_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        self.qa_chain = None
        
        # Ensure data directory exists
        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found: {self.data_dir}")

    def process_library_data(self) -> List[Dict[str, str]]:
        """Process scraped library data into documents"""
        documents = []
        
        try:
            # Find the most recent data directory
            domain_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
            if not domain_dirs:
                raise ValueError(f"No domain directories found in {self.data_dir}")
                
            latest_domain = domain_dirs[0]
            timestamp_dirs = [d for d in latest_domain.iterdir() if d.is_dir()]
            if not timestamp_dirs:
                raise ValueError(f"No timestamp directories found in {latest_domain}")
                
            latest_dir = max(timestamp_dirs, key=lambda x: x.stat().st_mtime)
            self.logger.info(f"Using data from: {latest_dir}")
            
            # Process each category
            categories = ['contact', 'hours', 'events', 'services', 'general']
            for category in categories:
                category_dir = latest_dir / 'raw' / category
                if category_dir.exists():
                    for file in category_dir.glob('*.json'):
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                # Create structured document
                                doc = {
                                    'page_content': f"Category: {category}\nTitle: {data.get('title', '')}\n\nContent: {data.get('content', '')}",
                                    'metadata': {
                                        'url': data.get('url', ''),
                                        'category': category,
                                        'title': data.get('title', ''),
                                        'timestamp': data.get('timestamp', '')
                                    }
                                }
                                documents.append(doc)
                        except Exception as e:
                            self.logger.error(f"Error processing {file}: {e}")
                            
            if not documents:
                raise ValueError("No documents found to process")
                
            self.logger.info(f"Processed {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error processing library data: {e}")
            raise

    def create_vectorstore(self):
        """Create vector store from processed documents"""
        try:
            documents = self.process_library_data()
            
            # Split documents into chunks
            texts = []
            metadatas = []
            
            for doc in documents:
                chunks = self.text_splitter.create_documents(
                    [doc['page_content']], 
                    metadatas=[doc['metadata']]
                )
                texts.extend([chunk.page_content for chunk in chunks])
                metadatas.extend([chunk.metadata for chunk in chunks])
                
            # Create vector store
            self.vectorstore = Chroma.from_texts(
                texts=texts,
                metadatas=metadatas,
                embedding=self.embeddings
            )
            
            self.logger.info(f"Created vectorstore with {len(texts)} chunks")
            
        except Exception as e:
            self.logger.error(f"Error creating vector store: {e}")
            raise

    def setup_qa_chain(self):
        """Setup the QA chain"""
        try:
            if not self.vectorstore:
                raise ValueError("Vector store not created. Run create_vectorstore first.")
                
            llm = ChatOpenAI(
                temperature=0,
                model_name="gpt-3.5-turbo"
            )
            
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 3}
                ),
                return_source_documents=True
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up QA chain: {e}")
            raise

    def initialize(self):
        """Initialize the complete RAG system"""
        self.logger.info("Initializing RAG system...")
        self.create_vectorstore()
        self.setup_qa_chain()
        self.logger.info("RAG system initialized successfully")

    def query(self, question: str, chat_history: List = None) -> Dict[str, Any]:
        """Query the RAG system"""
        if not self.qa_chain:
            raise ValueError("RAG system not initialized. Run initialize first.")
            
        chat_history = chat_history or []
        
        try:
            # Create a library-specific prompt
            formatted_question = f"""
            Based on the Northwestern University Library information provided, please answer the following question:
            {question}
            
            If the information isn't available in the provided context, please say so.
            Include relevant details like contact information, hours, or URLs when available.
            Be concise but informative.
            """
            
            # Get response
            response = self.qa_chain(
                {"question": formatted_question, "chat_history": chat_history}
            )
            
            # Format sources
            sources = []
            for doc in response.get("source_documents", []):
                sources.append({
                    "url": doc.metadata.get("url", ""),
                    "category": doc.metadata.get("category", ""),
                    "title": doc.metadata.get("title", "")
                })
                
            return {
                "answer": response["answer"].strip(),
                "sources": sources
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise