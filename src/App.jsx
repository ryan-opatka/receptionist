import { useState, useEffect, useRef } from 'react';
import './App.css';

// Helper functions
const formatMessageText = (text) => {
  return text.split('\n').map((line, i) => {
    if (line.includes('URL:')) {
      const [label, url] = line.split('URL:').map(part => part.trim());
      return (
        <p key={i}>
          {label && `${label} `}
          <a href={url} target="_blank" rel="noopener noreferrer" className="message-link">
            {url}
          </a>
        </p>
      );
    }
    return <p key={i}>{line}</p>;
  });
};

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Question sets based on different paths
const questionSets = {
  default: [
    {
      query: "Who do I contact if I need help finding materials?",
      response: "You can contact our research librarians in several ways:\n\n1. Visit the Reference Desk on Level 1\n2. Email library@university.edu\n3. Call (555) 123-4567\n\nOur librarians are available Monday-Friday 9am-5pm.",
      mapImage: null
    },
    {
      query: "Where do I go to find 1 South?",
      response: "1 South is located on the first floor of the main library building. Take the main entrance and turn left - you'll see signs directing you to 1 South.",
      mapImage: "base64EncodedMapImage1"
    },
    {
      query: "Great. Where do I go to get to information commons?",
      response: "The Information Commons is located on Level 1 of the library. From the main entrance, walk straight ahead and you'll see the open computing area with workstations and collaborative spaces.",
      mapImage: "base64EncodedMapImage2"
    }
  ],
  information_commons: [
    {
      query: "Where is the Information Commons located?",
      response: "The Information Commons is on Level 1 of the library. Enter through the main entrance and proceed straight ahead.",
      mapImage: "base64EncodedMapImage3"
    },
    {
      query: "What resources are available in the Information Commons?",
      response: "The Information Commons offers:\n- Computer workstations\n- Printing services\n- Group study rooms\n- Technical support desk\n- Collaborative workspace\n- Scanning equipment",
      mapImage: null
    },
    {
      query: "What are the Information Commons hours?",
      response: "The Information Commons is open:\n\nMonday-Thursday: 24 hours\nFriday: 7am-8pm\nSaturday: 10am-6pm\nSunday: 10am-24 hours",
      mapImage: null
    }
  ],
  // Add more path-specific question sets as needed
};

function App() {
  // State management
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([{ 
    text: 'Welcome to the Northwestern University Library Information System!\n\nI can help you with directions or information about the library. How can I assist you?', 
    isBot: true 
  }]);
  const [currentMapImage, setCurrentMapImage] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [prefilledIndex, setPrefilledIndex] = useState(0);
  const [currentQuestionSet, setCurrentQuestionSet] = useState([]);
  const messagesEndRef = useRef(null);

  // Determine which question set to use based on URL path
  useEffect(() => {
    const path = window.location.pathname.substring(1); // Remove leading slash
    const selectedSet = questionSets[path] || questionSets.default;
    setCurrentQuestionSet(selectedSet);
    // Reset prefilled index when question set changes
    setPrefilledIndex(0);
  }, []);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Automatically populate the chat message bar for prefilled queries
  useEffect(() => {
    if (prefilledIndex < currentQuestionSet.length) {
      setInput(currentQuestionSet[prefilledIndex].query);
    }
  }, [prefilledIndex, currentQuestionSet]);

  // Handle message submission
  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    // Add user message to chat
    const userMessage = { text: input, isBot: false };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      // Check if this is a prefilled query
      if (prefilledIndex < currentQuestionSet.length) {
        // Add artificial delay for prefilled responses
        await delay(200);
        
        const prefilledResponse = currentQuestionSet[prefilledIndex];
        
        // Add bot response to chat
        const botMessage = { text: prefilledResponse.response, isBot: true };
        setMessages((prevMessages) => [...prevMessages, botMessage]);

        // Handle map image if provided
        if (prefilledResponse.mapImage) {
          setCurrentMapImage(prefilledResponse.mapImage);
          setMessages((prevMessages) => [
            ...prevMessages,
            { 
              text: "Click 'View Map' below to see the location.", 
              isBot: true,
              hasMap: true 
            }
          ]);
        }

        // Update chat history
        setChatHistory((prevHistory) => [
          ...prevHistory,
          {
            question: input,
            answer: prefilledResponse.response,
            intent: 'prefilled'
          }
        ]);

        setPrefilledIndex(prevIndex => prevIndex + 1);
      } else {
        // Make API call for non-prefilled queries
        const response = await fetch('https://library-api-713856591597.us-central1.run.app/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            message: input,
            chat_history: chatHistory
          }),
        });

        const data = await response.json();

        if (data.error) {
          throw new Error(data.error);
        }

        // Add bot response to chat
        const botMessage = { text: data.response, isBot: true };
        setMessages((prevMessages) => [...prevMessages, botMessage]);

        // Handle map image if provided
        if (data.map_image) {
          setCurrentMapImage(data.map_image);
          setMessages((prevMessages) => [
            ...prevMessages,
            { 
              text: "Click 'View Map' below to see the location.", 
              isBot: true,
              hasMap: true 
            }
          ]);
        }

        // Update chat history
        if (data.intent) {
          setChatHistory((prevHistory) => [
            ...prevHistory,
            {
              question: input,
              answer: data.response,
              intent: data.intent
            }
          ]);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: 'Sorry, there was an error processing your request. Please try again.', isBot: true }
      ]);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };

  // Rest of the component remains the same...
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  const handleViewMap = () => {
    if (currentMapImage) {
      setIsModalOpen(true);
    }
  };

  return (
    <div className="app-container">
      <h1> &nbsp;📚 University Library Receptionist &nbsp;🗺️ </h1>
      
      <div className="chat-fullscreen">
        <div className="messages-container">
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`message ${msg.isBot ? 'bot-message' : 'user-message'}`}
            >
              {msg.isBot ? (
                <>
                  {formatMessageText(msg.text)}
                  {msg.hasMap && (
                    <button 
                      className="view-map-button"
                      onClick={handleViewMap}
                    >
                      View Map
                    </button>
                  )}
                </>
              ) : (
                <p>{msg.text}</p>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="message bot-message">
              <p className="typing-indicator">Thinking...</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about directions or library information..."
            className="chat-input"
            disabled={isLoading}
          />
          <button 
            onClick={handleSendMessage} 
            className={`send-button ${isLoading ? 'disabled' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>

      {/* Map Modal */}
      {isModalOpen && currentMapImage && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button 
              className="modal-close" 
              onClick={() => setIsModalOpen(false)}
              aria-label="Close map"
            >
              ×
            </button>
            <img
              src={`data:image/png;base64,${currentMapImage}`}
              alt="Map visualization"
              className="modal-image"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;