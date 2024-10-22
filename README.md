# Receptionist Chatbot App

## Overview

The Receptionist app is a simple chatbot built using a React frontend and a Flask backend. The app starts by asking the user, "Where are you going?" and takes the user's input to send it to a Python script (answer.py). The script processes the input and returns a response, which is displayed back to the user along with a happy emoji.

This project is based on a React + Vite template for fast development, using modern JavaScript tooling, and it includes a Flask backend for handling API requests.

## Project Structure

receptionist/
├── backend/
│   └── answer.py               # Flask backend that handles chatbot logic
├── public/                     # React public files
├── src/
│   └── App.jsx                 # React app where UI and fetch requests are handled
├── package.json                # React dependencies and scripts
├── vite.config.js              # Vite configuration for the React app
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore configuration

### Frontend: React + Vite

This project uses Vite, a fast build tool that provides Hot Module Replacement (HMR) for a smooth developer experience. The React frontend is a minimal setup that is easy to expand and customize.

The Vite template used for this project is based on the following plugins:
- @vitejs/plugin-react which uses Babel for fast refresh during development.
- @vitejs/plugin-react-swc which uses SWC for fast refresh as well.

### Backend: Flask API

The Flask backend serves an API that accepts user input and returns a processed response.

- answer.py: This file defines a simple Flask server. It exposes a /api/chat route where POST requests containing the user's message are handled. The server repeats the message back to the user, appending a happy emoji (😊).

### Setup Instructions

#### Prerequisites

- Node.js: Install from https://nodejs.org/.
- Python: Install from https://www.python.org/.

### Running the Project

1. Install Frontend Dependencies:

   In the project root directory (receptionist/), run:

   npm install

2. Start the React Frontend:

   Run the following command in the root directory:

   npm run dev

   This will start the React app at http://localhost:5173.

3. Set Up and Run the Flask Backend:

   Navigate to the backend/ directory and install Flask and the flask-cors package:

   cd backend
   pip install Flask flask-cors

   Then, run the Flask server:

   python answer.py

   The Flask backend will run on http://localhost:5000.

### Modifying the Chatbot Logic

To modify the chatbot's response behavior, edit the answer.py file.

1. Locate the /api/chat endpoint in answer.py:

   This endpoint processes the user input and returns a response. The current functionality repeats the user's message and adds a happy emoji.

   @app.route('/api/chat', methods=['POST'])
   def chat():
       data = request.json
       user_response = data.get('message')
       
       # Modify this logic to change the chatbot's behavior
       response = f"You said: {user_response} 😊"
       
       return jsonify({'response': response})

2. Modify the Response Logic:

   You can modify the logic in the chat() function to handle more complex responses. For example, you can add conditional statements, interact with other APIs, or add natural language processing (NLP) to generate more meaningful replies.

   Example modification:

   @app.route('/api/chat', methods=['POST'])
   def chat():
       data = request.json
       user_response = data.get('message')

       # Custom logic to modify response
       if "work" in user_response.lower():
           response = "You're heading to work! 🚀"
       else:
           response = f"You said: {user_response} 😊"

       return jsonify({'response': response})

### CORS Configuration

The app uses Flask-CORS to handle Cross-Origin Resource Sharing (CORS) between the React frontend and Flask backend. This is set up in answer.py like so:

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

### Vite + React Setup

This project is scaffolded using Vite, a next-generation frontend tooling that offers superior speed in development.

- Hot Module Replacement (HMR): Vite automatically updates changes in your React components without reloading the page.
- ESLint Configuration: The project includes basic ESLint rules for linting your code.

To modify the frontend, edit the src/ directory where the React components are located. For example, App.jsx is the main file handling the user interface and API requests.

### Troubleshooting

1. CORS Errors: If you encounter CORS-related issues, ensure that flask-cors is installed and that CORS(app) is present in answer.py.
2. Backend Not Running: Ensure that the Flask backend is running by checking http://localhost:5000 in your browser or terminal.
3. Frontend Issues: If the frontend doesn’t load, ensure that npm run dev is running and visit http://localhost:5173.

### License

This project is open source and available under the MIT License.
