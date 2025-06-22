from enum import Enum

class CollisionEffect(Enum):
    NO_EFFECT = 0
    BARRIER = 1
    SLOW_DOWN = 2
    SLIDE = 3
    DAMAGE_BURN = 4
    DAMAGE_WET = 5
    DAMAGE_EXPLOSION = 6

class EntityType(Enum):
    PLAYER_TANK = 0
    ENEMY_TANK = 2
    TERRAIN = 3
    SUPPLY_DROP = 4
    BASE = 5
    BOSS = 6
    BULLET = 7
    LANDMINE = 8

class DropEffect(Enum):
    MISSILE_DAMAGE_INCREASE = 0
    MISSILE_SPEED_INCREASE = 1
    MISSILE_RATE_INCREASE = 2
    LANDMINE_PICK = 3
    BUILDING_BLOCK_PICK = 4