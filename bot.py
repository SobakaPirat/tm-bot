import pkgutil

from interactions import (
    Client,
    Intents
)
from dotenv import find_dotenv, load_dotenv, get_key


# Load bot variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
TOKEN = get_key(dotenv_path, "DISCORD_TOKEN")
#GUILD_ID = get_key(dotenv_path, "GUILD_ID")


bot = Client(
    # set debug_scope to not be in global scope
    #debug_scope=GUILD_ID,
    # any discord intents we need
    intents=Intents.GUILDS
)

# Load all extensions
extensions = [m.name for m in pkgutil.iter_modules(["src/commands"], prefix="src.commands.")]
print(extensions)
for extension in extensions:
    bot.load_extension(extension)

# Start the bot
bot.start(TOKEN)
