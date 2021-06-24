"""A collection of useful SQL handling methods for data caching functionality
"""

import sqlite3
from utilities.config import DATABASE_FILE

def commit_world(**kwargs):
    """Caches a World on worlds table

    Arguments
    kwargs:
        id (int) : Worlds ID
        name (str): World's name
        population (str): World's population
        rotation_period (str): World's rotation period
        orbital_period (str): World's orbital period
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        sql = f"SELECT * FROM worlds WHERE worldid = {kwargs['id']}"
        response = cur.execute(sql)
        results = response.fetchall()
        if not results:
            sql = "INSERT INTO worlds(worldid,name,population,"\
                "rotation_period,orbital_period) VALUES(?,?,?,?,?)"
            row = ( kwargs['id'],
                    kwargs['name'],
                    kwargs['population'],
                    kwargs['rotation_period'],
                    kwargs['orbital_period'])
            cur.execute(sql,row)
            conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
    finally:
        if conn:
           conn.close()

def commit_person(**kwargs):
    """Caches a person on persons table

    Arguments
    kwargs:
        id (int) : Person's ID
        name (str): Person's name
        height (str): Person's height
        mass (str): Person's mass
        birth_year (str): Person's birth year
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        sql = f"SELECT * FROM persons WHERE personid = {kwargs['id']}"
        response = cur.execute(sql)
        results = response.fetchall()
        if not results:
            sql = "INSERT INTO persons(personid,name,height,mass,birth_year)"\
                "VALUES(?,?,?,?,?)"
            row = ( kwargs['id'],
                    kwargs['name'],
                    kwargs['height'],
                    kwargs['mass'],
                    kwargs['birth_year'])
            cur.execute(sql,row)
            conn.commit()
        if 'worldid' in kwargs.keys():
            sql = f"UPDATE persons SET worldid = {kwargs['worldid']}"\
                f" WHERE personid = {kwargs['id']}"
            cur.execute(sql)
            conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
    finally:
        conn.close()

def commit_search(**kwargs):
    """Caches a search query on searches table

    Arguments
    kwargs:
        time (str) : Time of the search
        personid (int): Single person id which came as a result
        query (str): Search query
        has_world (str): If home world info was demanded
    """
    try:
        current_time = kwargs['current_time']
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        sql = "INSERT INTO searches(time,personid,query,has_world)"\
            " VALUES(?,?,?,?)"
        row = (str(current_time),
            int(kwargs['personid']),
            str(kwargs['search_query']),
            str(kwargs['world_flag']))
        cur.execute(sql,row)
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def is_cached(**kwargs):
    """Checks if a search query is already cached

    Arguments
    kwargs:
        query: Search query
        has_world: If homeworld info is demanded

    Returns
    [int],str: List of search results' person ids , cached search time
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        sql = f"SELECT personid,time FROM searches WHERE "\
            f"query = '{kwargs['search_query']}' AND"\
            f" has_world = '{str(kwargs['world_flag'])}'"
        response = cur.execute(sql)
        results = response.fetchall()
        conn.close()
        if results:
            person_ids = [result[0] for result in results]
            time = results[0][1]
            return person_ids, time
        return None,None
    except sqlite3.Error as e:
        if conn:
            conn.close()

def name_from_id(personid):
    """Returns a name for a requested person

    Args:
        personid (int): Requested person's id

    Returns:
        str: Person's name
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        sql = f"SELECT name FROM persons WHERE personid = {personid}"
        response = cur.execute(sql)
        row = response.fetchone()
        result = row[0]
        conn.close()
        return result
    except sqlite3.Error as e:
        if conn:
            conn.close()

def fetch_person(**kwargs):
    """Returns a list of persons for requested ids

    Arguments:
    kwargs:
        person_ids: list of person_ids
    Returns:
        list of dicts: A list of dicts containing requested persons' attributes
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        results = []
        for person_id in kwargs['person_ids']:
            result = {}
            result['properties'] = {}
            sql = "SELECT name, height, mass, birth_year FROM persons"\
            f" WHERE personid = '{person_id}'"
            response=cur.execute(sql)
            row = response.fetchone()
            result['properties']['name'] = row[0]
            result['properties']['height'] = row[1]
            result['properties']['mass'] = row[2]
            result['properties']['birth_year'] = row[3]
            result['uid'] = person_id
            results.append(result)
        conn.close()
        return results
    except sqlite3.Error as e:
        if conn:
            conn.close()

def fetch_world(**kwargs):
    """Returns homeworld for a requested person

    Arguments:
        kwargs:
            person_id (int): person_id which corresponds to requested homeworld
    Returns:
        dict: A dictionary of homeworld properties
    """
    try:
        results = {}
        conn = sqlite3.connect(DATABASE_FILE)
        person_id = kwargs['person_id']
        cur = conn.cursor()
        sql = f"SELECT worlds.name, worlds.population, worlds.worldid,"\
            f" worlds.rotation_period, worlds.orbital_period "\
            f"FROM worlds JOIN persons ON worlds.worldid = persons.worldid"\
            f" WHERE persons.personid = {person_id}"
        response = cur.execute(sql)
        row = response.fetchone()
        conn.close()
        results['properties'] = { 'name': row[0],
                                    'population': row[1],
                                    'rotation_period': row[3],
                                    'orbital_period': row[4]
        }
        results['uid'] = row[2]
        return results
    except sqlite3.Error as e:
        if conn:
            conn.close()

def fetch_searches():
    """Returns all cached search queries

    Returns:
        [(str,str,str,str)]: List of search queries
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        sql = "SELECT time,personid,query,has_world FROM searches"
        response = cur.execute(sql)
        results = response.fetchall()
        conn.close()
        return results
    except sqlite3.Error as e:
        if conn:
            conn.close()

def clean_tables():
    """Deletes all records for each db table
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        sql = "DELETE FROM persons"
        cur.execute(sql)
        conn.commit()
        sql = "DELETE FROM worlds"
        cur.execute(sql)
        conn.commit()
        sql = "DELETE FROM searches"
        cur.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
