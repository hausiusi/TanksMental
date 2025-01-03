from ursina import *
from src.enums import EntityType

maps = [
        [            
            #-7,-6,-5,-4,-3,-2,-1,0, 1, 2, 3, 4, 5, 6, 7
            [0, 2, 0, 2, 2, 2, 0, 0, 0, 2, 2, 0, 0, 2, 0], #5
            [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0], #4
            [0, 1, 1, 1, 0, 5, 0, 0, 0, 5, 0, 1, 1, 1, 0], #3
            [0, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0], #2
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #1
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #0
            [0, 2, 2, 0, 0, 6, 0, 0, 0, 6, 0, 0, 2, 2, 0], #-1
            [0, 2, 2, 0, 0, 6, 0, 0, 0, 6, 0, 0, 2, 2, 0], #-2
            [0, 0, 0, 0, 0, 0, 5, 6, 5, 0, 0, 0, 0, 0, 0], #-3
            [0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0], #-4
            [0, 0, 0, 0, 0, 0, 6, 8, 6, 0, 0, 0, 0, 0, 0], #-5
        ],
        [            
            #-7,-6,-5,-4,-3,-2,-1,0, 1, 2, 3, 4, 5, 6, 7
            [0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0], #5
            [2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2], #4
            [2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2], #3
            [2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2], #2
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #1
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #0
            [0, 0, 0, 0, 0, 6, 0, 0, 0, 6, 0, 0, 0, 0, 0], #-1
            [0, 0, 0, 0, 0, 6, 0, 0, 0, 6, 0, 0, 0, 3, 0], #-2
            [0, 0, 0, 0, 0, 0, 5, 6, 5, 0, 0, 0, 0, 0, 0], #-3
            [0, 0, 0, 0, 0, 0, 6, 6, 6, 0, 0, 0, 0, 0, 0], #-4
            [0, 0, 0, 0, 0, 0, 6, 8, 6, 0, 0, 0, 0, 0, 0], #-5
        ],
        [
            #1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11,12,13,14,15
            #-7,-6,-5,-4,-3,-2,-1,0, 1, 2, 3, 4, 5, 6, 7
            [2, 0, 0, 6, 7, 7, 6, 6, 7, 7, 6, 0, 0, 0, 2], #5
            [2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2], #4
            [2, 1, 1, 1, 0, 5, 5, 1, 5, 5, 0, 1, 1, 1, 2], #3
            [2, 0, 2, 0, 0, 1, 3, 0, 3, 1, 0, 0, 0, 0, 2], #2
            [2, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 2], #1
            [2, 0, 2, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 1, 2], #0
            [2, 0, 1, 0, 2, 6, 2, 2, 2, 6, 2, 0, 1, 1, 2], #-1
            [2, 0, 1, 0, 2, 6, 2, 4, 2, 6, 2, 0, 1, 3, 2], #-2
            [2, 0, 6, 0, 2, 0, 6, 6, 6, 0, 2, 0, 6, 0, 2], #-3
            [2, 4, 1, 0, 6, 0, 6, 6, 6, 0, 6, 0, 1, 4, 2], #-4
            [2, 0, 1, 0, 0, 0, 6, 8, 6, 0, 0, 0, 1, 0, 2], #-5
        ],
    ]

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
                    'durability'    : 10,
                    'count'         : 5,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.ENEMY_TANK,
                    'color'         : color.azure,
                    'scale'         : (0.8, 1),
                    'max_speed'     : 1.5,
                    'max_bullets'   : 1,
                    'chosen_bullet' : 0,
                    'durability'    : 20,
                    'count'         : 5,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.BOSS,
                    'color'         : color.black,
                    'scale'         : (1.5, 1.5),
                    'max_speed'     : 2,
                    'max_bullets'   : 3,
                    'chosen_bullet' : 0,
                    'durability'    : 50,
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
                    'durability'    : 30,
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
                    'durability'    : 30,
                    'count'         : 10,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.BOSS,
                    'color'         : color.black,
                    'scale'         : (1.5, 1.5),
                    'max_speed'     : 3,
                    'max_bullets'   : 3,
                    'chosen_bullet' : 1,
                    'durability'    : 100,
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
                    'durability'    : 50,
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
                    'durability'    : 60,
                    'count'         : 10,
                    'at_once'       : 5
                },
                {
                    'texture'       : 'assets/images/tank0.png',
                    'entity_type'   : EntityType.BOSS,
                    'color'         : color.black,
                    'scale'         : (1.5, 1.5),
                    'max_speed'     : 4,
                    'max_bullets'   : 5,
                    'chosen_bullet' : 1,
                    'durability'    : 200,
                    'count'         : 1,
                    'at_once'       : 1
                }
            ]   
    ]

def __get_map(index: int):
    global maps

    if not index < len(maps):
        index = 0
    return maps[index]

def __load_npcs(level: int):
    global npcs

    return npcs[level]

def load_npcs(level: int):
    return __load_npcs(level)

def load_map(level: int):
    return __get_map(level)

def get_levels_count():
    global maps, npcs
    if len(maps) != len(npcs):
        raise ValueError("The number of levels and the number of NPC pools should be the same")
    return len(maps)