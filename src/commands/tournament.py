from interactions import (
    Extension,
    slash_command, 
    slash_option, 
    SlashContext,
    SlashCommandChoice,
    OptionType
)
import src.db.db as db

class Tournament(Extension):

    @slash_command(
        name="tournament",
        description="Tournament management"
    )
    @slash_option(
        name="action",
        description="Tournament management action",
        required=True,
        opt_type = OptionType.STRING,
        choices=[
            SlashCommandChoice(name="create", value="create"),
            SlashCommandChoice(name="delete", value="delete"),
            SlashCommandChoice(name="auto update ON", value="autoon"),
            SlashCommandChoice(name="auto update OFF", value="autooff")
        ]
    )
    @slash_option(
        name="name",
        description="Name of the tournament you want to manage",
        required=True,
        opt_type = OptionType.STRING
    )
    async def tournament(self, ctx: SlashContext, action: str, name: str = ""):

        conn = db.open_conn()

        try:
            match action:
                case "create":
                    query = [(db.add_tournament, [name])]
                    res = "Created tournament: " + name
                    db.execute_queries(conn, query)
                case "delete":
                    query = [(db.remove_tournament, [name])]
                    res = "Deleted tournament: " + name
                    db.execute_queries(conn, query)
                case "autoon":
                    query = [(db.auto_update_tournament, (1, name))]
                    res = "Turned ON auto update for tournament: " + name
                    db.execute_queries(conn, query)
                case "autooff":
                    query = [(db.auto_update_tournament, (0, name))]
                    res = "Turned OFF auto update for tournament: " + name
                    db.execute_queries(conn, query)
                case _:
                    res = "invalid tournament action"

            # always send reply
            await ctx.send(f"{res}")

        except Exception as e:
            await ctx.send(f"Error occurred while running command: {e}")

        finally:
            conn.close() 

    @slash_command(
        name="tournament_list",
        description="Lists all tournaments."
    )
    async def tournament_list(self, ctx: SlashContext):
        conn = db.open_conn()
        try:
            query = (db.list_tournaments, None)
            res = db.retrieve_data(conn, query)
            await ctx.send(f"{res}")
        except Exception as e:
            await ctx.send(f"Error occurred while running command: {e}")
        finally:
            conn.close() 