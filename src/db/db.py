import sqlite3
import os.path
from dotenv import find_dotenv, load_dotenv, get_key

# Create db file path
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
db_filename = get_key(dotenv_path, "DB_FILE")
db_file = os.path.join(os.path.dirname(__file__), db_filename)
db_init_sql = os.path.join(os.path.dirname(__file__), "template.sql")

#TODO: Figure out a better way to do this

get_players =          """ SELECT nickname, account_id
                                FROM Player 
                                ORDER BY (Player.nickname) """

add_player =            """ INSERT INTO Player(nickname, account_id, country, extra)
                            VALUES(?,?,?,?) """

remove_player =         """ DELETE FROM Player
                            WHERE nickname=? COLLATE NOCASE"""

list_players =          """ SELECT nickname, country
                            FROM Player 
                            ORDER BY (Player.id) """

update_player_name= """ UPDATE Player
                            SET nickname=?
                            WHERE nickname=? COLLATE NOCASE"""

update_player_account_id= """ UPDATE Player
                            SET account_id=?
                            WHERE nickname=? COLLATE NOCASE"""

update_player_country = """ UPDATE Player
                            SET country=?
                            WHERE nickname=? COLLATE NOCASE"""

update_player_extra =           """ UPDATE Player
                                    SET extra=?
                                    WHERE nickname=? COLLATE NOCASE"""

get_player_info =           """ SELECT nickname, account_id, country
                                FROM Player
                                WHERE nickname=? COLLATE NOCASE
                            """                  

get_player_id =         """ SELECT id
                            FROM Player
                            WHERE nickname=? COLLATE NOCASE"""

get_player_id_by_account_id = """ SELECT id
                            FROM Player
                            WHERE account_id=? """

get_map_uid =            """ SELECT uid
                            FROM Map
                            WHERE name=? COLLATE NOCASE"""

add_twitch_channel =    """ INSERT INTO TwitchChannel(name)
                            VALUES(?)
                        """

remove_twitch_channel = """ DELETE FROM TwitchChannel
                            WHERE name=? COLLATE NOCASE"""

get_twitch_list =       """ SELECT name
                            FROM TwitchChannel
                        """

def open_conn():
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

# Creates the initial database structure
def init():

    try:
        f = open(db_file, "x")
        print("db file created")
    except FileExistsError:
        print("db file already exists, no new file created")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    init_query = open(db_init_sql, "r").read()
    cursor.executescript(init_query)

    cursor.close()
    conn.close()

def run_script(script):

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.executescript(script)

    cursor.close()
    conn.close()


# Executes all queries provided, queries is a list of (sql, params)
#   Single param has to be in the form [a]
#   Multiple params has to be in the form (a,b,c) (for 3 parameters a, b and c) 
def execute_queries(conn, queries):

    cursor = conn.cursor()

    for (sql, param) in queries:
            
        try:
            # Check if there are parameters
            if param == None:
                print("none param")
                cursor.execute(sql)
            else:
                cursor.execute(sql, param)
        except sqlite3.IntegrityError as e:
            raise Exception(e)
        except sqlite3.Error as e:
            print(e, end="")
            print(" : ", end="")
            print(param)

    conn.commit()
    cursor.close()

def retrieve_data(conn, query):

    cursor = conn.cursor()
    (sql, param) = query

    try:
        # Check if there are parameters
        if param == None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, param)
    except sqlite3.Error as e:
        print(e, end="")
        print(" : ", end="")
        print(param)

    conn.commit()

    res = cursor.fetchall()
    cursor.close()

    return res







