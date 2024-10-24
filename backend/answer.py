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
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')

def classify_intent(query, prev_intent=None):
    """
    Classify whether the query is asking for directions or information
    using NLTK's POS tagging and keyword matching
    """
    # Lowercase the query
    query = query.lower()
    
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(query)
    tokens = [token for token in tokens if token not in stop_words]
    
    # POS tagging
    pos_tags = pos_tag(tokens)
    
    # Direction-related keywords and phrases
    direction_keywords = {
        'find', 'go', 'get', 'where', 'location', 'room', 'building',
        'floor', 'directions', 'route', 'path', 'way', 'navigate', 'walk',
        'take', 'lead', 'guide', 'there', 'that', 'here', 'entrance', 'exit',
        'near', 'closest', 'nearest'
    }
    
    # Information-related keywords and phrases
    info_keywords = {
        'what', 'how', 'when', 'who', 'why', 'tell', 'explain', 'information',
        'help', 'service', 'hour', 'time', 'policy', 'available', 'resource',
        'access', 'use', 'learn', 'about', 'detail', 'does', 'can', 'do',
        'open', 'close', 'cost', 'price', 'work'
    }
    
    # Count matches for each category
    direction_matches = sum(1 for token in tokens if token in direction_keywords)
    info_matches = sum(1 for token in tokens if token in info_keywords)
    
    # Additional weight for WH-questions
    wh_words = [token.lower() for token, pos in pos_tags if pos.startswith('W')]
    if 'where' in wh_words:
        direction_matches += 2
    if any(w in wh_words for w in ['what', 'how', 'when', 'who', 'why']):
        info_matches += 2
        
    # Verb analysis
    action_verbs = [token.lower() for token, pos in pos_tags if pos.startswith('VB')]
    if any(verb in direction_keywords for verb in action_verbs):
        direction_matches += 1
    if any(verb in info_keywords for verb in action_verbs):
        info_matches += 1
    
    # Check for pronouns that might indicate following up on directions
    if prev_intent == 'directions':
        location_pronouns = {'it', 'there', 'that', 'this', 'here'}
        if any(token in location_pronouns for token in tokens):
            direction_matches += 2
    
    # Check for pronouns that might indicate following up on information
    if prev_intent == 'information':
        info_pronouns = {'it', 'that', 'this', 'they', 'these', 'those'}
        if any(token in info_pronouns for token in tokens):
            info_matches += 2
    
    # Calculate confidence and determine intent
    total_matches = direction_matches + info_matches
    if total_matches == 0:
        # If no matches and we have previous intent, use it with lower confidence
        if prev_intent:
            return prev_intent, 0.6
        return 'information', 0.5
    
    # Return the classification with higher matches
    if direction_matches > info_matches:
        return 'directions', direction_matches / total_matches
    elif info_matches > direction_matches:
        return 'information', info_matches / total_matches
    else:
        # If tied and we have previous intent, continue with that
        if prev_intent:
            return prev_intent, 0.7
        return 'information', 0.5

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize systems
try:
    receptionist = ReceptionistSystem()
    library_rag = LibraryRAG(data_dir="library_data")
    library_rag.initialize()
    logger.info("All systems initialized successfully")
except Exception as e:
    logger.error(f"Error initializing systems: {e}")
    raise e

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

        # Get the previous intent from chat history if it exists
        prev_intent = None
        if chat_history:
            last_exchange = chat_history[-1]
            # Check if the last exchange has an intent field
            prev_intent = last_exchange.get('intent')

        # Classify the intent using the previous intent for context
        intent, confidence = classify_intent(user_query, prev_intent)
        logger.info(f"Classified intent: {intent} with confidence: {confidence}")

        # If confidence is too low, ask for clarification
        if confidence < 0.6:
            return jsonify({
                'response': "I'm not sure if you're asking for directions or information. Could you please rephrase your question?",
                'map_image': None,
                'intent': None
            })

        # Convert chat_history to the format expected by RAG
        rag_chat_history = [(msg['question'], msg['answer']) for msg in chat_history 
                           if msg.get('intent') == 'information']

        # Route to appropriate handler based on intent
        if intent == 'directions':
            result = handle_directions(user_query)
        else:  # intent == 'information'
            result = handle_information(user_query, rag_chat_history)
        
        # Add intent to the response
        result_dict = result.get_json()
        result_dict['intent'] = intent
        return jsonify(result_dict)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({
            'error': str(e),
            'response': 'An error occurred while processing your request.',
            'map_image': None,
            'intent': None
        }), 500

def handle_directions(location_query):
    """Handle directions-related queries"""
    try:
        destination = receptionist.find_closest_room_match(location_query)
        
        if not destination:
            return jsonify({
                'response': "I'm sorry, I couldn't find that location. Could you please rephrase your question?",
                'map_image': None
            })

        directions = receptionist.get_directions("mainEntrance", destination)
        receptionist.highlight_room(destination)
        
        numbered_directions = [f"{i}. {direction}" for i, direction in enumerate(directions, 1)]
        formatted_directions = "\n".join(numbered_directions)
        
        receptionist.visualize_map(nx.shortest_path(receptionist.nx_graph, "mainEntrance", destination))
        map_image = generate_map_image()
        
        return jsonify({
            'response': formatted_directions,
            'map_image': map_image
        })

    except Exception as e:
        logger.error(f"Error in handle_directions: {e}")
        return jsonify({
            'response': "Sorry, I encountered an error getting directions. Please try again.",
            'map_image': None
        })

def handle_information(info_query, chat_history):
    """Handle information-related queries"""
    try:
        logger.info(f"Processing information query: {info_query}")
        result = library_rag.query(info_query, chat_history)
        
        # Format response with answer and sources
        response_parts = [result["answer"]]
        
        if result["sources"]:
            response_parts.append("\nSources:")
            for source in result["sources"]:
                if source['url']:
                    response_parts.append(f"- {source['title']}")
                    response_parts.append(f"  URL: {source['url']}")
        
        formatted_response = "\n".join(response_parts)
        logger.info("Successfully processed information query")
        
        return jsonify({
            'response': formatted_response,
            'map_image': None
        })
        
    except Exception as e:
        logger.error(f"Error in handle_information: {e}")
        return jsonify({
            'response': "Sorry, I encountered an error getting that information. Please try again.",
            'map_image': None
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)