import sqlite3
from datetime import datetime

def commit_world(**kwargs):
    database_file = r'utilities/starwars.db'
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql = f'''SELECT * FROM worlds WHERE worldid = {kwargs['id']}'''
    r = cur.execute(sql)
    results = r.fetchall()
    if not results:
        sql = '''INSERT INTO worlds(worldid,name,population,rotation_period,orbital_period) VALUES(?,?,?,?,?)'''
        row = (kwargs['id'],kwargs['name'],kwargs['population'],kwargs['rotation_period'],kwargs['orbital_period'])
        cur.execute(sql,row)
        conn.commit()
    conn.close()

def commit_person(**kwargs):
    database_file = r'utilities/starwars.db'
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql = f'''SELECT * FROM persons WHERE personid = {kwargs['id']}'''
    r = cur.execute(sql)
    results = r.fetchall()
    if not results:
        sql = '''INSERT INTO persons(personid,name,height,mass,birth_year) VALUES(?,?,?,?,?)'''
        row = (kwargs['id'],kwargs['name'],kwargs['height'],kwargs['mass'],kwargs['birth_year'])
        cur.execute(sql,row)
        conn.commit()
    elif 'worldid' in kwargs.keys():
        sql = f"""UPDATE persons SET worldid = {kwargs['worldid']} WHERE personid = {kwargs['id']}"""
        cur.execute(sql)
        conn.commit()
    conn.close()

def commit_search(**kwargs):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S.%f")
    database_file = r'utilities/starwars.db'
    conn = sqlite3.connect(database_file)
    sql = '''INSERT INTO searches(time,personid,query,has_world) VALUES(?,?,?,?)'''
    cur = conn.cursor()
    row = (str(current_time),int(kwargs['personid']),str(kwargs['search_query']),str(kwargs['world_flag']))
    cur.execute(sql,row)
    conn.commit()

def is_cached(**kwargs):
    database_file = r'utilities/starwars.db'
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    sql = f"""SELECT personid,time FROM searches WHERE query = '{kwargs['search_query']}' AND has_world = '{str(kwargs['world_flag'])}'"""
    r = cur.execute(sql)
    results = r.fetchall()
    if results:
        person_ids = [result[0] for result in results]
        time = results[0][1]
        conn.close()
        return person_ids, time
    else:
        return None,None

def fetch_person(**kwargs):
    database_file = r'utilities/starwars.db'
    conn = sqlite3.connect(database_file)
    cur = conn.cursor()
    results = []
    for id in kwargs['person_ids']:
        result = {}
        result['properties'] = {}
        sql = f'''SELECT name, height, mass, birth_year FROM persons WHERE personid = {id}'''
        r = cur.execute(sql)
        row = r.fetchone()
        result['properties']['name'] = row[0]
        result['properties']['height'] = row[1]
        result['properties']['mass'] = row[2]
        result['properties']['birth_year'] = row[3]
        result['uid'] = id
        results.append(result)
    return results

def fetch_world(**kwargs):
    database_file = r'utilities/starwars.db'
    conn = sqlite3.connect(database_file)
    person_id = kwargs['person_id']
    cur = conn.cursor()
    sql = f"""SELECT worlds.name, worlds.population, worlds.worldid, worlds.rotation_period, worlds.orbital_period FROM worlds JOIN persons ON worlds.worldid = persons.worldid WHERE persons.personid = {person_id}"""
    r = cur.execute(sql)
    row = r.fetchone()
    conn.close()
    return row

def clean_tables():
    database_file = r'utilities/starwars.db'
    conn = sqlite3.connect(database_file)
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
    conn.close()
