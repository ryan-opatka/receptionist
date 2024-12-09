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

app = Flask(__name__)
# Allow all CORS - we'll lock this down later
CORS(app)

# Initialize OpenAI client
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Initialize systems
try:
    receptionist = ReceptionistSystem()
    library_rag = LibraryRAG(data_dir="library_data")
    library_rag.initialize()
except Exception as e:
    print(f"Error initializing systems: {e}")
    raise e

def get_intent(query: str) -> str:
    try:
        # response = client.chat.completions.create(
        response = OpenAI.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "user", 
                 "content": f'Is the user asking for directions? If so respond only with "DIRECTIONS". Otherwise, respond only with "INFORMATION". Query: "{query}"'}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in intent classification: {e}")
        return "INFORMATION"

def generate_map_image():
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_base64

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_query = data.get('message', '').strip()
        chat_history = data.get('chat_history', [])
        
        if not user_query:
            return jsonify({
                'response': "Please provide a question.",
                'map_image': None
            })

        intent = get_intent(user_query).upper()

        if intent == "DIRECTIONS":
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
        else:
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
        print(f"Error: {e}")
        return jsonify({
            'error': str(e),
            'response': 'An error occurred while processing your request.',
            'map_image': None,
            'intent': None
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)