from ursina import *
from .widgetry.healthbar import HealthBar
from .enums import CollisionEffect, EntityType, DropEffect
from .misc.timer import Timer
from .ammunition import AmmoCatalog
from .widgetry.drops import randomize_drop
from .widgetry.effects import WetEffect, FireEffect, AimEffect
from .misc.spranimator import SpriteAnimator
from .misc.utils import vectors_are_equal


class Tank(Entity):
    def __init__(self, game, max_durability, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.game.tanks.append(self)
        self.max_durability = max_durability
        self.durability = max_durability
        self.healthy_texture = self.texture
        self.health_bar = HealthBar(max_health=self.max_durability, current_health=self.durability, parent_entity=self)
        self.kills = 0
        self.tanks_damage_dealt = 0
        self.other_damage_dealt = 0
        self.affected_speed = 0
        self.collision_effect = CollisionEffect.BARRIER
        self.is_burn_damaging = False
        self.deaths = 0        
        self.explosion_animation = SpriteAnimator('assets/animations/explosion', delay=0.05)
        self.burn_damage_timer = Timer(timeout=1, counts=10, tick_callback=self.apply_burn_damage, end_callback=self.stop_burn_damage)
        self.wet_damage_timer = Timer(timeout=5, counts=1, tick_callback=self.apply_wet_damage, end_callback=self.stop_wet_damage)
        self.slow_down_timer = Timer(timeout=0.2, counts=1, tick_callback=self.apply_slow_down, end_callback=self.stop_slow_down)

        self.water_effect = WetEffect(self)
        self.fire_effect = FireEffect(self)
        self.aim_effect = AimEffect(self, position=(0, 1))
        self.ammunition = AmmoCatalog(self)

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
        return self.ammunition.bullet_pool.max_bullets
    
    @property
    def bullet_hit_damage(self):
        return self.ammunition.bullet_pool.hit_damage
    
    @property
    def bullet_speed(self):
        return self.ammunition.bullet_pool.bullet_speed        
    
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

    def check_destroy(self):
        if self.durability <= 0:
            self.is_exploded = True
            self.color = color.rgba(self.color.r, self.color.g, self.color.b, 0.5)
            self.health_bar.visible = False
            self.ammunition.bullet_effect.visible = False
            self.aim_effect.visible = False
            self.water_effect.visible = False
            self.fire_effect.visible = False
            self.explosion_animation.animate(self, self._destroy_or_respawn)  
            self.deaths += 1

    def _destroy_or_respawn(self):        
        is_enemy_tank = self.entity_type is not EntityType.PLAYER_TANK
        if is_enemy_tank:
            try:
                position = self.position    # Here is a bug (Remove try catch to reproduce)   
                self.destroy()
                randomize_drop(position, self.game)
            except Exception as ex:
                print(f"Happened error while processing the destroyed enemy tank. Enemy tank object: {self}. Error: {ex}")
        else:
            self.respawn()

    def respawn(self):
        raise Exception("We implement respawn method of Tank entity in derived classes")

    def move(self, direction_vector):
        """Move the enemy tank in the specified direction if no collision is detected."""
        if self.is_exploded:
            return
        # if self.entity_type == EntityType.PLAYER_TANK:
        #     theta = math.radians(30)
        #     raycast_around(vec=direction_vector, theta=theta, n_rays=5, entity=self, distance=5, ignore=[self], debug=True)
        
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
                        self.ammunition.bullet_pool.hit_damage += 1
                    if collided_entity.drop_effect == DropEffect.MISSILE_RATE_INCREASE:
                        self.ammunition.bullet_pool.max_bullets += 1
                    if collided_entity.drop_effect == DropEffect.MISSILE_SPEED_INCREASE:
                        self.ammunition.bullet_pool.bullet_speed += 1
                    if collided_entity.drop_effect == DropEffect.LANDMINE_PICK:
                        self.ammunition.add_landmine()
                        self.ammunition.add_landmine()
                        self.ammunition.add_landmine()
                    if collided_entity.drop_effect == DropEffect.BUILDING_BLOCK_PICK:
                        self.ammunition.add_block()
                        self.ammunition.add_block()
                    destroy(collided_entity)
                    destroy(collided_entity)
                elif (collided_entity.entity_type == EntityType.ENEMY_TANK 
                      or collided_entity.entity_type == EntityType.PLAYER_TANK or 
                      collided_entity.entity_type == EntityType.BOSS):
                    if collided_entity.collision_effect == CollisionEffect.BARRIER:
                        movement_is_allowed = False
                        break
                if collided_entity.entity_type == EntityType.LANDMINE:
                    if collided_entity.collision_effect == CollisionEffect.DAMAGE_EXPLOSION:
                        damage_amount = min(self.durability, collided_entity.effect_strength)
                        collided_entity.owner.tanks_damage_dealt += damage_amount
                        self.durability -= collided_entity.effect_strength
                        self.check_destroy()
                        collided_entity.explode()
        
        if movement_is_allowed:
            next_position = self.position + direction_vector * (time.dt * self.speed)
            self.__move(next_position)

        if vectors_are_equal(direction_vector, Vec3(0, 1, 0)):
            self.rotation_z = 0
        if vectors_are_equal(direction_vector, Vec3(1, 0, 0)):
            self.rotation_z = 90
        if vectors_are_equal(direction_vector, Vec3(0, -1, 0)):
            self.rotation_z = 180
        if vectors_are_equal(direction_vector, Vec3(-1, 0, 0)):
            self.rotation_z = -90

    @staticmethod
    def get_collision_element(element, direction, distance):
        """Gets the entity that was collided with passed entity"""
        try:
            ray = raycast(element.position, direction, ignore=[element], distance=distance)
            if ray.hit:
                return ray
        except Exception as ex:
            pass
        return None

    def move_bullet(self, dt):
        active_bullets = [] # List of (bullet, pool) tuples
        for pool in self.ammunition.bullet_pools:
            for bullet in pool.active_bullets:
                active_bullets.append((bullet, pool))
        for bullet, pool in active_bullets:
            ray = self.get_collision_element(bullet, bullet.velocity, 1)
            bullet.position += bullet.velocity * dt
            collided_entities, collision_point = [], (0, 0)
            if ray is not None:
                collided_entities, collision_point = ray.entities, ray.point
            # Find the first collided entity that takes hit
            collided_entity = None
            for entity in collided_entities:
                if hasattr(entity, 'takes_hit'):
                    collided_entity = entity
            # Destroy bullet if it goes off-screen
            if collided_entity == None and not self.game.is_on_screen(bullet):
                pool.release_bullet(bullet)
                return
            
            if bullet.visible and collided_entity != None:
                # This if and break affect the performance - consider fixing it
                if (collided_entity.entity_type == self.ammunition.owner.entity_type 
                    or collided_entity.entity_type == EntityType.BOSS and self.ammunition.owner.entity_type == EntityType.ENEMY_TANK
                    or collided_entity.entity_type == EntityType.ENEMY_TANK and self.entity_type == EntityType.BOSS):
                    break
                if collided_entity.takes_hit:
                    collided_entity.durability -= bullet.hit_damage
                    if collided_entity.durability <= 0:
                        if hasattr(collided_entity, 'is_tank'):
                                if not collided_entity.is_exploded:
                                    self.kills += 1
                                    collided_entity.check_destroy()
                        else:
                            destroy(collided_entity)
                            if collided_entity.entity_type == EntityType.BASE:
                                self.game.show_game_over()
                    if hasattr(collided_entity, 'is_tank') and not collided_entity.is_exploded:
                        self.tanks_damage_dealt += pool.hit_damage
                    else:
                        self.other_damage_dealt += pool.hit_damage
                        
                    self.ammunition.bullet_pool.release_bullet(bullet)

    def update(self):
        self.move_bullet(time.dt)
        if self.game.over:
            return
        
        self.burn_damage_timer.update()
        self.wet_damage_timer.update()
        self.slow_down_timer.update()

        if self.is_exploded:
            self.explosion_animation.update()
            if self.entity_type == EntityType.BOSS:
                self.boss_audio.stop()                
                
    def __move(self, next_position):
        if self.game.is_position_on_screen(next_position):
            self.position = next_position

    def destroy(self):
        self.ammunition.destroy()
        destroy(self.boss_audio)

        print(f'{self} destroyed')
        destroy(self)
