from interactions import (
    Extension,
    slash_command, 
    slash_option, 
    SlashContext,
    OptionType,
    Embed,
    cooldown,
    Buckets,
    Task,
    IntervalTrigger,
    listen
)
from interactions.api.events import Startup

import src.db.db as db
from src.ubi.authentication import get_nadeo_access_token
from src.commands.map import get_map_records
from src.commands.tournament import get_tournament_id

import asyncio

class Leaderboard(Extension):

    @slash_command(
        name="leaderboard",
        description="Leaderboards for maps, tournaments etc.",
        sub_cmd_name="update",
        sub_cmd_description="Updates tournament leaderboard."
    )
    @slash_option(
        name="tournament",
        description="Name of the tournament you want update leaderboard for",
        required=True,
        opt_type = OptionType.STRING
    )
    @cooldown(Buckets.GUILD, 1, 30)
    async def update(self, ctx: SlashContext, tournament: str = None):

        await ctx.defer()

        if(tournament == None):
            await ctx.send("Error updating: no tournament provided")
            return

        conn = db.open_conn()

        try:

            # load everything that should be updated from db:
            # Get tournament map ids
            tournament_id = get_tournament_id(conn, tournament)

            if tournament_id == None:
                await ctx.send(f"Error occurred while running command: Tournament '{tournament}' not found")
                conn.close()
                return
            
            maps = db.retrieve_data(conn, (db.get_tournament_maps, [tournament_id]))
            if(len(maps) == 0):
                await ctx.send(f"Error occurred while running command: No maps found for tournament '{tournament}'")
                conn.close()
                return

            map_names = []
            map_ids = []
            for (map_name, map_id) in maps:
                map_names.append(map_name)
                map_ids.append(map_id)

            # Get tournament player ids 
            players = db.retrieve_data(conn, (db.get_tournament_roster_players, [tournament_id]))
            if(len(players) == 0):
                await ctx.send(f"Error occurred while running command: No players found for tournament '{tournament}'")
                conn.close()
                return

            #print("Players: ", players)

            player_names = []
            player_ids = []
            player_roster = []
            for (name, id, roster) in players:
                player_names.append(name)
                player_ids.append(id)
                player_roster.append(roster)

                    
            # get data from nadeo and format it nicely
            print("Retrieving nadeo data for tournament: " + tournament)

            token = get_nadeo_access_token()
            res = get_map_records(player_ids, map_ids, token)
            #print(res)
                
            # update db 
            queries = []
            for [time, player_ubi_id, map_ubi_id] in res:

                player_id = db.retrieve_data(conn, (db.get_player_id_by_account_id, [player_ubi_id]))

                if(len(player_id) == 0):
                    await ctx.send(f"Error occurred while running command: Player '{player_ubi_id}' not found")
                    conn.close()
                    return
                    
                player_id = player_id[0][0]

                map_id = db.retrieve_data(conn, (db.get_map_db_id_by_map_id, [map_ubi_id]))

                if(len(map_id) == 0):
                    await ctx.send(f"Error occurred while running command: Map '{map_ubi_id}' not found")
                    conn.close()
                    return
                    
                map_id = map_id[0][0]

                queries.append((db.add_time, (player_id, map_id, time)))

            db.execute_queries(conn, queries)

            print("Nadeo data for tournament: " + tournament + ", added to database.")

            await ctx.send(f"Updated times for tournament: " + tournament)

        except Exception as e:
            await ctx.send(f"Error occurred while running command: {e}")
        finally:
            conn.close()


    @slash_command(
        name="leaderboard",
        sub_cmd_name="map",
        sub_cmd_description="Retrieves all times for a map. Shows map tournament players only."
    )
    @slash_option(
        name="map_name",
        description="Name of the map you want retrieve times maps for",
        required=True,
        opt_type = OptionType.STRING
    )
    @slash_option(
        name="roster",
        description="Limit the times to a certain roster.",
        required=False,
        opt_type = OptionType.STRING
    )
    @slash_option(
        name="amount",
        description="How many times you want to retrieve. Default = 50",
        required=False,
        opt_type = OptionType.INTEGER   
    )
    async def map(self, ctx: SlashContext, map_name: str, roster: str = None, amount: int = 50):

        conn = db.open_conn()

        try:

            if(amount > 50):
                amount = 50
            
            if(roster is not None):
                roster_id = db.retrieve_data(conn, (db.get_roster_id, [roster]))
                if(len(roster_id) == 0):
                    await ctx.send(f"Error occurred while running command: Roster '{roster}' not found")
                    return
                roster_id = roster_id[0][0]
                res = db.retrieve_data(conn, (db.get_n_map_times_from_roster, (map_name, roster_id, amount)))
            else:
                res = db.retrieve_data(conn, (db.get_n_map_times, (map_name, amount)))

            if len(res) == 0:
                await ctx.send("Error retrieving leaderboard times: No times found.")
                return
            
            embed = format_leaderboard_embed(map_name, res, roster)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error occurred while running command: {e}")
        finally:
            conn.close()


    @Task.create(IntervalTrigger(minutes=35))
    async def update_tournaments_automatically(self):

        print("Updating tournaments automatically: ")

        conn = db.open_conn()
        query = (db.list_tournaments, None)
        tournaments = db.retrieve_data(conn, query)

        for (tournament_name, autoupdate) in tournaments:
            if autoupdate == 1:
                
                print("Trying to update tournament: " + tournament_name + "...")
                #Perform update
                try:

                    # load everything that should be updated from db:
                    # Get tournament map ids
                    tournament_id = get_tournament_id(conn, tournament_name)

                    if tournament_id == None:
                        print("Error occurred in update_tournaments_automatically: Tournament id not found")
                        continue
                    
                    maps = db.retrieve_data(conn, (db.get_tournament_maps, [tournament_id]))
                    if(len(maps) == 0):
                        print("Error occurred in update_tournaments_automatically: Tournament maps not found")
                        continue

                    map_names = []
                    map_ids = []
                    for (map_name, map_id) in maps:
                        map_names.append(map_name)
                        map_ids.append(map_id)

                    # Get tournament player ids 
                    players = db.retrieve_data(conn, (db.get_tournament_roster_players, [tournament_id]))
                    if(len(players) == 0):
                        print("Error occurred in update_tournaments_automatically: Tournament players not found")
                        continue

                    player_names = []
                    player_ids = []
                    player_roster = []
                    for (name, id, roster) in players:
                        player_names.append(name)
                        player_ids.append(id)
                        player_roster.append(roster)

                            
                    # get data from nadeo and format it nicely
                    token = get_nadeo_access_token()
                    res = get_map_records(player_ids, map_ids, token)
                        
                    # update db 
                    queries = []
                    for [time, player_ubi_id, map_ubi_id] in res:

                        player_id = db.retrieve_data(conn, (db.get_player_id_by_account_id, [player_ubi_id]))

                        if(len(player_id) == 0):
                            print("Error occurred in update_tournaments_automatically: Tournament player ids not found")
                            continue
                            
                        player_id = player_id[0][0]

                        map_id = db.retrieve_data(conn, (db.get_map_db_id_by_map_id, [map_ubi_id]))

                        if(len(map_id) == 0):
                            print("Error occurred in update_tournaments_automatically: Tournament maps not found")
                            continue
                            
                        map_id = map_id[0][0]

                        queries.append((db.add_time, (player_id, map_id, time)))

                    db.execute_queries(conn, queries)

                    print("Times for tournament updated: " + tournament_name)
                    await asyncio.sleep(1) # Stagger next update slightly


                except Exception as e:
                    print(f"Exception occurred in update_tournaments_automatically: {e}")

        conn.close()
        print("Finished updating tournaments automatically.")

    @listen(Startup)
    async def on_startup(self):
        self.update_tournaments_automatically.start()
        

#times: [(player, time)]
#   where the first entry is the best time
def format_leaderboard_embed(map_name, times, roster = None):

    embed = Embed()
    embed.title = "Leaderboard for map: " + map_name
    if(roster is not None):
        embed.description = "Showing times for roster: " + roster
    all_positions = ""
    all_players = ""
    all_times = ""

    for i, time in enumerate(times, start=1):

        (nickname, record) = time
        pos = str(i) + "."
        all_positions += pos + "\n"
        all_players += nickname + "\n"
        all_times += record + "\n"

    embed.add_field(name="Pos", value=all_positions, inline=True)
    embed.add_field(name="Player", value=all_players, inline=True)
    embed.add_field(name="Time", value=all_times, inline=True)

    return embed
