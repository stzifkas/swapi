"""Consumes "The Star Wars API" (swapi.tech)
   Usage:
   python main.py search 'search term': Implements a Person search using SWAPI
   python main.py search 'search term' --world: Expands a person search fetching homeworld info
   python main.py cache --visualize: Provides a visualization of cached searches
   python main.py cache --clean: Clears search history

   Classes:
       World: A class to represent a world in Star Wars Universe
       Person: A class to represent a person in Star Wars Universe
"""
import sys
from datetime import datetime
from requests.models import HTTPError
from utilities import apihandler, dbhandler, visualization

WORLD_FLAG = False

class World():
    """A class to represent a world in Star Wars universe

    Attributes:
    world_id (int): The corresponding Star Wars API id
    name (str): World's name
    population (str): World's population
    rotation_period (str): World's self-rotation period
    orbital_period (str): World's around its sun orbital period
    """
    def __init__(self, **kwargs):
        properties = kwargs['properties']
        self.world_id = int(kwargs['id'])
        self.name = properties['name']
        self.population = properties['population']
        self.rotation_period = properties['rotation_period']
        self.orbital_period = properties['orbital_period']
        dbhandler.commit_world(id=self.world_id,
                                name=self.name,
                                population=self.population,
                                rotation_period=self.rotation_period,
                                orbital_period=self.orbital_period)

    def __str__(self):
        """Returns a represantative string for a specific World instance

        Returns:
            str: user-friendly representation
        """
        day, year = self.compare_to_earth()
        string = f"Name: {self.name}\nPopulation: {self.population}\nOn {self.name},"\
            f" 1 year on earth is {year:.2f} years and 1 day {day:.2} days\n"
        return string

    def compare_to_earth(self):
        """Calculates planet's relative time reduction using earth as reference point

        Returns:
            float,float: day,year relatively to ours
        """
        try:
            day = float(self.rotation_period)/24
            year = float(self.orbital_period)/365
            return day, year
        except ValueError as e:
            return 0.0, 0.0


class Person():
    """A class to represent a person in Star Wars universe

    Attributes:
    person_id (int): The corresponding Star Wars API id
    name (str): Person's name
    height (str): Person's height
    mass (str): Person's mass
    birth_year (str): Person's birth year
    """
    def __init__(self, **kwargs):
        properties = kwargs['properties']
        self.person_id = int(kwargs['id'])
        self.name = properties['name']
        self.height = properties['height']
        self.mass = properties['mass']
        self.birth_year = properties['birth_year']
        if kwargs['cached']:
            if WORLD_FLAG:
                home_world_data = dbhandler.fetch_world(person_id=self.person_id)
                self.homeworld = World(properties=home_world_data['properties'],
                                        id=home_world_data['uid'])
        else:
            if WORLD_FLAG:
                home_world_data = apihandler.homeworld_from_url(url=properties['homeworld'])
                self.homeworld = World(properties=home_world_data['properties'],
                                        id=home_world_data['uid'])
                print(self.homeworld.world_id)
                dbhandler.commit_person(
                    id=self.person_id,
                    name=self.name,
                    height=self.height,
                    mass=self.mass,
                    birth_year=self.birth_year,
                    worldid=self.homeworld.world_id)
            else:
                dbhandler.commit_person(
                    id=self.person_id,
                    name=self.name,
                    height=self.height,
                    mass=self.mass,
                    birth_year=self.birth_year)

    def __str__(self):
        """Returns a represantative string for a specific World instance

        Returns:
            str: user-friendly representation
        """
        global WORLD_FLAG
        string = f"\nName: {self.name}\nHeight: {self.height}\nMass: {self.mass}\n"\
            f"Birth Year: {self.birth_year}\n"
        if WORLD_FLAG:
            string += f"\nHomeworld\n---------\n{self.homeworld}\n"
        return string


def main():
    """Main function which orchestrates API search procedure
    """
    global WORLD_FLAG
    if sys.argv[1] == "search":
        cached = False
        if '--world' in sys.argv:
            WORLD_FLAG = True
        # Check if search query is cached
        cache_person_ids, cache_time = dbhandler.is_cached(
            search_query=sys.argv[2],
            world_flag=WORLD_FLAG)
        # Grab cached data
        if cache_person_ids:
            cached = True
            results = dbhandler.fetch_person(person_ids=cache_person_ids)
            for result in results:
                person = Person(properties=result['properties'],
                                id=result['uid'],
                                cached=cached)
                print(person)
            print(f"Cached: {cache_time}")
        else:
            try:
                now = datetime.now()
                current_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
                results = apihandler.search_person(search_query=sys.argv[2])
                for result in results:
                    person = Person(
                        properties=result['properties'], id=result['uid'], cached=cached)
                    print(person)
                    dbhandler.commit_search(current_time=current_time,
                                            personid=person.person_id,
                                            search_query=sys.argv[2],
                                            world_flag=str(WORLD_FLAG))
            except HTTPError:
                print("The force is not strong within you")
    elif sys.argv[1] == "cache":
        if sys.argv[2] == "--clean":
            dbhandler.clean_tables()
            print("removed cache")
        elif sys.argv[2] == "--visualize":
            visualization.visualize()


if __name__ == "__main__":
    main()
