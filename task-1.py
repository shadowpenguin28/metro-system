import uuid
from datetime import datetime

class Station:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.lines = []
    
    def __str__(self):
        return self.name
    
    def add_line(self, line): # accepts a line object and adds this station to that line
        if line not in self.lines:
            self.lines.append(line)
            print(f"Successfully added {self.name} to line: {line}")
        else:
            print(f"{self.name} is already part of line: {line}.")
    
    def is_transfer_station(self):
        if len(self.lines) > 1: # Station connected to more than one line
            return True
        return False

    def get_line_names(self):
        if self.lines != []:
            return [line.name for line in self.lines]
        else:
            return None
        
class Ticket:
    def __init__(self, id, origin, destination, price, misc):
        self.id = self._generate_id
        self.origin = origin
        self.destination = destination
        self.price = price
        self.misc = misc # stores miscellaneous ticket data
    
    def _generate_id(self):
        return f"MET-TKT-{datetime.now().strftime("%Y%m%d-%H%M%S")}-{uuid.uuid4()[:16]}"

    def display(self):
        return ""


class Line:
    def __init__(self, id, name, colour):
        self.id = id
        self.name = name
        self.colour = colour
        self.stations = [] # stores an ordered list of station objects
    
    def get_station_position(self, station_id):
        if station_id in self.stations:
            return self.stations.find(station_id)
        else:
            return None # Station doesn't exist in line
    
    def calculate_distance(self, origin, destination):
        if origin in self.stations and destination in self.stations:
            return abs(self.stations.find(origin) - self.stations.find(destination))
        else:
            return None

    # IMPLEMENT MAYBE => ADD STATIONS SEPARATELY AT A SPECIFIC SPOT
    # def add_station(self, station_id, station_position):
    #     pass

