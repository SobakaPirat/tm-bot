from interactions import (
    Extension,
    slash_command, 
    slash_option, 
    SlashContext,
    OptionType,
    SlashCommandChoice
)
import src.db.db as db

class Player(Extension):

    @slash_command(
    name="player_add",
    description="Add a player to the database."
    )
    @slash_option(
        name="nickname",
        description="Nickname of the player you want to add.",
        required=True,
        opt_type = OptionType.STRING
    )
    @slash_option(
        name="account_id",
        description="Account id of the player you want to add.",
        required=True,
        opt_type = OptionType.STRING
    )
    @slash_option(
        name="country",
        description="Discord flag country code of the player you want to add. Example: :flag_pl:",
        required=False,
        opt_type = OptionType.STRING
    )
    @slash_option(
        name="official_roster",
        description="Is the player part of an official PIWO roster?",
        required=False,
        opt_type = OptionType.STRING
    )
    @slash_option(
        name="extra",
        description="If the player is captain, etc.",
        required=False,
        opt_type = OptionType.STRING
    )
    async def player_add(self, ctx: SlashContext, nickname: str, account_id: str, 
                         country: str = None, official_roster: str = None, extra: str = None):

        conn = db.open_conn()

        try:

            query = [(db.add_player, (nickname, account_id, country, official_roster, extra))]
            db.execute_queries(conn, query)
            res = "Added player: " + nickname

            # always send reply
            await ctx.send(f"{res}")

        except Exception as e:
            await ctx.send(f"Error occurred while running command: {e}")

        finally:
            conn.close() 

    @slash_command(
        name="player_remove",
        description="Remove a player from the database."
    )
    @slash_option(
        name="nickname",
        description="Nickname of the player you want to remove.",
        required=True,
        opt_type = OptionType.STRING
    )
    async def player_remove(self, ctx: SlashContext, nickname: str):

        conn = db.open_conn()

        try:

            query = [(db.remove_player, [nickname])]
            db.execute_queries(conn, query)
            res = "Removed player: " + nickname

            # always send reply
            await ctx.send(f"{res}")

        except Exception as e:
            await ctx.send(f"Error occurred while running command: {e}")

        finally:
            conn.close() 

    @slash_command(
        name="player_list",
        description="Lists all players in the database."
    )
    async def player_list(self, ctx: SlashContext):

        conn = db.open_conn()

        try:

            query = [db.list_players, None]
            res = db.retrieve_data(conn, query)

            # always send reply
            await ctx.send(f"{res}")

        except Exception as e:
            await ctx.send(f"Error occurred while running command: {e}")

        finally:
            conn.close() 

    @slash_command(
        name="player_update",
        description="Update info for a player."
    )
    @slash_option(
        name="nickname",
        description="Nickname of the player.",
        required=True,
        opt_type = OptionType.STRING
    )
    @slash_option(
        name="action",
        description="What to update.",
        required=True,
        opt_type = OptionType.STRING,
        choices=[
            SlashCommandChoice(name="nickname", value="nickname"),
            SlashCommandChoice(name="account_id", value="account_id"),
            SlashCommandChoice(name="country", value="country"),
            SlashCommandChoice(name="official_roster", value="official_roster"),
            SlashCommandChoice(name="extra", value="extra")        ]
    )
    @slash_option(
        name="value",
        description="The updated value.",
        required=True,
        opt_type = OptionType.STRING
    )
    async def player_update(self, ctx: SlashContext, nickname: str, action: str, value: str):

        conn = db.open_conn()

        try:
            match action:
                case "nickname":
                    query = [(db.update_player_name, (value, nickname))]
                    db.execute_queries(conn, query)
                    res = "Updated nickname for player: " + nickname + "," + value
                case "account_id":
                    query = [(db.update_player_account_id, (value, nickname))]
                    db.execute_queries(conn, query)
                    res = "Updated account_id for player: " + nickname + "," + value
                case "country":
                    query = [(db.update_player_country, (value, nickname))]
                    db.execute_queries(conn, query)
                    res = "Updated country for player: " + nickname + "," + value
                case "official_roster":
                    query = [(db.update_player_official_roster, (value, nickname))]
                    db.execute_queries(conn, query)
                    res = "Updated official_roster for player: " + nickname + "," + value
                case "extra":
                    query = [(db.update_player_extra, (value, nickname))]
                    db.execute_queries(conn, query)
                    res = "Updated extra for player: " + nickname + "," + value
                case _:
                    res = "invalid player update action"

            # always send reply
            await ctx.send(f"{res}")

        except Exception as e:
            await ctx.send(f"Error occurred while running command: {e}")

        finally:
            conn.close() 
