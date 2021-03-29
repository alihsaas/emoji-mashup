## Emoji Mashup

A discord bot that generates random emojis out of other emojis' parts.

## Running

1. **Make sure to get python 3.5 or higher**

This is required to run the bot.

2. **Set up venv**

Run `python -m venv venv` in your shell. Then activate your venv.

3. **Install dependencies**

Run `pip install -r requirements.txt`

4. **Setup configuration**

Create a file named `config.py` in the root of your project.
This file should follow the following template:
```env
TOKEN="YOUR_TOKEN"
GUILDS = [] # list of guild ids the bot should allow the usage of slash commands in, leave as empty list to run in all servers the bot is in

GUILDS_INFO = {
	"""
	SOME_GUILD_ID: {
		"whitelisted_channels": [] list of channel ids the bot is allowed to talk in
		"manage_emojis": boolean: weither the bot should have votes for weither to add the generated emoji to the server or not
	}
	"""

	714868972549570653: {
		"whitelisted_channels": [809381683899400222],
		"manage_emojis": False
	}
}
```

5. **Run the bot**

Run `python bot.py` in your shell.