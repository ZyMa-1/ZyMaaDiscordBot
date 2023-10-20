# ZyMaaDiscordBot
[![Python Version](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)

Discord bot with a bunch of cool commands.

## Commands

### Fun

- Test command, that sends `test` message (`^test`)
- Beer command, that sends user `n` number of beer emojis (`^beer` `<cnt>`)

### Logic

- Config change. Changes the user config variables (`^config_change` `<osu_user_id>` `<osu_game_mode>`)
- Config checks. Prints out user's config variables (`^config_check`)
- Trusted users. Prints out a list of discord users, who can use the logic of the bot (`^trusted_users`)
- Admins. Prints out a list of discord users, who can add/remove trusted users (`^admins`)
- Add trusted user (`^add_trusted_user <user>`)
- Remove trusted user (`^remove_trusted_user <user>`)

### OsuApiLogic

- Get a grade stats on a certain group of beatmapsets obtained by query search (`beatmapsets_stats  <query>`)

### Help

- Custom help command (`^help`)

## Settings up the bot

To make the bot run, the following env variables should be there:

```
DISCORD_BOT_TOKEN=
OSU_APIV2_CLIENT_ID=
OSU_APIV2_CLIENT_SECRET=
```

The Python version should be 3.10 and all the requirements should be satisfied.

---

Annoying stuff stumbled upon developing:
- Default help command invokes predicates for no reason
- Singleton issues (Factory is much better)