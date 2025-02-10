from ursina import *
from src.enums import EntityType

npcs = [
            [
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.white,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 1,
                    'max_bullets'   : 1,
                    'chosen_bullet' : 0,
                    'max_durability': 10,
                    'count'         : 20,
                    'at_once'       : 2
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.azure,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 1.5,
                    'max_bullets'   : 1,
                    'chosen_bullet' : 0,
                    'max_durability': 10,
                    'count'         : 20,
                    'at_once'       : 2
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.BOSS,
                    'color'         : color.black,
                    'scale'         : (1, 1),
                    'max_speed'     : 2,
                    'max_bullets'   : 3,
                    'chosen_bullet' : 0,
                    'max_durability': 100,
                    'count'         : 1,
                    'at_once'       : 1
                }
            ],
            [
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.green,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 1.5,
                    'max_bullets'   : 1,
                    'chosen_bullet' : 1,
                    'max_durability': 1,
                    'count'         : 5,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.yellow,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 2,
                    'max_bullets'   : 2,
                    'chosen_bullet' : 0,
                    'max_durability': 1,
                    'count'         : 10,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.BOSS,
                    'color'         : color.black,
                    'scale'         : (1, 1),
                    'max_speed'     : 3,
                    'max_bullets'   : 3,
                    'chosen_bullet' : 1,
                    'max_durability': 1,
                    'count'         : 1,
                    'at_once'       : 1
                }
            ],
            [
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.green,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 2,
                    'max_bullets'   : 2,
                    'chosen_bullet' : 1,
                    'max_durability': 50,
                    'count'         : 10,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.yellow,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 2,
                    'max_bullets'   : 4,
                    'chosen_bullet' : 0,
                    'max_durability': 60,
                    'count'         : 10,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.BOSS,
                    'color'         : color.black,
                    'scale'         : (1, 1),
                    'max_speed'     : 4,
                    'max_bullets'   : 5,
                    'chosen_bullet' : 1,
                    'max_durability': 200,
                    'count'         : 1,
                    'at_once'       : 1
                }
            ],
            [
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.green,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 2,
                    'max_bullets'   : 4,
                    'chosen_bullet' : 1,
                    'max_durability': 50,
                    'count'         : 15,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.yellow,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 3,
                    'max_bullets'   : 4,
                    'chosen_bullet' : 0,
                    'max_durability': 50,
                    'count'         : 10,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.BOSS,
                    'color'         : color.black,
                    'scale'         : (1, 1),
                    'max_speed'     : 6,
                    'max_bullets'   : 8,
                    'chosen_bullet' : 1,
                    'max_durability': 300,
                    'count'         : 2,
                    'at_once'       : 2
                }
            ],
            [
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.green,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 2,
                    'max_bullets'   : 4,
                    'chosen_bullet' : 1,
                    'max_durability': 100,
                    'count'         : 15,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.yellow,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 3,
                    'max_bullets'   : 4,
                    'chosen_bullet' : 0,
                    'max_durability': 100,
                    'count'         : 10,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.BOSS,
                    'color'         : color.black,
                    'scale'         : (1, 1),
                    'max_speed'     : 6,
                    'max_bullets'   : 8,
                    'chosen_bullet' : 1,
                    'max_durability': 300,
                    'count'         : 2,
                    'at_once'       : 2
                }
            ]     
    ]


def __load_npcs(level: int):
    global npcs

    return npcs[level]


def load_npcs(level: int):
    return __load_npcs(level)


def get_levels_count():
    return len(npcs)