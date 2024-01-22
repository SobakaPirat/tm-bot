import pkgutil

import interactions
from dotenv import find_dotenv, load_dotenv, get_key

import src.db.db as db
from src.ubi.authentication import *



# load bot variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
TOKEN = get_key(dotenv_path, "DISCORD_TOKEN")
GUILD_ID = get_key(dotenv_path, "GUILD_ID")


bot = interactions.Client(
    # set debug_scope to not be in global scope
    debug_scope=GUILD_ID, 
)
#bot.interaction_tree.update()

# set up db
db.init()

#TODO: Authenticate



# Load all extensions
extensions = [m.name for m in pkgutil.iter_modules(["src/commands"], prefix="src.commands.")]
for extension in extensions:
    bot.load_extension(extension)

bot.start(TOKEN)
