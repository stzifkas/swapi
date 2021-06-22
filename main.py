import sys
import requests
from csv import DictReader, DictWriter

from requests.models import HTTPError 

world_flag = False
base_url = "https://www.swapi.tech/api"

class World(object):
    def __init__(self, kwargs):
        self.name = kwargs['name']
        self.population = kwargs['population']
        self.rotation_period = kwargs['rotation_period']
        self.orbital_period = kwargs['orbital_period']
    
    def __str__(self):
        day,year = self.compare_to_earth()
        s = f"Name: {self.name}\nPopulation: {self.population}\nOn {self.name}, 1 year on earth is {year:.2f} years and 1 day {day:.2} days\n"
        return s
        
    def compare_to_earth(self):
        day = float(self.rotation_period)/24
        year = float(self.orbital_period)/365
        return day,year

class Person(object):
    def __init__(self, kwargs):
        self.name = kwargs['name']
        self.height = kwargs['height']
        self.mass = kwargs['mass']
        self.birth_year = kwargs['birth_year']
        self.homeworld = self.get_homeworld(url=kwargs['homeworld'])

    
    def get_homeworld(self,**kwargs):
        x = requests.get(kwargs['url'])
        if not x.json()['result']:
            raise HTTPError
        result = x.json()['result']
        homeworld = World(result['properties'])
        return homeworld

    def __str__(self):
        global world_flag
        s = f"\nName: {self.name}\nHeight: {self.height}\nMass: {self.mass}\nBirth Year: {self.birth_year}\n"
        if world_flag:
            s += f"\nHomeworld\n---------\n{self.homeworld}\n"          
        return s


def search_person(**kwargs):
    persons = []
    x = requests.get(
        "/".join([base_url, f"people/?name={kwargs['search_query']}"]))
    if not x.json()['result']:
        raise HTTPError
    for result in x.json()['result']:
        persons.append(Person(result['properties']))
    return persons


def main():
    global world_flag
    if sys.argv[1] == "search":
        if '--world' in sys.argv:
            world_flag = True
        try:
            results = search_person(search_query=sys.argv[2])
            for result in results:
                print(result)
        except HTTPError:
            print("The force is not strong within you")
        except Exception as e:
            #TODO Print Help Message
            print(e)

if __name__ == "__main__":
    main()
