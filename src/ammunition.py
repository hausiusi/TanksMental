from ursina import *
from src.widgetry.effects import BulletEffect
from src.enums import EntityType, CollisionEffect
from src.misc.timer import Timer
from src.misc.spranimator import SpriteAnimator
from PIL import Image
from typing import List
from abc import ABC, abstractmethod

class Landmine(Entity):
    def __init__(self, owner:Entity, explosion_animation : SpriteAnimator, **kwargs):
        super().__init__(
            model='quad', 
            texture='assets/images/landmine.png',            
            collider='box',            
            color=color.white, 
            scale=(0.3, 0.3), 
            z=0,             
            **kwargs
            )
        
        self.deploy_sound = Audio('assets/audio/landmine_drop.ogg', parent=self, autoplay=False, volume=1.0)
        self.activation_sound = Audio('assets/audio/landmine_activation.ogg', parent=self,autoplay=False, volume=0.2)
        self.explosion_sound = Audio('assets/audio/landmine_explosion.ogg', parent=self, autoplay=False, volume=1.0)
        self.effect_strength=50
        self.entity_type=EntityType.LANDMINE
        self.collision_effect=CollisionEffect.NO_EFFECT
        self.explosion_animation = explosion_animation
        self.owner = owner
        self.activation_timer = Timer(3, 1, lambda _: None, self.activate)
        self.position = owner.position
        self.exploding = False
        self.deploy_sound.play()
    
    def activate(self):
        def _activate():
            self.activation_sound.play()
            self.collision_effect = CollisionEffect.DAMAGE_EXPLOSION
            self.color = color.red
            print("landmine activated")
        self.activation_timer.end_callback = _activate
        self.activation_timer.start()

    def update(self):
        self.activation_timer.update()
        if self.exploding:
            self.explosion_animation.update()

    def _destroy(self):
        destroy(self)

    def explode(self):
        self.explosion_sound.play()
        self.explosion_animation.animate(self, self._destroy)
        self.exploding = True
        

class BuildingBlock(Entity):
    def __init__(self, owner:Entity, **kwargs):
        self.tile_size = owner.game.settings.tile_size
        self.owner = owner
        super().__init__(name="building_block",
                         model='quad',
                            entity_type=EntityType.TERRAIN,
                            z = 0,                    
                            texture='assets/images/white_wall.png',
                            scale=(self.tile_size - 0.001, self.tile_size - 0.001),
                            position=(owner.x, owner.y),
                            collider='box',
                            durability=10,
                            takes_hit=True,
                            damaging=0,
                            collision_effect=CollisionEffect.BARRIER,
                            effect_strength=0,
                            render_queue=1,
                            color = color.Color(1,1,1,1),
                            **kwargs)

