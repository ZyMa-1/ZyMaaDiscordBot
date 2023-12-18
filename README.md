# ZyMaaDiscordBot
[![Python Version](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)

Discord bot with a bunch of cool commands build around Osu! (the game)

[Add the bot](https://discord.com/oauth2/authorize?client_id=1147875605052915823&permissions=8&scope=bot)

Commands provide a bunch of statistics around the osu!

## Commands

Use '^help' to see recent updates on the commands.

## Settings up the bot

To make the bot running, the following environment variables should be set (in '.env' file or somewhere else):

```
DISCORD_BOT_TOKEN=
OSU_APIV2_CLIENT_ID=
OSU_APIV2_CLIENT_SECRET=
```

The Python version should be 3.10 and all the requirements should be satisfied.

Starting point of the bot is `start.py`.


## Flow of the bot

Let's get straight to the point.

Assume you want to use the fancy `^get_filtered_by_mods_xlsx_scores_file` command.

First, you need to be the 'trusted_user'. You can send the application to the first (main) admin using the `^send_trusted_user_application` command.

Then the admin will accept or deny your request. Next, set up your osu! config. Use `^config_change` command to change the config. For example, my osu! user id is `16357858` and I play `osu` (std) game mode. So I will use `^config_change 16357858 osu` command to set up my config.

Now commands like `^beatmapsets_stats` and `^beatmap_playcount_slow` are already available for you.

Next, you can load all scores to the bot's database using `^load_all_user_scores` command. It may take a long time; 11000 scores took almost one whole day. You can delete all scores from the database using `^delete_all_user_scores` command to recalculate all the scores again or to just delete them.

Everything is prepared for the use of `^get_xlsx_scores_file` and `^get_filtered_by_mods_xlsx_scores_file` commands. The result of the commands will be a `.xlsx` file. Use it however you want.

That concludes the flow of the bot!

---
## Funny

Troubles:
- Singleton issues (Factory is much better)