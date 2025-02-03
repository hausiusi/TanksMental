from ursina import Vec3, Entity, time, raycast
import math
import numpy as np
from enum import Enum
from src.misc.utils import rotate_vector_around_y
from src.enums import *
import random


class NPCMissionType(Enum):
    WANDER = 0
    FIND_AND_DESTROY_PLAYER = 1
    DESTROY_BASE = 2


class NPCBehaviour(Enum):
    SHOOT_DEFAULT_BULLET = 0
    SWITCH_BULELTS_WHEN_AVAILABLE = 1
    USE_LANDMINES = 2


class NPCIqConfig:
    def __init__(self, mission:NPCMissionType, behaviour:NPCBehaviour, visibility:int=30, distance:int=2):
        self.mission = mission
        self.behaviour = behaviour
        self.visibility = math.radians(visibility)
        self.distance = distance
        self.scanning_step = math.radians(45) / distance
        

class NPCIntelligence:
    def __init__(self, owner: Entity, iq_config: NPCIqConfig):
        self.owner = owner
        self.iq_config = iq_config
        self.scan_range = np.arange(-iq_config.visibility, iq_config.visibility, self.iq_config.scanning_step)
        self.scan_index = 0
        self.scan_index_max = len(self.scan_range) - 1
        self.turn_time_counter = 0
        self.next_turn_time = random.uniform(0.0, 0.5)
        self.direction = 0
        self.target_player = None  # Single player tracking, otherwise npc gets crazy
        self.last_known_player_position = None
        self.wandering = False
        self.locked_on_player = False
        self.lost_player_timer = 0
        self.lost_player_timeout = 3  
        self.scan_timer = random.uniform(0.5, 1.0)  
        self.player_last_position = None
        self.player_movement_direction = Vec3(0, 0, 0)
        self.detection_buffer = 0  # Detection memory counter
        self.detection_threshold = 2  # Number of consecutive detections required

    @property
    def next_scan_angle(self):
        if self.scan_index < self.scan_index_max:
            self.scan_index += 1
        else:
            self.scan_index = 0
        return self.scan_range[self.scan_index]

    def next_scan_vector(self, direction_vector):
        return rotate_vector_around_y(direction_vector, self.next_scan_angle)

    def get_random_direction(self):
        if self.turn_time_counter > self.next_turn_time:
            self.direction = random.randint(0, 3)  
            self.turn_time_counter = 0
            self.next_turn_time = random.uniform(1, 5)
        self.turn_time_counter += time.dt
        return self.owner.game.directions[self.direction]

    def scan_player_movement(self, player):
        """ Tracks the player's last movement direction every scan interval. """
        if self.player_last_position:
            movement_vector = player.position - self.player_last_position
            if movement_vector.length() > 0:  
                self.player_movement_direction = movement_vector.normalized()
        self.player_last_position = player.position

    def snap_to_smart_direction(self, player_position):
        dx = player_position.x - self.owner.position.x
        dy = player_position.y - self.owner.position.y

        align_threshold = 0.4
        # If already aligned on x-axis, move vertically
        if abs(dx) < align_threshold:
            return Vec3(0, np.sign(dy), 0)

        # If already aligned on y-axis, move horizontally
        if abs(dy) < align_threshold:
            return Vec3(np.sign(dx), 0, 0)
        
        if abs(dx) > abs(dy): # find the shortest alignment
            return Vec3(0, np.sign(dy), 0) # Moving vertically as it's faster
        elif abs(dx) < abs(dy):
            return Vec3(np.sign(dx), 0, 0)

    def get_direction(self):
        """ Determines movement based on detected player, last known position, or random wandering. 
            TODO: later other missions will be also implemented
        """
        if self.iq_config.mission == NPCMissionType.FIND_AND_DESTROY_PLAYER:
            direction_vector = self.owner.direction_vector
            vec = self.next_scan_vector(direction_vector)
            hitinfo = raycast(self.owner.position, vec, self.iq_config.distance, ignore=[self.owner], debug=False)

            if hitinfo.hit:
                entity = hitinfo.entity
                if hasattr(entity, "entity_type") and entity.entity_type == EntityType.PLAYER_TANK:
                    if self.target_player is None:
                        self.target_player = entity  
                    if self.target_player == entity:
                        self.detection_buffer += 1
                        if self.detection_buffer >= self.detection_threshold:
                            print(f"{self} locked onto player tank")
                            self.last_known_player_position = entity.position
                            self.wandering = False
                            self.locked_on_player = True
                            self.detection_buffer = 0
                            self.lost_player_timer = 0  
                            return Vec3(0, 0, 0)  

            else:
                self.detection_buffer = max(0, self.detection_buffer - 1)  
                if self.locked_on_player:
                    self.lost_player_timer += time.dt
                    if self.lost_player_timer >= self.lost_player_timeout:
                        print(f"{self} lost track of player, switching to wandering mode")
                        self.target_player = None  
                        self.last_known_player_position = None
                        self.wandering = True
                        self.locked_on_player = False

        if self.locked_on_player and self.last_known_player_position:
            self.scan_timer -= time.dt
            if self.scan_timer <= 0:
                self.scan_player_movement(self.target_player)
                self.scan_timer = random.uniform(0.5, 1.0)

            snapped_direction = self.snap_to_smart_direction(self.last_known_player_position)
            if (self.owner.position - self.last_known_player_position).length() < 0.5:
                self.last_known_player_position = None
                self.wandering = True
                self.locked_on_player = False
            return snapped_direction

        if self.wandering or not self.locked_on_player:
            return self.get_random_direction()

        return self.owner.direction_vector


if __name__ == '__main__':
    npc_config = NPCIqConfig(NPCMissionType.FIND_AND_DESTROY_PLAYER, NPCBehaviour.SHOOT_DEFAULT_BULLET)
    npc_iq = NPCIntelligence(Entity(), npc_config)


