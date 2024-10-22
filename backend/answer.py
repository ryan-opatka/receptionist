from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_response = data.get('message')
    
    # Generate a response
    response = f"You said: {user_response} 😊"
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
