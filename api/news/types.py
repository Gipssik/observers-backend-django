from enum import Enum


class UpdateAction(str, Enum):
    """Enum for possible update actions."""

    LIKES = "likes"
    DISLIKES = "dislikes"

    @classmethod
    def tuple(cls) -> tuple[str, ...]:
        """Returns a tuple of all enum's values.

        :return: Tuple of all values of enum.
        """
        return tuple(str(value.value) for value in cls.__members__.values())
