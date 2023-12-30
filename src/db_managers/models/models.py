from datetime import datetime
from typing import TYPE_CHECKING

from ossapi import GameMode, Mod
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from db_managers.data_classes import DbUserInfo, DbScoreInfo


class UserTable(Base):
    __tablename__ = 'users'

    discord_user_id = Column(Integer, primary_key=True, autoincrement=False)
    osu_user_id = Column(Integer)
    _osu_game_mode = Column(String)

    # Workaround for `Column(Enum(GameMode))`
    @property
    def osu_game_mode(self):
        return GameMode(str(self._osu_game_mode))

    @classmethod
    def from_db_user_info(cls, user_info: 'DbUserInfo'):
        return UserTable(discord_user_id=user_info.discord_user_id,
                         osu_user_id=user_info.osu_user_id,
                         _osu_game_mode=str(user_info.osu_game_mode.value))

    scores = relationship("ScoreTable", back_populates="user_info")


class ScoreTable(Base):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    user_info_id = Column(Integer, ForeignKey('users.discord_user_id'))
    score_json_data = Column(String)
    _mods = Column(Integer)
    beatmap_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    # Workaround for `Column(Enum(Mod))`
    @property
    def mods(self):
        return Mod(int(self._mods))

    user_info = relationship("UserTable", back_populates="scores")

    @classmethod
    def from_db_score_info(cls, score_info: 'DbScoreInfo'):
        return cls(user_info_id=score_info.user_info_id,
                   score_json_data=score_info.score_json_data,
                   _mods=int(score_info.mods.value),
                   beatmap_id=score_info.beatmap_id,
                   timestamp=score_info.timestamp)
