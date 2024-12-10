import { useState, useEffect, useRef } from 'react';
import './App.css';
import periodicals1south from './images/periodicals_1south.png';
import periodicalsroomb from './images/periodicalsroomb.png';
import periodicalsmain from './images/periodicalsmain.png';

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
      query: "I'm in an area with study tables and whiteboards, but I'm not sure where exactly I am.",
      response: `Based on your description, you might be in one of these locations:

1. 1 South Collaborative Study Area (most likely)
2. Periodicals & Newspapers Reading Room

To help you better, could you tell me:
- Do you see any signs that say "1South"?
- Are there glass-walled project rooms nearby?
- Are there computer workstations in your vicinity?`,
      mapImage: null
    },
    {
      query: "Yes, I see the 1South sign. I need to get to the Periodicals room.",
      response: `I can help you get from 1 South to the Periodicals & Newspapers Reading Room:

1. From 1 South Collaborative Study Area, head north to reach the 1South Entrance
2. From 1South Entrance, turn right and head east along the main hallway
3. Continue past the Circulation desk until you reach the café entrance
4. From To Café Bergson, continue east to reach Periodicals & Newspapers
5. Look for the newspaper racks and magazine displays`,
      mapImage: periodicals1south
    },
    {
      query: "Thanks! Are there computers I can use in Periodicals?",
      response: "Yes, the Periodicals & Newspapers Reading Room has 6 iMacs available for use, along with a color printer. You'll find them along the wall near the current periodicals section. Do you have any questions about printing or computer usage?",
      mapImage: null
    },
    {
            query: "I'm having some trouble signing into the wifi. Can you give me some instructions?",
            response: `To connect to the Northwestern University Library's wifi, use the "eduroam" network. Log in with your NetID@northwestern.edu and your password. If you encounter any issues, assistance is available through the NUIT Support Center. Are you experiencing any specific issues while trying to connect?`,
            mapImage: null
          },
          {
            query: "Can you give me instructions for printing??",
            response: `To print at the Northwestern University Library, you need to use the Northwestern Print system. First, send your print job from a library workstation or your personal device, then release the job from a library printer. A NetID and password are required to log in, and guests must request a guest NetID. Printing is only available over the Northwestern network, not the Guest-Northwestern network. Would you like more details on how to connect to the Northwestern network?`,
            mapImage: null
          },
          {
            query: "Can you give me directions now from periodicals to Project Room B?",
            response: `Directions from Periodicals & Newspapers to Project Room B:

1. From Periodicals & Newspapers, continue straight west along the hallway to reach To Café Bergson

2. Look for the staircase on your right leading up

3. From To Café Bergson, head west and slightly to your right to reach Circulation (Borrowing)

4. Look for the main service desk with self-checkout stations

5. From Circulation (Borrowing), head west and slightly to your left to reach 1South Entrance

6. From 1South Entrance, head straight south to reach 1 South Collaborative Study Area

7. Look for the large '1South' sign above the entrance

8. From 1 South Collaborative Study Area, head west and slightly to your left to reach Project Room B

9. Project Room B is located in the southwest corner of 1South`,
            mapImage: periodicalsroomb
          },
        ],
        periodicals: [
          {
            query: "How do I get to the main entrance from where I am?",
            response: `Here are the directions from Periodicals & Newspapers back to the Main Entrance:

1. From Periodicals & Newspapers, head west along the hallway to reach To Café Bergson
2. You'll pass the staircase on your left leading up
3. Head west to reach Circulation (Borrowing)
4. Look for the main service desk with self-checkout stations
5. From Circulation (Borrowing), head west reach Main Entrance`,
            mapImage: periodicalsmain
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
        await delay(1400);
        
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
        const response = await fetch('https://receptionist-api-713856591597.us-central1.run.app/api/chat', {
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
              src={currentMapImage}
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