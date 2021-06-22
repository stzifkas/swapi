import sys
import requests
from requests.models import HTTPError 
from utilities import config,helpers,dbhandler

base_url = config.base_url
world_flag = False

class World(object):
    def __init__(self, kwargs):
        properties = kwargs['properties']
        self.id = int(kwargs['uid'])
        self.name = properties['name']
        self.population = properties['population']
        self.rotation_period = properties['rotation_period']
        self.orbital_period = properties['orbital_period']
        dbhandler.commit_world(id=self.id, name=self.name, population=self.population, rotation_period=self.rotation_period, orbital_period = self.orbital_period)

    
    def __str__(self):
        day,year = self.compare_to_earth()
        s = f"Name: {self.name}\nPopulation: {self.population}\nOn {self.name}, 1 year on earth is {year:.2f} years and 1 day {day:.2} days\n"
        return s

    def compare_to_earth(self):
        day = float(self.rotation_period)/24
        year = float(self.orbital_period)/365
        return day,year

class Person(object):
    def __init__(self, **kwargs):
        properties = kwargs['properties']
        self.id = int(kwargs['id'])
        self.name = properties['name']
        self.height = properties['height']
        self.mass = properties['mass']
        self.birth_year = properties['birth_year']
        if kwargs['cached']:
            if world_flag:
                parameters = {}
                cached_world = dbhandler.fetch_world(person_id = self.id)
                parameters['properties'] = { 'name': cached_world[0],
                                            'population': cached_world[1],
                                            'rotation_period': cached_world[3],
                                            'orbital_period': cached_world[4]
                }
                parameters['uid'] = cached_world[2]
                self.homeworld = World(parameters)
        else:
            if world_flag:
                self.homeworld = self.get_homeworld(url=properties['homeworld'])
                dbhandler.commit_person(
                    id=self.id, 
                    name=self.name, 
                    height=self.height, 
                    mass=self.mass, 
                    birth_year=self.birth_year,
                    worldid = self.homeworld.id)
            else:
                dbhandler.commit_person(
                    id=self.id, 
                    name=self.name, 
                    height=self.height, 
                    mass=self.mass, 
                    birth_year=self.birth_year)

    def get_homeworld(self,**kwargs):
        x = requests.get(kwargs['url'])
        if not x.json()['result']:
            raise HTTPError
        result = x.json()['result']
        homeworld = World(result)
        return homeworld

    def __str__(self):
        global world_flag
        s = f"\nName: {self.name}\nHeight: {self.height}\nMass: {self.mass}\nBirth Year: {self.birth_year}\n"
        if world_flag:
            s += f"\nHomeworld\n---------\n{self.homeworld}\n"          
        return s

def main():
    global world_flag
    if sys.argv[1] == "search":
        cached = False
        if '--world' in sys.argv:
            world_flag = True
        cache_person_ids,cache_time = dbhandler.is_cached(search_query=sys.argv[2],world_flag=world_flag)
        if cache_person_ids:
            cached = True
            results = dbhandler.fetch_person(person_ids = cache_person_ids)
            for result in results:
                person = Person(properties = result['properties'], id = result['uid'], cached=cached)
                print(person)
            print(f"Cached: {cache_time}")
        else:
            try:
                results = helpers.search_person(search_query=sys.argv[2])
                for result in results:
                    person = Person(properties = result['properties'], id = result['uid'], cached=cached)
                    print(person)
                    dbhandler.commit_search(personid = person.id, search_query=sys.argv[2],world_flag=str(world_flag))
            except HTTPError:
                print("The force is not strong within you")
    elif sys.argv[1] == "cache" and sys.argv[2] == "--clean":
        dbhandler.clean_tables()
        print("removed cache")
if __name__ == "__main__":
    main()
