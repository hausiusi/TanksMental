from ursina import *
from src.game import Game
from src.healthbar import HealthBar
from src.tank import Tank
from src.types import EntityType
import random

class EnemyTank(Tank):
    def __init__(self, game : Game, **kwargs):
        super().__init__(game, entity_type=EntityType.ENEMY_TANK, **kwargs)
        self.game = game
        self.turn_time_counter = 0
        self.next_turn_time = random.uniform(0.0, 0.5)
        self.least_interval_between_bullets = 0.2
        self.bullet_interval_counter = 0

    def update(self):
        # Enemy tank movement logic
        if self.turn_time_counter > self.next_turn_time:
            self.direction = random.randint(0, 3)  # Pick a random direction
            self.turn_time_counter = 0
            self.next_turn_time = random.uniform(1, 5)
        self.turn_time_counter += time.dt

        # Attempt to move the tank in its current direction
        movement_distance = 0.5
        self.move(self.direction, movement_distance)

        self.bullet_interval_counter += time.dt

        if (self.bullet_interval_counter > self.least_interval_between_bullets 
            and not self.is_exploded 
            and self.bullets_on_screen < self.bullets_max):
            if self.bullets_on_screen < 0:
                self.bullets_on_screen = 0
                
            self.bullet.shoot_bullet(self)
            self.bullet_interval_counter = 0
            self.health_bar.update_health(self.durability)

        super().update()
        