from flask import Flask, request, jsonify
from flask_cors import CORS
from Main_Graph import ReceptionistSystem 
import matplotlib
import networkx as nx
matplotlib.use('Agg')  # Set the backend to Agg for non-interactive plotting
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create a global instance of ReceptionistSystem
receptionist = ReceptionistSystem()

def generate_map_image():
    """Capture the current matplotlib figure as a base64 encoded string"""
    # Save the current figure to a bytes buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()  # Close the figure to free memory
    
    # Encode the buffer as base64
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    return image_base64

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_query = data.get('message', '')
        
        if not user_query:
            return jsonify({
                'error': 'No message provided',
                'response': 'Please provide a question about a location.'
            }), 400

        # Process the query using ReceptionistSystem
        destination = receptionist.find_closest_room_match(user_query)
        
        if not destination:
            return jsonify({
                'response': "I'm sorry, I couldn't find that location. Could you please rephrase your question?"
            })

        # Get directions and generate visualization
        directions = receptionist.get_directions("mainEntrance", destination)
        receptionist.highlight_room(destination)
        
        # Format directions with numbers
        numbered_directions = [f"{i}. {direction}" for i, direction in enumerate(directions, 1)]
        formatted_directions = "\n".join(numbered_directions)
        
        # Generate the visualization and get it as base64
        receptionist.visualize_map(nx.shortest_path(receptionist.nx_graph, "mainEntrance", destination))
        map_image = generate_map_image()
        
        return jsonify({
            'response': formatted_directions,
            'map_image': map_image
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': 'An error occurred while processing your request.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)