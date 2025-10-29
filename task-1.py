import uuid
from datetime import datetime
import csv

class Station:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.lines = []

    def __str__(self):
        return self.name

    def join_line(self, line):  # accepts a line object and adds this station to that line
        if line not in self.lines:
            self.lines.append(line)
            return self.lines
        else:
            return None

    def is_transfer_station(self):
        if len(self.lines) > 1:  # Station connected to more than one line
            return True
        return False

    def get_line_names(self):
        if self.lines != []:
            return [line.name for line in self.lines]
        else:
            return None


class Ticket:
    def __init__(self, origin, destination, price, route_info, misc):
        self.id = self._generate_id()
        self.origin = origin
        self.destination = destination
        self.price = price
        self.route_info = route_info
        self.misc = misc  # stores miscellaneous ticket data

    def _generate_id(self):
        return f"MET-TKT-{datetime.now().strftime("%Y%m%d-%H%M%S")}-{str(uuid.uuid4()[:16])}"

    def display(self):
        return f"""
Ticket: {self.id}
From: {self.origin} to {self.destination}
Cost: {self.price} rupees
===============================================
Route Instructions: 
{self.route_info}
===============================================
Miscellaneous Information: {self.misc}        
"""


class Line:
    def __init__(self, id, name, colour):
        self.id = id
        self.name = name
        self.colour = colour
        self.stations = []  # stores an ordered list of station objects

    def get_station_position(self, station_id):
        try:
            return self.stations.find(station_id)
        except ValueError:
            return None

    def stations_on_line(self, station_list):  # do these stations exist on this line
        for station in station_list:
            if not (station in self.stations):
                return False
        return True

    def calculate_distance(self, origin, destination):
        if self.stations_on_line([origin, destination]):
            try:
                origin_idx = self.stations.index(origin)
                destination_idx = self.stations.index(destination)
                return abs(destination_idx - origin_idx)
            except ValueError:  # stations not on line
                return None

        return None

    def add_station(self, station: Station):
        if station.id not in self.stations:
            self.stations.append(station.id)
            station.join_line(self)

    def __str__(self):
        return f"""
Line: {self.name}
Stations: {self.stations}
Colour: {self.colour}
"""

    # IMPLEMENT MAYBE => ADD STATIONS at a particular position in the line


# TODO
# [] Create load_csv data function
# [] Implement shortest route between origin and dest
# [] Detect line changes and stations involved and create 'route_info'
# [] Create a ticket purchase system
# [] Cost: base_cost + 10 * number of stations crossed

class MetroSystem:
    def __init__(self):
        self.stations = {}
        self.lines = {}
        self.tickets = {}
    
    def load_data(self, station_file_path, lines_file_path):
        self._load_stations(station_file_path)
        self._load_lines(lines_file_path)
    
    def _load_stations(self, filepath):
        with open(filepath, 'r', newline='') as station_csv:
            reader = csv.reader(station_csv, delimiter=';')
            next(reader)
            for line in reader:
                station_id = line[0]
                station_lines = line[2].split(',')
                station = Station(station_id, line[1])
                self.stations[station_id] = station
                for sline in station_lines:
                    station.join_line(sline)
            
        print(self.stations)

    def _load_lines(self, filepath):
        with open(filepath, 'r', newline='') as lines_csv:
            reader = csv.reader(lines_csv, delimiter=';')
            next(reader)
            for l in reader:
                line_id = l[0]
                line_name = l[1]
                line_colour = l[2]
                stations_in_order = l[3].split(',')

                line = Line(line_id, line_name, line_colour)
                for station in stations_in_order:
                    line.add_station(self.stations[station])

                self.lines[line_id] = line

            print(self.lines['L1'])


metro = MetroSystem()
metro.load_data('./data/stations.csv', './data/lines.csv')
 