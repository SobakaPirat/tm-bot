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

get_test_players =          """ SELECT nickname, account_id
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

get_map_id =            """ SELECT id
                            FROM Map
                            WHERE name=? COLLATE NOCASE"""

get_map_uid =            """ SELECT uid
                            FROM Map
                            WHERE name=? COLLATE NOCASE"""

get_map_db_id_by_map_id = """ SELECT id
                            FROM Map
                            WHERE uid=? """

add_participant =       """ INSERT INTO Participant(player_id, roster_id)
                            VALUES(?,?) """

remove_participant =    """ DELETE FROM Participant
                            WHERE player_id=? AND roster_id=? """

add_time =              """ INSERT INTO Time(player_id, map_id, time)
                            VALUES(?,?,?) 
                                ON CONFLICT (player_id, map_id) DO
                                UPDATE SET time=excluded.time"""

get_n_map_times =       """ SELECT Player.nickname, Time.time  
                            FROM Map
                            JOIN Time ON Time.map_id = Map.id
                            JOIN Player ON Player.id = Time.player_id
                            WHERE Map.name=? COLLATE NOCASE
                            ORDER BY LENGTH(Time.time) ASC, CAST (Time.time AS DECIMAL) ASC
                            LIMIT ?
                        """

get_player_tournament_times =   """
                                SELECT player_id, map_id, time
                                FROM Time
                                WHERE map_id IN
                                    (SELECT map_id
                                        FROM Mappack
                                        WHERE tournament_id = ?
                                    )
                                AND player_id = ?
                                """

get_player_time =   """
                    SELECT time
                    FROM Time
                    WHERE map_id = ?
                    AND player_id = ?
                    """

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







