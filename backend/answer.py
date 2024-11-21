from flask import Flask, request, jsonify
from flask_cors import CORS
from Main_Graph import ReceptionistSystem
from library_rag import LibraryRAG
import matplotlib
import networkx as nx
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import logging
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "OPTIONS"])

# @app.before_request
# def handle_options():
#     response = app.make_default_options_response()
#     headers = response.headers

#     headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
#     headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
#     headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
#     headers["Access-Control-Allow-Credentials"] = "true"

#     return response


# CORS(app, origins=["http://localhost:5173"], methods=["GET", "POST", "OPTIONS"],
#      supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# @app.before_request
# def handle_options():
#     if request.method == "OPTIONS":
#         response = app.make_default_options_response()
#         headers = response.headers

#         headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
#         headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
#         headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

#         return response


# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize systems
try:
    receptionist = ReceptionistSystem()
    library_rag = LibraryRAG(data_dir="library_data")
    library_rag.initialize()
    logger.info("All systems initialized successfully")
except Exception as e:
    logger.error(f"Error initializing systems: {e}")
    raise e


def get_intent(query: str) -> str:
    """Simple intent classification using OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", 
                 "content": f'Is the user asking for directions? If so respond only with "DIRECTIONS". Otherwise, respond only with "INFORMATION". Query: "{query}"'}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in intent classification: {e}")
        return "INFORMATION"  # Default fallback

def generate_map_image():
    """Generate base64 encoded image from the current matplotlib figure"""
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_base64

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle incoming chat requests"""
    try:
        data = request.json
        user_query = data.get('message', '').strip()
        chat_history = data.get('chat_history', [])
        
        if not user_query:
            return jsonify({
                'response': "Please provide a question.",
                'map_image': None
            })

        # Get intent using OpenAI
        intent = get_intent(user_query).upper()
        logger.info(f"Classified intent: {intent}")

        # Handle directions
        if intent == "DIRECTIONS":
            try:
                destination = receptionist.find_closest_room_match(user_query)
                if not destination:
                    return jsonify({
                        'response': "I couldn't find that location. Could you please be more specific?",
                        'map_image': None,
                        'intent': 'directions'
                    })

                directions = receptionist.get_directions("mainEntrance", destination)
                receptionist.highlight_room(destination)
                
                numbered_directions = [f"{i}. {direction}" for i, direction in enumerate(directions, 1)]
                formatted_directions = "\n".join(numbered_directions)
                
                path = nx.shortest_path(receptionist.nx_graph, "mainEntrance", destination)
                receptionist.visualize_map(path)
                map_image = generate_map_image()
                
                return jsonify({
                    'response': formatted_directions,
                    'map_image': map_image,
                    'intent': 'directions'
                })
            except Exception as e:
                logger.error(f"Error handling directions: {e}")
                return jsonify({
                    'response': "Sorry, I had trouble getting those directions. Please try again.",
                    'map_image': None,
                    'intent': 'directions'
                })

        # Handle information
        else:
            try:
                rag_chat_history = [(msg['question'], msg['answer']) 
                                  for msg in chat_history 
                                  if msg.get('intent') == 'information']
                
                result = library_rag.query(user_query, rag_chat_history)
                
                return jsonify({
                    'response': result["answer"],
                    'map_image': None,
                    'intent': 'information'
                })
            except Exception as e:
                logger.error(f"Error handling information query: {e}")
                return jsonify({
                    'response': "Sorry, I had trouble finding that information. Please try again.",
                    'map_image': None,
                    'intent': 'information'
                })

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({
            'error': str(e),
            'response': 'An error occurred while processing your request.',
            'map_image': None,
            'intent': None
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)