class Bullet(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_type=EntityType.BULLET
        self.pool_origin = None

class BulletPool:
    def __init__(self, owner, pool_size, hit_damage, bullet_speed, shoot_sound, bullet):
        if pool_size < 1:
            raise Exception("BulletPool object must have size 1 or more")
        self.bullet_prefab = bullet
        self.texture = self.bullet_prefab.texture
        self.bullet_prefab.name = f"Bullet blueprint. Owner: {owner}"
        self.pool = []
        for _ in range(pool_size):
            bullet = duplicate(self.bullet_prefab)
            bullet.pool_origin = self.pool
            self.pool.append(bullet)
        self.active_bullets = []
        self.size = pool_size
        self.hit_damage = hit_damage
        self.shoot_sound = shoot_sound
        self.bullet_speed = bullet_speed
        self.owner = owner
    
    @property
    def max_bullets(self):
        return self.size
    
    @max_bullets.setter
    def max_bullets(self, value):
        delta = value - self.size
        self.size = value
        if delta > 0:
            for _ in range(delta):
                bullet = duplicate(self.bullet_prefab)
                bullet.pool_origin = self.pool
                self.pool.append(bullet)
        elif delta < 0:
            for _ in range(delta):
                self.pool.pop()
        
    def take_bullet(self):
        if self.pool:
            bullet = self.pool.pop()
            self.active_bullets.append(bullet)
            return bullet
        return None

    def release_bullet(self, bullet):
        if bullet in self.active_bullets:
            self.active_bullets.remove(bullet)
            bullet.pool_origin.append(bullet) # append the bullet to it's original pool
            bullet.visible = False

    def increase_pool(self):
        self.pool.append(duplicate(self.pool[0]))

    def destroy_bullets(self):
        for bullet in self.pool:
            print(f"Destroying pooled bullet: {bullet}")
            destroy(bullet)
        self.pool.clear()

        for bullet in self.active_bullets:
            print(f"Destroying active bullet: {bullet}")
            destroy(bullet)
        self.active_bullets.clear()

        if self.bullet_prefab:
            print(f"Destroying blueprint: {self.bullet_prefab}")
            destroy(self.bullet_prefab)
            self.bullet_prefab = None  # Clear reference

        if self.shoot_sound:
            print(f"Destroying sound: {self.shoot_sound}")
            destroy(self.shoot_sound)
            self.shoot_sound = None  # Clear reference

        print(f"BulletPool destruction for {self.owner} complete.")

class BaseDeployable(ABC):
    '''Contains methods and attributes to help with deploying'''
    @abstractmethod
    def __init__(self, owner:Entity, max_size:int):
        pass

    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def deploy(self):
        pass

class Deployable(BaseDeployable):
    def __init__(self, owner:Entity, max_size:int, deploy_method):
        self.max_size = max_size
        self.items_count = 0
        self.owner = owner
        self.deploy_method = deploy_method

    def add(self):
        if self.items_count >= self.max_size:
            return
        self.items_count += 1

    def deploy(self):
        if self.items_count <= 0:
            return
        self.items_count -= 1
        deployed_object = self.deploy_method()
        return deployed_object

class LandmineDeployer(Deployable):
    def __init__(self, owner:Entity, max_size:int):
        self.owner = owner  
        self.landmine_explosion_animation = SpriteAnimator('assets/animations/landmine_explosion', delay=0.04)     
        def deploy_object():
            return Landmine(owner=self.owner,
                            explosion_animation=self.landmine_explosion_animation, visible=True)
        super().__init__(owner=owner, max_size=max_size, deploy_method=deploy_object)

    def deploy(self):
        if self.items_count <= 0:
            return
        
        deployed_object:Landmine = super().deploy()
        deployed_object.activate()

class BuildingBlockDeployer(Deployable):
    def __init__(self, owner:Entity, max_size:int):
        self.owner = owner
        self.block_deploy_sound = None # TODO: add block deploy sound
        def deploy_object():
            return BuildingBlock(owner=self.owner)
        super().__init__(owner=owner, max_size=max_size, deploy_method=deploy_object)

    def deploy(self):
        if self.items_count <= 0:
            return
    
        deployed_object:BuildingBlock = super().deploy()

        offset_x = math.sin(math.radians(self.owner.rotation_z)) * self.owner.scale_x * 1.5
        offset_y = math.cos(math.radians(self.owner.rotation_z)) * self.owner.scale_y * 1.5
        calculated_position = self.owner.position + Vec3(offset_x, offset_y, 0)

        # Snap the position to the nearest tile
        tile_size = deployed_object.tile_size
        snapped_x = round(calculated_position.x / tile_size) * tile_size
        snapped_y = round(calculated_position.y / tile_size) * tile_size
        snapped_position = Vec3(snapped_x, snapped_y, calculated_position.z)

        deployed_object.position = snapped_position

class Deployables:
    def __init__(self, owner:Entity):
        self.deployables = {"landmine_deployer" : LandmineDeployer(owner=owner, max_size=10),
                            "bb_deployer" : BuildingBlockDeployer(owner=owner, max_size=5) }
        self.deployable_keys = list(self.deployables.keys())
        self.choose_deployable(0)
    
    def choose_deployable(self, index):
        self.chosen_deployable_index = index
        deployable_key = self.deployable_keys[index]  # Access by index from the list
        self.active_deployable = self.deployables[deployable_key]
        print(f"Active deployable: {deployable_key}")
        self.active_deployable.owner.aim_effect.visible = isinstance(self.active_deployable, BuildingBlockDeployer)

    def next_deployable(self):
        self.chosen_deployable_index += 1
        if self.chosen_deployable_index >= len(self.deployable_keys):
            self.chosen_deployable_index = 0
        self.choose_deployable(self.chosen_deployable_index)
    
    def add_landmine(self):
        self.deployables["landmine_deployer"].add()
    
    def add_building_block(self):
        self.deployables["bb_deployer"].add()
    
    def deploy(self):
        return self.active_deployable.deploy()
    
    def recover_from_save(self, save: list):
        for deployable in save:
            name = deployable['name']
            count = deployable['items_count']
            for i in range(count):
                self.deployables[name].add()

class AmmoCatalog:
    def __init__(self, owner:Entity):
        self.owner = owner
        self.game = owner.game
        self.shoot_sound0 = Audio("assets/audio/shoot0.wav", autoplay=False, volume=1.0)
        self.shoot_sound1 = Audio("assets/audio/shoot1.wav", autoplay=False, volume=1.0)
        self.deploy_pool = Deployables(owner=owner)

        texture_bullet0 = load_texture('assets/images/bullet0.png')
        texture_bullet1 = load_texture('assets/images/bullet1.png')
        def reduce_texture_resolution(texture, factor):
            image = Image.open(texture.path)
            image = image.resize((image.width // factor, image.height // factor), Image.LANCZOS)
            return Texture(image)

        texture_bullet0 = reduce_texture_resolution(texture_bullet0, 5)
        texture_bullet1 = reduce_texture_resolution(texture_bullet1, 5)
        self.bullet_pools: List[BulletPool] = []
        bullet = Bullet(owner=owner, model='quad', 
                   texture=texture_bullet0, 
                   color=color.white, scale=(0.1, 0.1), 
                   z= 0.1,
                   visible=False)
        self.bullet_pools.append(BulletPool(owner=owner, 
                                            hit_damage=1,
                                            bullet_speed=10,
                                            pool_size=2,
                                            shoot_sound=self.shoot_sound0,
                                            bullet=bullet))

        bullet = Bullet(owner=owner, model='quad', 
                   texture=texture_bullet1, 
                   color=color.white, 
                   scale=(0.15, 0.15), 
                   z=0.1,
                   visible=False)
        self.bullet_pools.append(BulletPool(owner=owner, 
                                            hit_damage=2,
                                            bullet_speed=5,
                                            pool_size=1,
                                            shoot_sound=self.shoot_sound1,
                                            bullet=bullet))

        self.owner = owner
        self.bullet_effect = None
        self.choose_bullet_pool(0)

    def choose_bullet_pool(self, bullet_pool_index):
        self.bullet_pool : BulletPool = self.bullet_pools[bullet_pool_index]
        self.chosen_bullet_index = bullet_pool_index
        if self.bullet_effect is None:
            self.bullet_effect = BulletEffect(self.owner, self.bullet_pool.texture)
        self.bullet_effect.texture = self.bullet_pool.texture

    def next_bullet_variant(self):
        self.chosen_bullet_index += 1
        if self.chosen_bullet_index >= len(self.bullet_pools):
            self.chosen_bullet_index = 0

        self.choose_bullet_pool(self.chosen_bullet_index)

    def shoot_bullet(self, play_sound=False):
        bullet = self.bullet_pool.take_bullet()
        if bullet is None:
            return
        
        owner = self.owner
        bullet.rotation_z = owner.rotation_z
        offset_x = math.sin(math.radians(owner.rotation_z)) * owner.scale_x * 0.65
        offset_y = math.cos(math.radians(owner.rotation_z)) * owner.scale_y * 0.65
        bullet.position = owner.position + Vec3(offset_x, offset_y, 0)
        bullet.visible = True
        bullet.velocity = Vec3(sin(math.radians(owner.rotation_z)) * self.bullet_pool.bullet_speed,
                            cos(math.radians(owner.rotation_z)) * self.bullet_pool.bullet_speed, 0)  # Set bullet velocity
        bullet.hit_damage = self.bullet_pool.hit_damage
        if play_sound:
            self.bullet_pool.shoot_sound.play()

    def choose_deployable(self, index):
        self.deploy_pool.choose_deployable(index)

    def next_deployable(self):
        self.deploy_pool.next_deployable()

    def deploy_object(self):
        self.deploy_pool.deploy()

    def add_landmine(self):
        self.deploy_pool.add_landmine()
        # add landmine effect to owner
    
    def add_block(self):
        self.deploy_pool.add_building_block()

    def destroy(self):
        for bullet_pool in self.bullet_pools:
            bullet_pool.destroy_bullets()
        destroy(self.bullet_effect)
        destroy(self.shoot_sound0)
        destroy(self.shoot_sound1)
