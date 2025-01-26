from ursina import *
from src.widgetry.healthbar import HealthBar
from src.tank import Tank
from src.controller import BaseController
from src.enums import EntityType
from src.widgetry.bars import LandmineBar, BuildingBlockBar

class Player(Tank):
    def __init__(self, game, controller: BaseController, controller_id, player_id: int, **kwargs):
        super().__init__(game, entity_type=EntityType.PLAYER_TANK, **kwargs)
        self.game = game
        self.settings = game.settings
        self.controller_id = controller_id
        self.controller = controller
        self.player_id = player_id        
        self.initial_position = self.position
        self.initial_texture = self.texture
        self.controller.initialize_controller()
        self.switch_speed = 0.3
        self.last_bullet_switch = 0
        self.last_deployable_switch = 0
        self.pause_allowed = True
        self.landmine_drop_allowed = True
        self.move_audio = Audio("assets/audio/tank_move.ogg", volume=1, loop=True, autoplay=False)
        self.prepare_stats()

    def respawn(self):
        self.game.spawn(self)
        self.is_exploded = False
        self.texture = self.initial_texture
        self.color = color.rgba(self.color.r, self.color.g, self.color.b, 1)
        self.health_bar.visible = True
        self.ammunition.bullet_effect.visible = True
        self.remove_counter = 0
        self.durability = self.max_durability
        self.rotation_z = 0 # Respawn pointing up

    def update(self):
        if self.game.over:
            return
        if self.controller.controllers_count <= self.controller_id:
            return # There is no controller connected for this player
        buttons_state = self.controller.get_buttons_state(self.controller_id)
        if buttons_state['pause'] and self.pause_allowed:
            self.game.toggle_pause()
            self.pause_allowed = False
        elif not self.pause_allowed and not buttons_state['pause']:
            self.pause_allowed = True
        
        if self.game.paused:
            return

        if self.game.level_complete:            
            if buttons_state['shoot']:
                destroy(self.game.background)
                destroy(self.game.level_completed_text)
                destroy(self.game.press_key_text)
                self.game.destroy_terrain_elements()
                self.game.level_index += 1
                if self.game.level_index >= self.game.levels_count:
                    self.game.show_you_win()
                    return
                self.game.create_tile_map()
                self.game.npc_spawner.load_level_npcs(self.game.level_index)
                self.game.npc_spawner.spawn_initial_npcs()
                for player in self.game.players:
                    tmp = player.health
                    player.respawn()
                    player.durability = tmp

                self.game.level_complete = False
                
            return
        
        super().update()

        if self.is_exploded:
            return

        movement_distance = 0.5
        direction = ""
        if buttons_state['left']:
            direction = 'a'
        elif buttons_state['up']:
            direction = 'w'
        elif buttons_state['down']:
            direction = 's'
        elif buttons_state['right']:
            direction = 'd'
        else:
            self.move_audio.stop()
        
        if direction != "":
            if not self.move_audio.playing:
                self.move_audio.play()
            self.move(direction, movement_distance)        

        if buttons_state['shoot'] and self.can_shoot:
            self.ammunition.shoot_bullet(play_sound=True)
            self.can_shoot = False
        elif not buttons_state['shoot']:
            self.can_shoot = True

        if buttons_state['drop'] and self.landmine_drop_allowed:
            self.ammunition.deploy_object()
            self.landmine_drop_allowed = False
        elif not buttons_state['drop'] and not self.landmine_drop_allowed:
            self.landmine_drop_allowed = True

        self.last_bullet_switch += time.dt
        if buttons_state['next_bullet'] and self.last_bullet_switch > self.switch_speed:
            self.ammunition.next_bullet_variant()
            self.last_bullet_switch = 0

        self.last_deployable_switch += time.dt
        if buttons_state['previous_bullet'] and self.last_deployable_switch > self.switch_speed:
            self.ammunition.next_deployable()
            self.last_deployable_switch = 0

            if self.ammunition.deploy_pool.chosen_deployable_index == 0:
                self.landmine_stat.select(True)
                self.building_block_stat.select(False)
            elif self.ammunition.deploy_pool.chosen_deployable_index == 1:
                self.landmine_stat.select(False)
                self.building_block_stat.select(True)

        if not self.is_exploded:
            self.health_bar.update_health(self.durability)

    def refresh_stats(self):
        for stat_text_pair in self.stat_text_pairs:
            attr = stat_text_pair[0].name
            value = getattr(self, attr)
            stat_text_pair[1].text = f'{value}'
        self.landmine_stat.set_ammo_bars(self.ammunition.deploy_pool.deployables["landmine_deployer"].items_count)
        self.building_block_stat.set_ammo_bars(self.ammunition.deploy_pool.deployables["bb_deployer"].items_count)
        
    @property
    def bullets_on_screen(self):
        return len(self.ammunition.bullet_pool.active_bullets)

    def prepare_stats(self):
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
                      "kills" : "Kills",
                      "deaths" : "Deaths"
                      }
        self.stat_text_pairs = []
        pos_y = 0
        pos_x = 0
        icon_pos = (0, 0)
        if self.player_id == 0:
            pos_x = self.game.left_edge
            pos_y = 0.3            
        elif self.player_id == 1:
            pos_x = self.game.right_edge - 0.15
            pos_y = 0.3
        elif self.player_id == 2:
            pos_x = self.game.left_edge
            pos_y = -0.1
        elif self.player_id == 3:
            pos_x = self.game.right_edge - 0.15
            pos_y = -0.1

        # Place the player icon above the stats
        icon_pos = self.game.pos_text_to_pos_entity(Vec2(pos_x, pos_y))  
        icon_pos.y += self.settings.player_icon_scale / 2 + (0.05 if icon_pos.y > 0 else 0.15)
        icon_pos.x += self.settings.player_icon_scale / 2
        self.player_icon = Entity(
            model='quad', 
            position=icon_pos, 
            texture=self.texture,
            color=self.color,
            scale=(self.settings.player_icon_scale, self.settings.player_icon_scale), 
            z=-0.1)

        origin_x = -0.5
        # Text stats preparation
        for key in stat_items.keys():
            value = getattr(self, key)
            name_text = Text(
            name=key,
            text=f"{stat_items[key]}",
            scale=0.6,
            position=(pos_x, pos_y),
            z=-0.1,
            color=color.white,
            origin=(origin_x, pos_y),
            )

            value_text = Text(
            text=f"{value}",
            scale=0.6,
            position=(pos_x + 0.1, pos_y),
            z=-0.1,
            color=color.white,
            origin=(origin_x, pos_y),
            )
            self.stat_text_pairs.append((name_text, value_text))
            pos_y -= 0.02

        bar_pos = self.game.pos_text_to_pos_entity(Vec2(pos_x, pos_y))
        bar_icon_scale = (0.2, 0.2)
        bar_pos.x += bar_icon_scale[0]/2
        self.landmine_stat = LandmineBar(max=10, count=0, icon_scale=bar_icon_scale, position=bar_pos)
        bar_pos.y -= bar_icon_scale[0]
        self.building_block_stat = BuildingBlockBar(max=5, count=0, icon_scale=bar_icon_scale, position=bar_pos)
        self.landmine_stat.select(True)

    def destroy(self):
        for stat_pair in self.stat_text_pairs:
            name, value = stat_pair
            if name is not None:
                destroy(name)
            if value is not None:
                destroy(value)

        destroy(self.building_block_stat)
        destroy(self.landmine_stat)

        super().destroy()
