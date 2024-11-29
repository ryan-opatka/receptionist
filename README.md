# Receptionist

## Overview

The Receptionist app is an intelligent chatbot that serves Northwestern University Library visitors. Built with a React frontend hosted on Firebase and a containerized Flask backend, it automatically understands and responds to two types of queries:

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
│   ├── library_data/          # Library information database
│   └── Dockerfile             # Docker configuration for backend
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

- Node.js & npm: https://nodejs.org/
- Docker: https://www.docker.com/
- Firebase CLI: https://firebase.google.com/docs/cli
- Git: https://git-scm.com/

### Setup Instructions

1. Clone the Repository:

```bash
git clone [repository-url]
cd receptionist
```

2. Frontend Setup:

```bash
# Install all frontend dependencies
npm install
```

3. Backend Setup:

The backend is containerized using Docker, which eliminates the need for local Python setup. Simply build the Docker image:

```bash
cd backend
docker build -t receptionist-api .
```

4. Environment Setup:
   Create a `.env` file in the backend directory:

```bash
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

1. Start the Backend Container:

```bash
docker run -p 8080:8080 --env-file .env receptionist-api
```

The API will be available at http://localhost:8080

2. Start the Frontend Locally (Development):

```bash
npm run dev
# Runs on http://localhost:5173
```

3. Deploy to Firebase:

```bash
# Build the production version
npm run build

# Deploy to Firebase
firebase deploy
```

## Features

- Automatic Query Classification: Uses NLTK to understand whether users need directions or information
- Interactive Map: Visual guidance for directions with clickable interface
- Library Information: Comprehensive answers with source citations
- Context-Aware: Maintains conversation context for natural interactions
- Rich Text Responses: Includes clickable links and formatted text
- Responsive Design: Works on all screen sizes
- Hot Module Replacement: Fast development with Vite
- Error Handling: Graceful error management and user feedback

## Usage Examples

1. Direction Queries:
```
"Where is room 101?"
"How do I get to the study area?"
"Find the computer lab"
```

2. Information Queries:
```
"What are the library hours?"
"Tell me about printing services"
"How do I reserve a study room?"
```

## Troubleshooting

1. Docker Issues:

```bash
# Check Docker container logs
docker logs [container-id]

# Rebuild Docker image
docker build --no-cache -t receptionist-api .

# Remove old containers and images
docker container prune
docker image prune
```

2. Firebase Deployment Issues:

```bash
# Check Firebase login status
firebase login

# List Firebase projects
firebase projects:list

# Clear Firebase cache
firebase deploy --only hosting --no-cache
```

3. API Connection Issues:

- Verify the API URL in your frontend configuration
- Check if Docker container is running (`docker ps`)
- Ensure environment variables are properly set
- Check Cloud Run logs in Google Cloud Console

## Development

### Frontend Development

The React frontend uses Vite and can be developed locally:

```bash
# Development with HMR
npm run dev

# Production build
npm run build

# Deploy to Firebase
firebase deploy
```

### Backend Development

The Flask backend is containerized and can be developed using Docker:

```bash
# Build the Docker image
docker build -t receptionist-api .

# Run the container with development settings
docker run -p 8080:8080 -e FLASK_ENV=development --env-file .env receptionist-api

# View logs
docker logs -f [container-id]
```

## Deployment

### Backend (Cloud Run)

The Docker container can be deployed to Google Cloud Run:

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/[PROJECT-ID]/receptionist-api

# Deploy to Cloud Run
gcloud run deploy receptionist-api \
  --image gcr.io/[PROJECT-ID]/receptionist-api \
  --platform managed \
  --allow-unauthenticated
```

### Frontend (Firebase)

Deploy the React application to Firebase Hosting:

```bash
# Build the production version
npm run build

# Deploy to Firebase
firebase deploy
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