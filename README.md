# ZyMaaDiscordBot
[![Python Version](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/release/python-310/)

Discord bot with a bunch of cool commands build around Osu! (the game)

Commands are designed to be nerdy, but not boring, and not easy accessible, so thinking is required.

## Commands

### Fun

- Test command, that sends `test` message (`^test`)
- Beer command, that sends `n` number of beer emojis (`^beer` `<cnt>`)

### Logic

- Config change. Changes user's config variables (`^config_change` `<osu_user_id>` `<osu_game_mode>`)
- Config checks. Prints out user's config variables (`^config_check`)
- Trusted users. Prints out a list of discord users, who can use the logic of the bot (`^trusted_users`)
- Admins. Prints out a list of discord users, who can add/remove trusted users (`^admins`)
- Add trusted user (`^add_trusted_user` `<user>`)
- Remove trusted user (`^remove_trusted_user`  `<user>`)

### OsuApiLogic

- Get a grade stats on a certain group of beatmapsets obtained by query search (`^beatmapsets_stats` `<query>`)
- Get user's playcount on a beatmap (`^beatmap_playcount_slow` `<beatmap_id`)
- Get user's most recent play info (`^most_recent`)



### Help

- Custom help command (`^help`)

## Settings up the bot

To make the bot running, the following environment variables should be set (in '.env' file or somewhere else):

```
DISCORD_BOT_TOKEN=
OSU_APIV2_CLIENT_ID=
OSU_APIV2_CLIENT_SECRET=
```

The Python version should be 3.10 and all the requirements should be satisfied.

---
## Funny

Annoying stuff stumbled upon developing:
- Default help command invokes predicates for no reason
- Singleton issues (Factory is much better)
- No obsession pls

---