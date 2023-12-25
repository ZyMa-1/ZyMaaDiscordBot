from datetime import datetime

from ossapi import GameMode, Mod
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import Base
from .. import conversion_utils
from ..data_classes import DbUserInfo, DbScoreInfo


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
    def from_db_user_info(cls, user_info: DbUserInfo):
        return conversion_utils.from_db_user_info(user_info)


class ScoreTable(Base):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    user_info_id = Column(Integer, ForeignKey('users.discord_user_id'))
    score_json_data = Column(String)
    _mods = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    # Workaround for `Column(Enum(Mod))`
    @property
    def mods(self):
        return Mod(int(self._mods))

    user_info = relationship("UserTable", back_populates="scores")

    @classmethod
    def from_db_score_info(cls, score_info: DbScoreInfo):
        return conversion_utils.from_db_score_info(score_info)
