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

Proceed directly to the following steps:
Consider using the `^get_filtered_by_mods_xlsx_scores_file` command.

Begin by obtaining 'trusted_user' status.
Submit your application to the primary administrator using the
`^send_trusted_user_application` command.

Await approval or denial from the administrator.
Configure your osu! settings.
Utilize the `^config_change` command to modify the configuration.
For instance, if your osu! user id is `16357858` and you play `osu` (std) game mode,
execute the command `^config_change 16357858 osu` to set up your config.

Commands like `^beatmapsets_stats` and `^beatmap_playcount_slow` are now accessible.

Load all beatmaps user has ever played into the bot's database using
`^load_all_user_played_beatmaps`.
Load all scores into the bot's database with `^load_all_user_scores`.
This process may take a considerable amount of time.
For instance, processing 11000 scores took almost a day.
You can erase all scores from the database using `^delete_all_user_scores`
to recalculate or simply delete them.

Now you are ready to utilize the
`^get_xlsx_scores_file` and `^get_filtered_by_mods_xlsx_scores_file` commands.
The output will be a '.xlsx' file.
Feel free to use it in any way you prefer.

This concludes the operational flow of the bot!

---
## Funny

Troubles:
- Singleton issues (Factory is much better)
