from ursina import *
from src.game import Game
from src.healthbar import HealthBar
from src.types import CollisionEffect, EntityType, DropEffect
from src.timer import Timer
from src.ammunition import AmmoCatalog
from src.drops import randomize_drop
from src.effects import WetEffect, FireEffect

class Tank(Entity):
    def __init__(self, game : Game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.healthy_texture = self.texture
        self.health_bar = HealthBar(max_health=self.durability, current_health=self.durability, parent_entity=self)
        self.kills = 0
        self.tanks_damage_dealt = 0
        self.other_damage_dealt = 0
        self.affected_speed = 0
        self.collision_effect = CollisionEffect.BARRIER
        self.is_burn_damaging = False

        self.burn_damage_timer = Timer(timeout=1, counts=10, tick_callback=self.apply_burn_damage, end_callback=self.stop_burn_damage)
        self.wet_damage_timer = Timer(timeout=10, counts=1, tick_callback=self.apply_wet_damage, end_callback=self.stop_wet_damage)
        self.slow_down_timer = Timer(timeout=0.2, counts=1, tick_callback=self.apply_slow_down, end_callback=self.stop_slow_down)

        self.ammunition = AmmoCatalog(self)
        self.water_effect = WetEffect(self)
        self.fire_effect = FireEffect(self)

        self.boss_audio = Audio('assets/audio/boss.ogg', loop=True, volume=0.5, autoplay=False)
        if self.entity_type == EntityType.BOSS:
            self.boss_audio.play()

    @property
    def total_damage_dealt(self):
        return self.tanks_damage_dealt + self.other_damage_dealt
    
    @property
    def speed(self):
        return round(self.max_speed - ((self.affected_speed / 100) * self.max_speed), 2)
    
    @property
    def health(self):
        return max(0, self.durability)
    
    @property
    def bullets_max(self):
        return self.ammunition.bullet.max_bullets
    
    @property
    def bullet_hit_damage(self):
        return self.ammunition.bullet.hit_damage
    
    @property
    def bullet_speed(self):
        return self.ammunition.bullet.speed        
    
    def apply_burn_damage(self, effect):
        self.fire_effect.visible = True
        self.durability -= effect
        self.check_destroy()

    def stop_burn_damage(self):
        self.burn_damage_timer.stop()
        self.fire_effect.visible = False

    def apply_wet_damage(self, effect):
        self.stop_burn_damage()
        self.water_effect.visible = True
        self.apply_slow_down(effect)

    def stop_wet_damage(self):
        self.water_effect.visible = False
        self.affected_speed = 0
        self.wet_damage_timer.stop()

    def apply_slow_down(self, effect):
        self.affected_speed = max(self.affected_speed, effect)

    def stop_slow_down(self):
        self.affected_speed = 0
        self.slow_down_timer.stop()

    def check_destroy(self, texture='assets/images/tank0_explode.png'):
        if self.durability <= 0:
            self.texture = texture
            self.is_exploded = True

    def respawn(self):
        raise Exception("We implement respawn method of Tank entity in derived classes")

    def move(self, direction, movement_distance):
        """Move the enemy tank in the specified direction if no collision is detected."""
        if direction not in self.game.directions:
            return
        
        direction_vector = self.game.directions[direction]
        if self.is_exploded:
            return
        
        
        movement_is_allowed = True
        #collided_entity = self.game.get_collided_entity(self, direction_vector, movement_distance)
        next_position = self.position + direction_vector * (time.dt * self.speed)
        collided_entities = self.game.get_collided_entities_at_position(self, next_position)
        if len(collided_entities) == 0:
            #self.affected_speed = 0
            movement_is_allowed = True
        else:
            for collided_entity in collided_entities:
                if collided_entity.entity_type == EntityType.TERRAIN:
                    if hasattr(collided_entity, 'collision_effect'):
                        if collided_entity.collision_effect == CollisionEffect.BARRIER:
                            movement_is_allowed = False
                            break
                        if collided_entity.collision_effect == CollisionEffect.SLOW_DOWN:
                            if not self.wet_damage_timer.is_on:
                                self.slow_down_timer.start(collided_entity.effect_strength)
                        elif collided_entity.collision_effect == CollisionEffect.DAMAGE_BURN:
                            self.burn_damage_timer.start(collided_entity.effect_strength)
                        elif collided_entity.collision_effect == CollisionEffect.DAMAGE_WET:
                            self.wet_damage_timer.start(collided_entity.effect_strength)
                elif collided_entity.entity_type == EntityType.SUPPLY_DROP:
                    if collided_entity.drop_effect == DropEffect.MISSILE_DAMAGE_INCREASE:
                        self.ammunition.bullet.hit_damage += 1
                    if collided_entity.drop_effect == DropEffect.MISSILE_RATE_INCREASE:
                        self.ammunition.bullet.max_bullets += 1
                    if collided_entity.drop_effect == DropEffect.MISSILE_SPEED_INCREASE:
                        self.ammunition.bullet.speed += 1
                    destroy(collided_entity)
                elif (collided_entity.entity_type == EntityType.ENEMY_TANK 
                      or collided_entity.entity_type == EntityType.PLAYER_TANK or 
                      collided_entity.entity_type == EntityType.BOSS):
                    if collided_entity.collision_effect == CollisionEffect.BARRIER:
                        movement_is_allowed = False
                        break
        
        if movement_is_allowed:
            next_position = self.position + direction_vector * (time.dt * self.speed)
            self.__move(next_position)

        if direction == 0 or direction == 'w':
            self.rotation_z = 0
        if direction == 1 or direction == 'd':
            self.rotation_z = 90
        if direction == 2 or direction == 's':
            self.rotation_z = 180
        if direction == 3 or direction == 'a':
            self.rotation_z = -90

    def update(self):
        if self.game.over:
            return
        
        self.burn_damage_timer.update()
        self.wet_damage_timer.update()
        self.slow_down_timer.update()
        if self.is_exploded:
            self.remove_counter += time.dt
            if self.remove_counter > self.remove_limit:
                tmp_position = self.position
                if self.entity_type is not EntityType.PLAYER_TANK:
                    print(f"{self.name} has been destroyed")
                    destroy(self)
                    if self.entity_type == EntityType.BOSS:
                        self.boss_audio.stop()
                else:
                    self.respawn()
                randomize_drop(tmp_position)

    def __move(self, next_position):
        if self.game.is_position_on_screen(next_position):
            self.position = next_position