from enum import Enum


class UpdateAction(str, Enum):
    LIKES = "likes"
    DISLIKES = "dislikes"

    @classmethod
    def tuple(cls):
        return tuple(v.value for v in cls.__members__.values())
