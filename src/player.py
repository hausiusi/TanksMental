from ursina import *
from src.game import Game
from src.healthbar import HealthBar
from src.tank import Tank
from src.controller import BaseController
from src.types import EntityType

class Player(Tank):
    def __init__(self, game : Game, controller: BaseController, player_id: int, **kwargs):
        super().__init__(game, entity_type=EntityType.PLAYER_TANK, **kwargs)
        self.game = game
        self.controller = controller
        self.player_id = player_id        
        self.initial_position = self.position
        self.controller.initialize_controller()
        self.bullet_switch_speed = 0.3
        self.last_bullet_switch = 0

        stat_items = {"player_id" : "Player", 
                      "health" : "Health", 
                      "speed" : "Speed", 
                      "bullet_hit_damage" : "Hit damage",
                      "bullet_speed": "Missile speed",
                      "bullets_on_screen" : "Visible bullets",
                      "bullets_max" : "Max bullets",
                      "tanks_damage_dealt" : "Tanks dmg",
                      "other_damage_dealt" : "Other dmg",
                      "total_damage_dealt" : "Total dmg",
                      "kills" : "Kills"
                      }
        self.stat_text_pairs = []
        pos_y = 0
        pos_x = 0
        if player_id == 0:
            pos_x = self.game.left_edge
            pos_y = 0.3
        elif player_id == 1:
            pos_x = self.game.right_edge - 0.15
            pos_y = 0.3
        elif player_id == 2:
            pos_x = self.game.left_edge
            pos_y = 0

        origin_x = -0.5
        for key in stat_items.keys():
            value = getattr(self, key)
            name_text = Text(
            name=key,
            text=f"{stat_items[key]}",
            scale=0.6,
            position=(pos_x, pos_y),
            z=-0.1,
            color=color.white,
            origin=(origin_x, pos_y)
            )

            value_text = Text(
            text=f"{value}",
            scale=0.6,
            position=(pos_x + 0.1, pos_y),
            z=-0.1,
            color=color.white,
            origin=(origin_x, pos_y)
            )
            self.stat_text_pairs.append((name_text, value_text))
            pos_y -= 0.02

    def update(self):
        if self.game.over:
            return
        
        movement_distance = 0.5
        direction = ""
        buttons_state = self.controller.get_buttons_state(self.player_id)
        if buttons_state['left']:
            direction = 'a'
        if buttons_state['up']:
            direction = 'w'
        if buttons_state['down']:
            direction = 's'
        if buttons_state['right']:
            direction = 'd'
        self.move(direction, movement_distance)            

        if buttons_state['shoot'] and self.can_shoot == True and self.bullets_on_screen < self.bullets_max:
            self.bullet.shoot_bullet(self)
            self.can_shoot = False
        elif not buttons_state['shoot']:
            self.can_shoot = True

        self.last_bullet_switch += time.dt
        if buttons_state['next_bullet'] and self.last_bullet_switch > self.bullet_switch_speed:
            self.bullet.next_bullet_variant()
            self.last_bullet_switch = 0

        if not self.is_exploded:
            self.health_bar.update_health(self.durability)

        super().update()

    def refresh_stats(self):
        for stat_text_pair in self.stat_text_pairs:
            attr = stat_text_pair[0].name
            value = getattr(self, attr)
            stat_text_pair[1].text = f'{value}'
