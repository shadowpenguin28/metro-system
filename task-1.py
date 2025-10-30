import uuid
from datetime import datetime
import csv
from collections import deque

class Station:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.lines = []

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"Station({self.id}, {self.name})"

    def join_line(self, line):
        """Accept a line object and add this station to that line"""
        if line not in self.lines:
            self.lines.append(line)
            return self.lines
        else:
            return None

    def is_transfer_station(self):
        """Check if station is connected to more than one line"""
        return len(self.lines) > 1

    def get_line_names(self):
        """Get list of line names serving this station"""
        if self.lines:
            return [line.name for line in self.lines]
        else:
            return []


class Ticket:
    def __init__(self, origin, destination, price, route_info, misc=""):
        self.id = self._generate_id()
        self.origin = origin
        self.destination = destination
        self.price = price
        self.route_info = route_info
        self.timestamp = datetime.now()
        self.misc = misc

    def _generate_id(self):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"MET-TKT-{timestamp}-{unique_id}"

    def display(self):
        """Display formatted ticket information"""
        print(f"\n{'='*60}")
        print(f"{'METRO TICKET':^60}")
        print(f"{'='*60}")
        print(f"Ticket ID     : {self.id}")
        print(f"From          : {self.origin.name} (ID: {self.origin.id})")
        print(f"To            : {self.destination.name} (ID: {self.destination.id})")
        print(f"Price         : ₹{self.price}")
        print(f"Purchase Time : {self.timestamp.strftime('%d %B %Y, %H:%M:%S')}")
        print(f"\n{'Route Instructions:':^60}")
        print(f"{'-'*60}")
        for i, instruction in enumerate(self.route_info, 1):
            print(f"  {i}. {instruction}")
        if self.misc:
            print(f"\nAdditional Info: {self.misc}")
        print(f"{'='*60}\n")
    
    def __str__(self):
        return f"Ticket {self.id}: {self.origin.name} → {self.destination.name} (₹{self.price})"


class Line:
    def __init__(self, id, name, colour):
        self.id = id
        self.name = name
        self.colour = colour
        self.stations = []  # Ordered list of Station objects

    def get_station_position(self, station):
        """Get the index position of a station on this line"""
        try:
            return self.stations.index(station)
        except ValueError:
            return None

    def stations_on_line(self, station_list):
        """Check if all stations in list exist on this line"""
        for station in station_list:
            if station not in self.stations:
                return False
        return True

    def calculate_distance(self, origin, destination):
        """Calculate number of stations between origin and destination"""
        if self.stations_on_line([origin, destination]):
            try:
                origin_idx = self.stations.index(origin)
                destination_idx = self.stations.index(destination)
                return abs(destination_idx - origin_idx)
            except ValueError:
                return None
        return None

    def add_station(self, station):
        """Add a station to this line (creates bidirectional relationship)"""
        if station not in self.stations:
            self.stations.append(station)
            station.join_line(self)

    def __str__(self):
        station_names = [s.name for s in self.stations]
        return f"Line: {self.name} ({self.colour}) - {len(self.stations)} stations"
    
    def __repr__(self):
        return f"Line({self.id}, {self.name})"


