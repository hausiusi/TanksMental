from enum import Enum

class CollisionEffect(Enum):
    NO_EFFECT = 0
    BARRIER = 1
    SLOW_DOWN = 2
    SLIDE = 3
    DAMAGE_BURN = 4
    DAMAGE_WET = 5