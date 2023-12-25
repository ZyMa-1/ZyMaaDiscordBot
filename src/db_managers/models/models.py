from datetime import datetime

from ossapi import GameMode, Mod
from sqlalchemy import Column, Integer, Enum, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import Base
from ..data_classes import DbUserInfo, DbScoreInfo


class User(Base):
    __tablename__ = 'users'

    discord_user_id = Column(Integer, primary_key=True, autoincrement=False)
    osu_user_id = Column(Integer)
    osu_game_mode = Column(Enum(GameMode))

    @classmethod
    def from_db_user_info(cls, user_info: DbUserInfo):
        return cls(discord_user_id=user_info.discord_user_id,
                   osu_user_id=user_info.osu_user_id,
                   osu_game_mode=user_info.osu_game_mode)


class Score(Base):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    user_info_id = Column(Integer, ForeignKey('users.discord_user_id'))
    score_json_data = Column(String)
    mods = Column(Enum(Mod))
    timestamp = Column(DateTime, default=datetime.now)

    user_info = relationship("User", back_populates="scores")

    @classmethod
    def from_db_score_info(cls, score_info: DbScoreInfo):
        return cls(user_info_id=score_info.user_info_id,
                   score_json_data=score_info.score_json_data,
                   mods=score_info.mods,
                   timestamp=score_info.timestamp)
