import matplotlib.pyplot as plt
import math
import networkx as nx
from difflib import get_close_matches

class ReceptionistSystem:
    def __init__(self):
        # Room aliases for common terms and variations
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
            "borrowing": "circulation",
            "help desk": "circulation",
            "front desk": "circulation",
            "main desk": "circulation",
            "computers": "johnPMcGowanInformationCommons",
            "study rooms": "southCollaborativeStudyArea",
            "group study": "southCollaborativeStudyArea",
            "quiet reading": "bookNookLeisureReading",
            "stairs up": "toLevel2",
            "stairs down": "toLowerLevel",
            "staff offices": "administration",
            "recording booth": "vocalBooth"
        }

        # Area descriptors for lost users
        self.area_descriptors = {
            "large open space with computers": ["johnPMcGowanInformationCommons"],
            "quiet study area with tables": ["southCollaborativeStudyArea", "periodicalsNewspapersReadingRoom"],
            "near stairs": ["toLevel2", "toLowerLevel", "toCafeBergson"],
            "near entrance": ["mainEntrance", "southEntrance"],
            "near bookshelves": ["referenceCollection", "bookNookLeisureReading"],
            "small rooms": ["projectRoomA", "projectRoomB", "icProjectRoom1134", "vocalBooth"],
            "service desk": ["circulation", "administration"],
            "glass walls": ["projectRoomA", "projectRoomB", "icProjectRoom1134"],
            "main hallway": ["mainEntrance", "circulation", "toCafeBergson"],
            "computers and printers": ["johnPMcGowanInformationCommons"],
            "study tables": ["southCollaborativeStudyArea", "periodicalsNewspapersReadingRoom"],
            "help desk area": ["circulation"],
            "comfortable seating": ["bookNookLeisureReading"],
            "staff area": ["personnel", "administration"],
            "meeting rooms": ["projectRoomA", "projectRoomB"],
            "recording space": ["vocalBooth"]
        }

        # Location features and details
        self.location_features = {
            "mainEntrance": {
                "features": ["automatic doors", "security gates", "welcome desk", "building directory"],
                "nearby": ["information commons", "level 2 stairs"],
                "identifiers": ["main doors", "security gates", "entrance mat"]
            },
            "johnPMcGowanInformationCommons": {
                "features": ["computer workstations", "large open space", "help desk", "printers"],
                "nearby": ["main entrance", "project rooms", "vocal booth"],
                "identifiers": ["rows of computers", "printing station", "help desk"]
            },
            "southCollaborativeStudyArea": {
                "features": ["group study tables", "whiteboard walls", "1South sign", "collaborative space"],
                "nearby": ["project rooms", "main hallway"],
                "identifiers": ["1South sign", "study tables", "whiteboards"]
            },
            "projectRoomA": {
                "features": ["glass walls", "conference table", "wall-mounted display", "whiteboard"],
                "nearby": ["1South study area", "project room B"],
                "identifiers": ["room number", "glass-walled room", "meeting space"]
            },
            "projectRoomB": {
                "features": ["glass walls", "conference table", "wall-mounted display", "whiteboard"],
                "nearby": ["1South study area", "project room A"],
                "identifiers": ["room number", "glass-walled room", "meeting space"]
            },
            "icProjectRoom1134": {
                "features": ["glass walls", "technology setup", "presentation screen"],
                "nearby": ["information commons", "vocal booth"],
                "identifiers": ["room 1134", "IC project room", "glass walls"]
            },
            "vocalBooth": {
                "features": ["soundproof walls", "recording equipment", "microphone"],
                "nearby": ["information commons", "project room 1134"],
                "identifiers": ["recording booth", "soundproof room"]
            },
            "circulation": {
                "features": ["service desk", "self-checkout machines", "hold shelf"],
                "nearby": ["main hallway", "café entrance", "1South entrance"],
                "identifiers": ["main desk", "checkout stations", "help desk"]
            },
            "toCafeBergson": {
                "features": ["staircase", "café signage", "seating area"],
                "nearby": ["circulation desk", "periodicals"],
                "identifiers": ["café sign", "upward stairs", "coffee shop entrance"]
            },
            "toLowerLevel": {
                "features": ["staircase", "level signage", "directory"],
                "nearby": ["book nook", "personnel offices"],
                "identifiers": ["downward stairs", "lower level sign"]
            },
            "bookNookLeisureReading": {
                "features": ["comfortable seating", "magazine displays", "quiet area"],
                "nearby": ["lower level stairs", "reference collection"],
                "identifiers": ["casual seating", "reading nook"]
            },
            "administration": {
                "features": ["staff offices", "administrative suite", "meeting room"],
                "nearby": ["personnel office", "lower level entrance"],
                "identifiers": ["admin suite", "staff area"]
            },
            "periodicalsNewspapersReadingRoom": {
                "features": ["newspaper racks", "magazine displays", "study tables", "current periodicals"],
                "nearby": ["reference collection", "café entrance"],
                "identifiers": ["newspaper racks", "magazine shelves"]
            },
            "referenceCollection": {
                "features": ["reference books", "study carrels", "quiet area"],
                "nearby": ["periodicals room", "book nook"],
                "identifiers": ["reference shelves", "study carrels"]
            },
            "personnel": {
                "features": ["staff offices", "workroom"],
                "nearby": ["administration", "lower level entrance"],
                "identifiers": ["staff offices", "personnel sign"]
            },
            "toLevel2": {
                "features": ["staircase", "level signage", "directory"],
                "nearby": ["main entrance", "information commons"],
                "identifiers": ["upward stairs", "level 2 sign"]
            },
            "southEntrance": {
                "features": ["entrance doors", "1South signage", "study area entrance"],
                "nearby": ["circulation desk", "collaborative study area"],
                "identifiers": ["1South entrance", "study area doors"]
            }
        }

        # Define the main hallway y-coordinate as reference
        HALLWAY_Y = 400
        
        # Floor plan configuration
        self.floor_plan = {
            "nodes": {
                # West end
                "mainEntrance": {"x": 100, "y": HALLWAY_Y, "label": "Main Entrance", "color": "lightgray"},
                "toLevel2": {"x": 120, "y": HALLWAY_Y - 50, "label": "To Level 2", "color": "lightgray"},
                
                # Information Commons area
                "johnPMcGowanInformationCommons": {"x": 250, "y": HALLWAY_Y + 100, "label": "Information Commons", "color": "lightgray"},
                "icProjectRoom1134": {"x": 200, "y": HALLWAY_Y + 150, "label": "IC Project Room 1134", "color": "lightgray"},
                "vocalBooth": {"x": 300, "y": HALLWAY_Y + 150, "label": "Vocal Booth", "color": "lightgray"},
                
                # Central area
                "circulation": {"x": 400, "y": HALLWAY_Y + 20, "label": "Circulation (Borrowing)", "color": "lightgray"},
                
                # 1South area
                "southEntrance": {"x": 350, "y": HALLWAY_Y - 20, "label": "1South Entrance", "color": "lightgray"},
                "southCollaborativeStudyArea": {"x": 350, "y": HALLWAY_Y - 150, "label": "1 South Collaborative Study Area", "color": "lightgray"},
                "projectRoomB": {"x": 250, "y": HALLWAY_Y - 200, "label": "Project Room B", "color": "lightgray"},
                "projectRoomA": {"x": 450, "y": HALLWAY_Y - 200, "label": "Project Room A", "color": "lightgray"},
                
                # East central area
                "toCafeBergson": {"x": 500, "y": HALLWAY_Y + 30, "label": "To Café Bergson", "color": "lightgray"},
                "toLowerLevel": {"x": 500, "y": HALLWAY_Y - 30, "label": "To Lower Level", "color": "lightgray"},
                "bookNookLeisureReading": {"x": 500, "y": HALLWAY_Y - 100, "label": "Book Nook/Leisure Reading", "color": "lightgray"},
                
                # North tower
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
                
                # Information Commons connections
                {"from": "johnPMcGowanInformationCommons", "to": "icProjectRoom1134", "weight": 100},
                {"from": "johnPMcGowanInformationCommons", "to": "vocalBooth", "weight": 100},
                
                # Main hallway connections
                {"from": "mainEntrance", "to": "circulation", "weight": 300},
                {"from": "circulation", "to": "toCafeBergson", "weight": 100},
                
                # 1South connections
                {"from": "circulation", "to": "southEntrance", "weight": 50},
                {"from": "southEntrance", "to": "southCollaborativeStudyArea", "weight": 150},
                {"from": "southCollaborativeStudyArea", "to": "projectRoomB", "weight": 100},
                {"from": "southCollaborativeStudyArea", "to": "projectRoomA", "weight": 100},
                
                # East central connections
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
        
        # Initialize NetworkX graph for pathfinding
        self.nx_graph = nx.Graph()
        for edge in self.floor_plan["edges"]:
            self.nx_graph.add_edge(edge["from"], edge["to"], weight=edge["weight"])

    def find_user_location(self, description: str, additional_details: str = None) -> dict:
        """Attempt to determine user's location based on their description."""
        description = description.lower()
        potential_locations = {}
        
        # First pass: Check for exact room numbers or names
        for alias, room_id in self.room_aliases.items():
            if alias in description:
                return {
                    "locations": [{
                        "id": room_id,
                        "name": self.floor_plan["nodes"][room_id]["label"],
                        "confidence": 1.0
                    }],
                    "needs_clarification": False
                }
        
        # Second pass: Parse area descriptors
        for descriptor, locations in self.area_descriptors.items():
            if descriptor in description:
                for location in locations:
                    if location not in potential_locations:
                        potential_locations[location] = 0.0
                    potential_locations[location] += 0.3
        
        # Third pass: Check for specific features
        for location, details in self.location_features.items():
            for feature in details["features"]:
                if feature in description:
                    if location not in potential_locations:
                        potential_locations[location] = 0.0
                    potential_locations[location] += 0.4
            
            for nearby in details["nearby"]:
                if nearby in description:
                    if location not in potential_locations:
                        potential_locations[location] = 0.0
                    potential_locations[location] += 0.2
        
        # Sort and format results
        sorted_locations = sorted(
            [(k, v) for k, v in potential_locations.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        results = []
        for location_id, confidence in sorted_locations[:3]:
            results.append({
                "id": location_id,
                "name": self.floor_plan["nodes"][location_id]["label"],
                "confidence": min(1.0, confidence)
            })
        
        return {
            "locations": results,
            "needs_clarification": len(results) > 1 or (results and results[0]["confidence"] < 0.7)
        }

    def get_clarifying_questions(self, potential_locations: list) -> list:
        """Generate relevant follow-up questions based on potential locations."""
        questions = []
        
        # Get unique features from potential locations
        all_features = set()
        for loc in potential_locations:
            if loc["id"] in self.location_features:
                all_features.update(self.location_features[loc["id"]]["features"])
        
        # Generate specific questions
        questions.extend([
            f"Do you see any of these features: {', '.join(list(all_features)[:3])}?",
            "Are you near any stairs or elevators?",
            "Can you see any room numbers or signs?",
            "Are you in a quiet study area or a more active space?",
            "Do you see any service desks or help stations nearby?",
            "Are there computer workstations in your vicinity?"
        ])
        
        return questions

    def handle_lost_user(self, initial_description: str, destination: str = None) -> dict:
        """Main method to handle a lost user scenario and provide directions to a destination."""
        # First attempt to locate user
        location_results = self.find_user_location(initial_description)
        
        response = {
            "possible_locations": location_results["locations"],
            "needs_clarification": location_results["needs_clarification"],
            "clarifying_questions": [],
            "directions": []
        }
        
        # If we need more information
        if location_results["needs_clarification"]:
            response["clarifying_questions"] = self.get_clarifying_questions(
                location_results["locations"]
            )
        # If we're confident about the location and have a destination
        elif location_results["locations"] and destination:
            start_location = location_results["locations"][0]["id"]
            dest_location = self.find_closest_room_match(destination)
            
            if dest_location:
                response["directions"] = self.get_directions(
                    start_location, 
                    dest_location
                )
                
                # Highlight the path on the map
                self.highlight_room(dest_location)
                path = nx.shortest_path(self.nx_graph, start_location, dest_location)
                self.visualize_map(path)
        # If we're confident about location but no destination specified
        elif location_results["locations"]:
            start_location = location_results["locations"][0]["id"]
            response["directions"] = self.get_directions(
                start_location, 
                "mainEntrance"  # Default to main entrance only if no destination specified
            )
            
            # Highlight the path on the map
            self.highlight_room("mainEntrance")
            path = nx.shortest_path(self.nx_graph, start_location, "mainEntrance")
            self.visualize_map(path)
        
        return response

    def visualize_map(self, highlight_path=None):
        """Visualize the floor plan with optional path highlighting."""
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

    def find_closest_room_match(self, query):
        """Find the closest matching room from the query using room aliases."""
        if not query:
            return None
            
        query = query.lower().strip()
        
        # Direct match in aliases
        if query in self.room_aliases:
            return self.room_aliases[query]
        
        # Look for substring matches
        longest_match = ""
        matched_room = None
        for alias, room_id in self.room_aliases.items():
            if alias in query and len(alias) > len(longest_match):
                longest_match = alias
                matched_room = room_id
                
        if matched_room:
            return matched_room
        
        # Try fuzzy matching as a last resort
        room_labels = {node["label"].lower(): room_id 
                    for room_id, node in self.floor_plan["nodes"].items()}
        matches = get_close_matches(query, room_labels.keys(), n=1, cutoff=0.6)
        
        if matches:
            return room_labels[matches[0]]
        return None

    def get_directions(self, start, goal):
        """Generate step-by-step directions between two locations."""
        try:
            path = nx.shortest_path(self.nx_graph, start, goal, weight="weight")
            
            directions = []
            for i in range(len(path) - 1):
                current_node = self.floor_plan["nodes"][path[i]]
                next_node = self.floor_plan["nodes"][path[i + 1]]
                
                # Calculate relative position (left/right/ahead)
                dx = next_node["x"] - current_node["x"]
                dy = next_node["y"] - current_node["y"]
                
                # Get current and next location names
                current_name = current_node["label"]
                next_name = next_node["label"]
                
                # Generate direction based on relative positions
                if abs(dx) > abs(dy):  # Primarily east-west movement
                    if dx > 0:
                        if dy > 20:  # Slightly north
                            directions.append(f"From {current_name}, head east and slightly to your right to reach {next_name}")
                        elif dy < -20:  # Slightly south
                            directions.append(f"From {current_name}, head east and slightly to your left to reach {next_name}")
                        else:
                            directions.append(f"From {current_name}, continue straight east along the hallway to reach {next_name}")
                    else:
                        if dy > 20:  # Slightly north
                            directions.append(f"From {current_name}, head west and slightly to your right to reach {next_name}")
                        elif dy < -20:  # Slightly south
                            directions.append(f"From {current_name}, head west and slightly to your left to reach {next_name}")
                        else:
                            directions.append(f"From {current_name}, continue straight west along the hallway to reach {next_name}")
                else:  # Primarily north-south movement
                    if dy > 0:
                        if dx > 20:  # Slightly east
                            directions.append(f"From {current_name}, turn right and head north to reach {next_name}")
                        elif dx < -20:  # Slightly west
                            directions.append(f"From {current_name}, turn left and head north to reach {next_name}")
                        else:
                            directions.append(f"From {current_name}, head straight north to reach {next_name}")
                    else:
                        if dx > 20:  # Slightly east
                            directions.append(f"From {current_name}, turn right and head south to reach {next_name}")
                        elif dx < -20:  # Slightly west
                            directions.append(f"From {current_name}, turn left and head south to reach {next_name}")
                        else:
                            directions.append(f"From {current_name}, head straight south to reach {next_name}")

                # Add additional context for specific locations
                if next_name == "1 South Collaborative Study Area":
                    directions.append("Look for the large '1South' sign above the entrance")
                elif "Project Room" in next_name:
                    if "A" in next_name:
                        directions.append("Project Room A is located in the southeast corner of 1South")
                    else:
                        directions.append("Project Room B is located in the southwest corner of 1South")
                elif next_name == "To Café Bergson":
                    directions.append("Look for the staircase on your right leading up")
                elif next_name == "To Lower Level":
                    directions.append("Look for the staircase on your left leading down")
                elif "Information Commons" in next_name:
                    directions.append("Look for the large open area with computer workstations")
                elif "Circulation" in next_name:
                    directions.append("Look for the main service desk with self-checkout stations")

            return directions
        except nx.NetworkXNoPath:
            return ["No path found between these locations."]

    def highlight_room(self, room_id):
        """Reset all rooms to default color and highlight the specified room."""
        for node in self.floor_plan["nodes"].values():
            node["color"] = "lightgray"
            
        if room_id in self.floor_plan["nodes"]:
            self.floor_plan["nodes"][room_id]["color"] = "red"

    def process_natural_language_query(self, query: str) -> str:
        """
        Process a natural language navigation query.
        Example inputs:
        - "How do I get from 1South to Information Commons?"
        - "Where is the Information Commons from 1South?"
        - "I'm at circulation, how do I get to periodicals?"
        """
        query = query.lower().strip()
        start_location = None
        end_location = None
        
        # Common patterns for extracting locations
        from_patterns = ["from", "at", "in", "near"]
        to_patterns = ["to", "find", "reach", "get to"]
        
        # First try to find the destination (end location)
        parts = query.split()
        found_end = False
        for pattern in to_patterns:
            if pattern in query:
                idx = query.index(pattern)
                end_part = query[idx + len(pattern):].strip()
                # Look for the longest matching alias
                longest_match = ""
                for alias in self.room_aliases.keys():
                    if alias in end_part and len(alias) > len(longest_match):
                        longest_match = alias
                        end_location = self.room_aliases[alias]
                        found_end = True
                if found_end:
                    break
        
        # Try to find the starting location
        found_start = False
        for pattern in from_patterns:
            if pattern in query:
                idx = query.index(pattern)
                start_part = query[idx + len(pattern):].strip()
                # Look for the longest matching alias
                longest_match = ""
                for alias in self.room_aliases.keys():
                    if alias in start_part and len(alias) > len(longest_match):
                        longest_match = alias
                        start_location = self.room_aliases[alias]
                        found_start = True
                if found_start:
                    break
        
        # Debug output
        print(f"Parsed start location: {start_location}")
        print(f"Parsed end location: {end_location}")
        
        # If we found both locations, use them
        if start_location and end_location and start_location != end_location:
            return self.process_query(start_location, end_location)
        # If we only found destination, use normal processing
        elif end_location:
            return self.process_query("mainEntrance", end_location)
        else:
            return "I couldn't understand the locations in your query. Please specify where you want to go more clearly."


    def process_query(self, start_location, end_location):
        """
        Process a navigation query between any two locations and return formatted directions.
        
        Args:
            start_location (str): Starting location query
            end_location (str): Destination location query
            
        Returns:
            str: Formatted directions or error message
        """
        # Find matching rooms for both start and end locations
        start = self.find_closest_room_match(start_location)
        destination = self.find_closest_room_match(end_location)
        
        # Error handling for locations not found
        error_messages = []
        if not start:
            error_messages.append(f"Could not find starting location: '{start_location}'")
        if not destination:
            error_messages.append(f"Could not find destination: '{end_location}'")
        
        if error_messages:
            return "\n".join(error_messages) + "\nPlease rephrase or provide more details."
            
        if start == destination:
            return "You are already at your destination!"
        
        # Get directions between the two points
        directions = self.get_directions(start, destination)
        
        # Highlight destination and show path on map
        self.highlight_room(destination)
        path = nx.shortest_path(self.nx_graph, start, destination)
        self.visualize_map(highlight_path=path)
        
        # Format the directions nicely with step numbers
        numbered_directions = []
        for i, direction in enumerate(directions, 1):
            numbered_directions.append(f"{i}. {direction}")
        
        # Get the actual location names from the floor plan
        start_name = self.floor_plan['nodes'][start]['label']
        dest_name = self.floor_plan['nodes'][destination]['label']
        
        return "\n".join([
            f"Directions from {start_name} to {dest_name}:",
            "",  # Empty line for spacing
            "\n".join(numbered_directions)
        ])
    def get_navigation_options(self):
        """
        Returns a list of all available locations for navigation.
        
        Returns:
            list: List of dictionaries containing location IDs and labels
        """
        return [
            {"id": node_id, "name": node_info["label"]}
            for node_id, node_info in self.floor_plan["nodes"].items()
        ]

if __name__ == "__main__":
    receptionist = ReceptionistSystem()
    
    # Test queries for both navigation and lost user scenarios
    test_queries = [
        "How do I get to 1South?",
        "Where is the Information Commons?",
        "I need to find the Reference Collection",
        "How do I get to Project Room A?",
        "Where is the Circulation desk?",
        "I'm lost near some computers",
        "I see stairs but don't know where I am",
        "I'm in a quiet area with bookshelves"
    ]
    
    print("Testing Navigation Queries:")
    for query in test_queries[:5]:
        print(f"\nQuery: {query}")
        response = receptionist.process_query(query)
        print("Directions:")
        print(response)
    
    print("\nTesting Lost User Scenarios:")
    for query in test_queries[5:]:
        print(f"\nDescription: {query}")
        response = receptionist.handle_lost_user(query)
        print("System Response:")
        if response["needs_clarification"]:
            print("Possible locations:", [loc["name"] for loc in response["possible_locations"]])
            print("Clarifying questions:", response["clarifying_questions"])
        else:
            print("Identified location:", response["possible_locations"][0]["name"])
            print("Directions to main entrance:")
            print("\n".join(response["directions"]))