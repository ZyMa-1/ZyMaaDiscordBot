from db_managers.data_classes import DbUserInfo, DbScoreInfo
from db_managers.models.models import ScoreTable, UserTable


def from_db_user_info(user_info: DbUserInfo) -> UserTable:
    return UserTable(discord_user_id=user_info.discord_user_id,
                     osu_user_id=user_info.osu_user_id,
                     _osu_game_mode=str(user_info.osu_game_mode.value))


def from_db_score_info(score_info: DbScoreInfo) -> ScoreTable:
    return ScoreTable(user_info_id=score_info.user_info_id,
                      score_json_data=score_info.score_json_data,
                      _mods=int(score_info.mods.value),
                      timestamp=score_info.timestamp)


def from_user_row(row: UserTable):
    return DbUserInfo(discord_user_id=row.discord_user_id,
                      osu_user_id=row.osu_user_id,
                      osu_game_mode=row.osu_game_mode)


def from_score_row(row: ScoreTable):
    return DbScoreInfo(id=row.id,
                       user_info_id=row.user_info_id,
                       score_json_data=row.score_json_data,
                       mods=row.mods,
                       timestamp=row.timestamp)
