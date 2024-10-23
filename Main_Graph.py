import matplotlib.pyplot as plt
import math
import networkx as nx
from difflib import get_close_matches

class ReceptionistSystem:
    def __init__(self):
        # Room aliases remain the same as before
        self.room_aliases = {
            "1south": "southCollaborativeStudyArea",
            "1 south": "southCollaborativeStudyArea",
            "one south": "southCollaborativeStudyArea",
            "information commons": "johnPMcGowanInformationCommons",
            "info commons": "johnPMcGowanInformationCommons",
            "project room 1134": "icProjectRoom1134",
            "vocal booth": "vocalBooth",
            "book nook": "bookNookLeisureReading",
            "leisure reading": "bookNookLeisureReading",
            "project room a": "projectRoomA",
            "project room b": "projectRoomB",
            "level 2": "toLevel2",
            "cafe": "toCafeBergson",
            "cafe bergson": "toCafeBergson",
            "lower level": "toLowerLevel",
            "admin": "administration",
            "periodicals": "periodicalsNewspapersReadingRoom",
            "newspapers": "periodicalsNewspapersReadingRoom",
            "reference": "referenceCollection",
            "circulation": "circulation",
            "borrowing": "circulation"
        }

        # Define the main hallway y-coordinate as reference
        HALLWAY_Y = 400
        
        # Updated coordinates to match the floor plan
        self.floor_plan = {
            "nodes": {
                # West end
                "mainEntrance": {"x": 100, "y": HALLWAY_Y, "label": "Main Entrance", "color": "lightgray"},
                "toLevel2": {"x": 120, "y": HALLWAY_Y - 50, "label": "To Level 2", "color": "lightgray"},
                
                # Information Commons area (large area north of hallway)
                "johnPMcGowanInformationCommons": {"x": 250, "y": HALLWAY_Y + 100, "label": "Information Commons", "color": "lightgray"},
                "icProjectRoom1134": {"x": 200, "y": HALLWAY_Y + 150, "label": "IC Project Room 1134", "color": "lightgray"},
                "vocalBooth": {"x": 300, "y": HALLWAY_Y + 150, "label": "Vocal Booth", "color": "lightgray"},
                
                # Central area
                "circulation": {"x": 400, "y": HALLWAY_Y + 20, "label": "Circulation (Borrowing)", "color": "lightgray"},
                
                # 1South entrance and room
                "southEntrance": {"x": 350, "y": HALLWAY_Y - 20, "label": "1South Entrance", "color": "lightgray"},
                "southCollaborativeStudyArea": {"x": 350, "y": HALLWAY_Y - 150, "label": "1 South Collaborative Study Area", "color": "lightgray"},
                "projectRoomB": {"x": 250, "y": HALLWAY_Y - 200, "label": "Project Room B", "color": "lightgray"},
                "projectRoomA": {"x": 450, "y": HALLWAY_Y - 200, "label": "Project Room A", "color": "lightgray"},
                
                # East central area
                "toCafeBergson": {"x": 500, "y": HALLWAY_Y + 30, "label": "To Café Bergson", "color": "lightgray"},
                "toLowerLevel": {"x": 500, "y": HALLWAY_Y - 30, "label": "To Lower Level", "color": "lightgray"},
                "bookNookLeisureReading": {"x": 500, "y": HALLWAY_Y - 100, "label": "Book Nook/Leisure Reading", "color": "lightgray"},
                
                # North tower (above Lower Level entrance)
                "personnel": {"x": 500, "y": HALLWAY_Y + 100, "label": "Personnel", "color": "lightgray"},
                "administration": {"x": 500, "y": HALLWAY_Y + 150, "label": "Administration", "color": "lightgray"},
                
                # East end
                "periodicalsNewspapersReadingRoom": {"x": 700, "y": HALLWAY_Y + 50, "label": "Periodicals & Newspapers", "color": "lightgray"},
                "referenceCollection": {"x": 700, "y": HALLWAY_Y - 50, "label": "Reference Collection", "color": "lightgray"}
            },
            "edges": [
                # Main entrance connections
                {"from": "mainEntrance", "to": "toLevel2", "weight": 50},
                {"from": "mainEntrance", "to": "johnPMcGowanInformationCommons", "weight": 150},
                
                # Information Commons internal connections
                {"from": "johnPMcGowanInformationCommons", "to": "icProjectRoom1134", "weight": 100},
                {"from": "johnPMcGowanInformationCommons", "to": "vocalBooth", "weight": 100},
                
                # Main hallway connections
                {"from": "mainEntrance", "to": "circulation", "weight": 300},
                {"from": "circulation", "to": "toCafeBergson", "weight": 100},
                
                # 1South area connections
                {"from": "circulation", "to": "southEntrance", "weight": 50},
                {"from": "southEntrance", "to": "southCollaborativeStudyArea", "weight": 150},
                {"from": "southCollaborativeStudyArea", "to": "projectRoomB", "weight": 100},
                {"from": "southCollaborativeStudyArea", "to": "projectRoomA", "weight": 100},
                
                # Central to East connections
                {"from": "circulation", "to": "toLowerLevel", "weight": 100},
                {"from": "toLowerLevel", "to": "bookNookLeisureReading", "weight": 100},
                
                # North tower connections
                {"from": "toLowerLevel", "to": "personnel", "weight": 100},
                {"from": "personnel", "to": "administration", "weight": 50},
                
                # East end connections
                {"from": "toCafeBergson", "to": "periodicalsNewspapersReadingRoom", "weight": 200},
                {"from": "periodicalsNewspapersReadingRoom", "to": "referenceCollection", "weight": 100}
            ]
        }
        
        # Create NetworkX graph for pathfinding
        self.nx_graph = nx.Graph()
        for edge in self.floor_plan["edges"]:
            self.nx_graph.add_edge(edge["from"], edge["to"], weight=edge["weight"])

    def visualize_map(self, highlight_path=None):
        """Visualize the floor plan with optional path highlighting"""
        plt.figure(figsize=(15, 10))
        
        # Plot edges first
        for edge in self.floor_plan["edges"]:
            start = self.floor_plan["nodes"][edge["from"]]
            end = self.floor_plan["nodes"][edge["to"]]
            plt.plot([start["x"], end["x"]], [start["y"], end["y"]], 
                    'k-', linewidth=1, alpha=0.5)

        # Plot main hallway as a reference line
        plt.axhline(y=400, color='gray', linestyle='--', alpha=0.3)

        # Plot nodes
        for node_id, node in self.floor_plan["nodes"].items():
            plt.plot(node["x"], node["y"], 'o', 
                    color=node["color"], markersize=12)
            # Adjust label positions based on node location relative to hallway
            if node["y"] > 400:  # Above hallway
                va = 'bottom'
            else:  # Below hallway
                va = 'top'
            plt.text(node["x"] + 5, node["y"], node["label"], 
                    fontsize=8, ha='left', va=va)

        # Highlight path if specified
        if highlight_path:
            for i in range(len(highlight_path) - 1):
                start = self.floor_plan["nodes"][highlight_path[i]]
                end = self.floor_plan["nodes"][highlight_path[i + 1]]
                plt.plot([start["x"], end["x"]], [start["y"], end["y"]], 
                        'r-', linewidth=2)

        plt.title("Library Floor Plan Navigation")
        plt.xlabel("West → East")
        plt.ylabel("South → North")
        plt.grid(True)
        
        # Set fixed aspect ratio and adjust limits
        plt.axis('equal')
        plt.xlim(50, 800)
        plt.ylim(150, 650)
        
        # Add compass direction
        plt.text(750, 600, 'N↑', fontsize=12, ha='center')
        
        plt.show()

    # Rest of the methods remain the same as in the previous version
    def find_closest_room_match(self, query):
        """Find the closest matching room from the query using room aliases"""
        query = query.lower().strip()
        
        if query in self.room_aliases:
            return self.room_aliases[query]
            
        possible_matches = []
        for alias, room_id in self.room_aliases.items():
            if query in alias or alias in query:
                possible_matches.append(room_id)
                
        if possible_matches:
            return possible_matches[0]
            
        room_labels = {node["label"].lower(): room_id 
                      for room_id, node in self.floor_plan["nodes"].items()}
        matches = get_close_matches(query, room_labels.keys(), n=1, cutoff=0.6)
        
        if matches:
            return room_labels[matches[0]]
        return None

    def get_directions(self, start, goal):
        """Generate natural language directions between two points"""
        try:
            path = nx.shortest_path(self.nx_graph, start, goal, weight="weight")
            
            directions = []
            for i in range(len(path) - 1):
                current = self.floor_plan["nodes"][path[i]]["label"]
                next_stop = self.floor_plan["nodes"][path[i + 1]]["label"]
                directions.append(f"Go from {current} to {next_stop}")
                
            return directions
        except nx.NetworkXNoPath:
            return ["No path found between these locations."]

    def highlight_room(self, room_id):
        """Reset all rooms to default color and highlight the specified room"""
        for node in self.floor_plan["nodes"].values():
            node["color"] = "lightgray"
            
        if room_id in self.floor_plan["nodes"]:
            self.floor_plan["nodes"][room_id]["color"] = "red"

    def process_query(self, query):
        """Process a user query and return directions and visualization"""
        destination = self.find_closest_room_match(query)
        
        if not destination:
            return "I'm sorry, I couldn't find that location. Could you please rephrase?"
            
        directions = self.get_directions("mainEntrance", destination)
        self.highlight_room(destination)
        
        path = nx.shortest_path(self.nx_graph, "mainEntrance", destination)
        self.visualize_map(highlight_path=path)
        
        return "\n".join(directions)

# Example usage
if __name__ == "__main__":
    receptionist = ReceptionistSystem()
    
    # Test queries
    test_queries = [
        "How do I get to 1South?",
        "Where is the Information Commons?",
        "I need to find the Reference Collection",
        "How do I get to Project Room A?",
        "Where is the Circulation desk?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = receptionist.process_query(query)
        print("Directions:")
        print(response)