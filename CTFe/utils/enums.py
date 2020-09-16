from enum import Enum


class UserType(str, Enum):
    ADMIN = 'admin'
    PLAYER = 'player'
    CONTRIBUTOR = 'contributor'

    @classmethod
    def has_type(cls, value):
        return (
            value in cls.__members__.keys()
            or
            value in cls.__members__.values()
        )