class MetroSystem:
    def __init__(self):
        self.stations = {}  # {station_id: Station object}
        self.lines = {}     # {line_id: Line object}
        self.tickets = []   # List of Ticket objects
        self.graph = {}     # Adjacency list for pathfinding
        
        # Pricing configuration
        self.BASE_FARE = 10
        self.FARE_PER_STATION = 5
    
    # ============================================
    # DATA LOADING
    # ============================================
    
    def load_data(self, station_file_path, lines_file_path, tickets_file_path=None):
        """Load all data from CSV files"""
        self._load_stations(station_file_path)
        self._load_lines(lines_file_path)
        self._build_graph()
        if tickets_file_path:
            self._load_tickets(tickets_file_path)
        print("✅ Metro system data loaded successfully!\n")
    
    def _load_stations(self, filepath):
        """Load stations from CSV file"""
        with open(filepath, 'r', newline='') as station_csv:
            reader = csv.reader(station_csv, delimiter=';')
            next(reader)  # Skip header
            for line in reader:
                station_id = line[0].strip()
                station_name = line[1].strip()
                station = Station(station_id, station_name)
                self.stations[station_id] = station

    def _load_lines(self, filepath):
        """Load lines from CSV and connect stations"""
        with open(filepath, 'r', newline='') as lines_csv:
            reader = csv.reader(lines_csv, delimiter=';')
            next(reader)  # Skip header
            for l in reader:
                line_id = l[0].strip()
                line_name = l[1].strip()
                line_colour = l[2].strip()
                stations_in_order = [s.strip() for s in l[3].split(',')]

                line = Line(line_id, line_name, line_colour)
                
                # Add stations in order
                for station_id in stations_in_order:
                    if station_id in self.stations:
                        line.add_station(self.stations[station_id])

                self.lines[line_id] = line
    
    def _build_graph(self):
        """Build adjacency list representation for pathfinding"""
        # Initialize graph
        for station_id in self.stations:
            self.graph[station_id] = []
        
        # Add edges based on line connections
        for line in self.lines.values():
            for i in range(len(line.stations) - 1):
                station1 = line.stations[i]
                station2 = line.stations[i + 1]
                
                # Add bidirectional edges
                self.graph[station1.id].append({
                    'station': station2,
                    'line': line
                })
                self.graph[station2.id].append({
                    'station': station1,
                    'line': line
                })
    
    def _load_tickets(self, filepath):
        """Load existing tickets from CSV"""
        try:
            with open(filepath, 'r', newline='') as tickets_csv:
                reader = csv.reader(tickets_csv, delimiter=";")
                next(reader)  # Skip header
                for l in reader:
                    if len(l) >= 5:
                        ticket_id, origin_id, dest_id, price, route_info = l[:5]
                        misc = l[5] if len(l) > 5 else ""
                        
                        # Reconstruct ticket (simplified version)
                        origin = self.stations.get(origin_id.strip())
                        destination = self.stations.get(dest_id.strip())
                        
                        if origin and destination:
                            instructions = route_info.split('|')
                            ticket = Ticket(origin, destination, float(price), instructions, misc)
                            ticket.id = ticket_id  # Use stored ID
                            self.tickets.append(ticket)
        except FileNotFoundError:
            print("No existing tickets file found. Starting fresh.")
    
    # ============================================
    # TICKET PURCHASING
    # ============================================
    
    def purchase_ticket(self, origin_id, destination_id):
        """
        Purchase a ticket from origin to destination
        Returns: (Ticket object, success message) or (None, error message)
        """
        # Validate station IDs
        origin = self.stations.get(origin_id)
        destination = self.stations.get(destination_id)
        
        if not origin:
            return None, f"Error: Station ID '{origin_id}' not found"
        if not destination:
            return None, f"Error: Station ID '{destination_id}' not found"
        if origin.id == destination.id:
            return None, "Error: Origin and destination are the same"
        
        # Find shortest path
        path, distance = self._find_shortest_path(origin, destination)
        
        if not path:
            return None, "Error: No route found between stations"
        
        # Generate route instructions
        instructions = self._generate_route_instructions(path)
        
        # Calculate price
        price = self._calculate_price(distance)
        
        # Create ticket
        ticket = Ticket(origin, destination, price, instructions)
        
        # Store ticket
        self.tickets.append(ticket)
        self._save_ticket_to_csv(ticket)
        
        return ticket, "Ticket purchased successfully!"
    
    # ============================================
    # PATHFINDING
    # ============================================
    
    def _find_shortest_path(self, origin, destination):
        """
        Find shortest path using BFS
        Returns: (list of Station objects, distance) or (None, 0)
        """
        queue = deque([(origin, [origin], 0)])  # (current_station, path, distance)
        visited = {origin.id}
        
        while queue:
            current, path, distance = queue.popleft()
            
            # Found destination
            if current.id == destination.id:
                return path, distance
            
            # Explore neighbors
            for neighbor_info in self.graph[current.id]:
                neighbor = neighbor_info['station']
                
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path, distance + 1))
        
        return None, 0  # No path found
    
    def _generate_route_instructions(self, path):
        """
        Generate human-readable route instructions from path
        Returns: List of instruction strings
        """
        if len(path) < 2:
            return ["You are already at the destination"]
        
        instructions = []
        current_line = None
        segment_start_idx = 0
        
        for i in range(len(path) - 1):
            station1 = path[i]
            station2 = path[i + 1]
            
            # Find connecting line
            connecting_line = self._find_connecting_line(station1, station2)
            
            if connecting_line != current_line:
                # Save previous segment
                if current_line is not None:
                    stops = i - segment_start_idx
                    instructions.append(
                        f"Travel {stops} stop(s) on {current_line.name} to {station1.name}"
                    )
                
                # Start new segment
                if current_line is None:
                    instructions.append(f"Board {connecting_line.name} at {station1.name}")
                else:
                    instructions.append(f"Transfer to {connecting_line.name} at {station1.name}")
                
                current_line = connecting_line
                segment_start_idx = i
        
        # Add final segment
        final_stops = len(path) - 1 - segment_start_idx
        instructions.append(
            f"Travel {final_stops} stop(s) on {current_line.name} to {path[-1].name}"
        )
        
        return instructions
    
    def _find_connecting_line(self, station1, station2):
        """Find which line connects two adjacent stations"""
        common_lines = set(station1.lines) & set(station2.lines)
        return list(common_lines)[0] if common_lines else None
    
    def _calculate_price(self, distance):
        """Calculate ticket price based on distance"""
        return self.BASE_FARE + (distance * self.FARE_PER_STATION)
    
    # ============================================
    # TICKET MANAGEMENT
    # ============================================
    
    def _save_ticket_to_csv(self, ticket, filepath='./data/tickets.csv'):
        """Save ticket to CSV file"""
        try:
            # Check if file exists
            try:
                with open(filepath, 'r') as f:
                    file_exists = True
            except FileNotFoundError:
                file_exists = False
            
            with open(filepath, 'a', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                
                # Write header if new file
                if not file_exists:
                    writer.writerow(['ticket_id', 'origin_id', 'destination_id', 'price', 'route_info', 'misc'])
                
                # Write ticket data
                route_str = '|'.join(ticket.route_info)
                writer.writerow([
                    ticket.id,
                    ticket.origin.id,
                    ticket.destination.id,
                    ticket.price,
                    route_str,
                    ticket.misc
                ])
        except Exception as e:
            print(f"Error saving ticket: {e}")
    
    def view_all_tickets(self):
        """Display all purchased tickets"""
        if not self.tickets:
            print("\n❌ No tickets have been purchased yet.\n")
            return
        
        print(f"\n{'='*60}")
        print(f"ALL PURCHASED TICKETS ({len(self.tickets)} total)")
        print(f"{'='*60}\n")
        
        for i, ticket in enumerate(self.tickets, 1):
            print(f"\n--- Ticket {i} ---")
            print(ticket)
    
    def view_ticket_details(self, index):
        """Display detailed view of a specific ticket"""
        if 0 <= index < len(self.tickets):
            self.tickets[index].display()
        else:
            print("Invalid ticket number")
    
    # ============================================
    # DISPLAY METHODS
    # ============================================
    
    def display_all_stations(self):
        """Display all stations grouped by line"""
        print(f"\n{'='*60}")
        print(f"{'METRO STATIONS':^60}")
        print(f"{'='*60}\n")
        
        for line in self.lines.values():
            print(f"{line.name} ({line.colour}):")
            for station in line.stations:
                transfer = " [TRANSFER]" if station.is_transfer_station() else ""
                lines_str = ", ".join(station.get_line_names())
                print(f"  {station.id:4s} - {station.name:30s} (Lines: {lines_str}){transfer}")
            print()
    
    def display_all_lines(self):
        """Display all metro lines"""
        print(f"\n{'='*60}")
        print(f"{'METRO LINES':^60}")
        print(f"{'='*60}\n")
        
        for line in self.lines.values():
            print(f"{line.id}: {line}")
        print()


# ============================================
# MAIN PROGRAM
# ============================================

def main():
    # Initialize metro system
    metro = MetroSystem()
    
    try:
        metro.load_data('./data/stations.csv', './data/lines.csv', './data/tickets.csv')
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        print("Please ensure CSV files exist in ./data/ directory")
        return
    
    # Main menu loop
    while True:
        print("\n" + "="*60)
        print(f"{'METRO TICKET PURCHASING SYSTEM':^60}")
        print("="*60)
        print("1. View All Stations")
        print("2. View All Lines")
        print("3. Purchase Ticket")
        print("4. View All My Tickets")
        print("5. View Ticket Details")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            metro.display_all_stations()
        
        elif choice == '2':
            metro.display_all_lines()
        
        elif choice == '3':
            print("\n" + "-"*60)
            print("PURCHASE TICKET")
            print("-"*60)
            
            origin_id = input("Enter origin station ID: ").strip()
            dest_id = input("Enter destination station ID: ").strip()
            
            ticket, message = metro.purchase_ticket(origin_id, dest_id)
            
            if ticket:
                print(f"\n✓ {message}")
                ticket.display()
            else:
                print(f"\n✗ {message}")
        
        elif choice == '4':
            metro.view_all_tickets()
        
        elif choice == '5':
            if metro.tickets:
                try:
                    ticket_num = int(input(f"Enter ticket number (1-{len(metro.tickets)}): ")) - 1
                    metro.view_ticket_details(ticket_num)
                except ValueError:
                    print("Invalid input. Please enter a number.")
            else:
                print("\n❌ No tickets available.")
        
        elif choice == '6':
            print("\n" + "="*60)
            print("Thank you for using Metro Ticket System!")
            print("="*60 + "\n")
            break
        
        else:
            print("\n✗ Invalid choice. Please enter a number between 1-6.")


if __name__ == "__main__":
    main()