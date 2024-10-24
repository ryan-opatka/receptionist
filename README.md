# Receptionist

## Overview

The Receptionist app is an intelligent chatbot that serves Northwestern University Library visitors. Built with a React frontend and Flask backend, it automatically understands and responds to two types of queries:
1. Providing directions within the library building using a graph-based pathfinding system
2. Answering questions about library information, services, and resources using a RAG (Retrieval-Augmented Generation) model

The project uses Vite for fast development with modern JavaScript tooling, NLTK for natural language processing, and includes comprehensive library information retrieval capabilities.

## Project Structure

```
receptionist/
├── backend/
│   ├── answer.py               # Flask backend with routing and intent classification
│   ├── Main_Graph.py          # Graph-based pathfinding for directions
│   ├── library_rag.py         # RAG model for library information
│   └── library_data/          # Library information database
├── public/                     # React public files
├── src/
│   ├── App.jsx                # Main React component
│   └── App.css                # Application styles
├── package.json               # React dependencies
├── vite.config.js             # Vite configuration
└── README.md                  # Documentation
```

## Installation

### Prerequisites

Download and install these tools first:
- Node.js & npm: [https://nodejs.org/](https://nodejs.org/)
- Python 3.8+: [https://www.python.org/](https://www.python.org/)
- Git: [https://git-scm.com/](https://git-scm.com/)

### Setup Instructions

1. **Clone the Repository**:
```bash
git clone [repository-url]
cd receptionist
```

2. **Frontend Setup**:
```bash
# Install all frontend dependencies
npm install
```

3. **Backend Setup**:

Virtual Environment (Recommended but Optional):
```bash
# Create and activate virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Unix/macOS:
source venv/bin/activate
```

Why use a virtual environment? (not necessary, recommended.)
- Isolates project dependencies from system Python
- Prevents conflicts between different project requirements
- Makes project more portable and reproducible
- Easier to manage package versions
- Simple to recreate the environment on other machines

Install Dependencies:
```bash
# Install all required packages (with or without venv)
pip install Flask flask-cors nltk networkx matplotlib openai langchain chromadb tiktoken sqlalchemy python-dotenv

# Download required NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('stopwords')"
```

4. **Environment Setup**:
Create a `.env` file in the backend directory:
```bash
OPENAI_API_KEY=your_api_key_here
```

### Starting the Application

1. **Start the Frontend**:
```bash
npm run dev
# Runs on http://localhost:5173
```

2. **Start the Backend**:
```bash
cd backend
python answer.py
# Runs on http://localhost:5000
```

## Features

- **Automatic Query Classification**: Uses NLTK to understand whether users need directions or information
- **Interactive Map**: Visual guidance for directions with clickable interface
- **Library Information**: Comprehensive answers with source citations
- **Context-Aware**: Maintains conversation context for natural interactions
- **Rich Text Responses**: Includes clickable links and formatted text
- **Responsive Design**: Works on all screen sizes
- **Hot Module Replacement**: Fast development with Vite
- **Error Handling**: Graceful error management and user feedback

## Usage Examples

1. **Direction Queries**:
```
"Where is room 101?"
"How do I get to the study area?"
"Find the computer lab"
```

2. **Information Queries**:
```
"What are the library hours?"
"Tell me about printing services"
"How do I reserve a study room?"
```

The system automatically determines query type and provides appropriate responses, including:
- Step-by-step directions with interactive maps
- Detailed information with source citations
- Clickable links to relevant resources

## Troubleshooting

1. **Installation Issues**:
```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules
npm install

# Recreate Python environment
deactivate  # if using venv
pip install -r requirements.txt
```

2. **CORS Issues**: 
- Verify flask-cors is installed
- Check CORS configuration in answer.py
- Ensure both servers are running

3. **Connection Problems**:
- Frontend should be on http://localhost:5173
- Backend should be on http://localhost:5000
- Check if ports are available

4. **Dependencies Issues**:
```bash
# Update all dependencies
npm update  # for frontend
pip install --upgrade -r requirements.txt  # for backend
```

## Development

### Frontend Development
The React frontend uses Vite for:
- Hot Module Replacement (HMR)
- Fast refresh during development
- Optimized builds

```bash
# Development with HMR
npm run dev

# Production build
npm run build
```

### Backend Development
The Flask backend supports:
- API routing
- NLTK processing
- Map generation
- RAG model integration

```bash
# Run with debug mode
export FLASK_ENV=development  # Unix/macOS
set FLASK_ENV=development    # Windows
python answer.py
```

## API Documentation

### POST /api/chat
Accepts JSON with:
```json
{
  "message": "user query string",
  "chat_history": [
    {
      "question": "previous question",
      "answer": "previous answer",
      "intent": "previous intent"
    }
  ]
}
```

Returns:
```json
{
  "response": "bot response string",
  "map_image": "base64 encoded image (optional)",
  "intent": "classified intent"
}
```

## License

This project is open source and available under the MIT License.

## Contributors

Please check the project contributors page for a list of developers who have contributed to this project.