from ursina import *
from src.widgetry.effects import BulletEffect
from src.enums import EntityType, CollisionEffect
from src.misc.timer import Timer
from src.misc.spranimator import SpriteAnimator
from PIL import Image
from abc import ABC, abstractmethod

class Landmine(Entity):
    def __init__(self, owner, activation_sound, explosion_sound, explosion_animation : SpriteAnimator, **kwargs):
        super().__init__(
            model='quad', 
            texture='assets/images/landmine.png',            
            collider='box',            
            color=color.white, 
            scale=(0.3, 0.3), 
            z=0,             
            **kwargs
            )
        self.effect_strength=50
        self.entity_type=EntityType.LANDMINE
        self.collision_effect=CollisionEffect.NO_EFFECT
        self.explosion_animation = explosion_animation
        self.activation_sound = activation_sound
        self.explosion_sound = explosion_sound
        self.owner = owner
        self.activation_timer = Timer(3, 1, lambda _: None, self.activate)
        self.position = owner.position
    
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

    def _destroy(self):
        destroy(self)

    def explode(self):
        self.explosion_sound.play()
        self.explosion_animation.animate(self, self._destroy)


class Bullet(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entity_type=EntityType.BULLET

class BulletPool:
    def __init__(self, owner, pool_size, hit_damage, bullet_speed, shoot_sound, bullet):
        if pool_size < 1:
            raise Exception("BulletPool object must have size 1 or more")
        self.texture = bullet.texture
        self.bullet_blueprint = bullet
        self.pool = [duplicate(bullet) for _ in range(pool_size)]
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
                self.pool.append(duplicate(self.bullet_blueprint))
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
        self.active_bullets.remove(bullet)
        self.pool.append(bullet)
        bullet.visible = False

    def increase_pool(self):
        self.pool.append(duplicate(self.pool[0]))

    def destroy_bullets(self):
        for bullet in self.pool:
            destroy(bullet)
        self.pool.clear()
        for bullet in self.active_bullets:
            destroy(bullet)
        self.active_bullets.clear()

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
    def __init__(self, owner:Entity, max_size:int, deploy_method, deploy_sound:Audio):
        self.max_size = max_size
        self.items_count = 0
        self.owner = owner
        self.deploy_method = deploy_method
        self.deploy_sound = deploy_sound

    def add(self):
        if self.items_count >= self.max_size:
            return
        self.items_count += 1

    def deploy(self):
        if self.items_count <= 0:
            return
        self.items_count -= 1
        deployed_object = self.deploy_method()
        self.deploy_sound.play()
        return deployed_object

class LandmineDeployer(Deployable):
    def __init__(self, owner:Entity, max_size:int):
        self.owner = owner
        self.landmine_deploy_sound = Audio('assets/audio/landmine_drop.ogg', autoplay=False, volume=1.0)
        self.landmine_activation_sound = Audio('assets/audio/landmine_activation.ogg', autoplay=False, volume=0.2)
        self.landmine_explosion_sound = Audio('assets/audio/landmine_explosion.ogg', autoplay=False, volume=1.0)
        self.landmine_explosion_animation = SpriteAnimator('assets/animations/landmine_explosion', delay=0.04)
        def deploy_object():
            return Landmine(owner=self.owner, 
                            activation_sound=self.landmine_activation_sound,                             
                            explosion_sound=self.landmine_explosion_sound, 
                            explosion_animation=self.landmine_explosion_animation, visible=True)
        super().__init__(owner=owner, max_size=max_size, deploy_method=deploy_object, deploy_sound=self.landmine_deploy_sound)

    def deploy(self):
        if self.items_count <= 0:
            return
        
        deployed_object:Landmine = super().deploy()
        deployed_object.activate()


class AmmoCatalog:
    def __init__(self, owner:Entity):
        self.owner = owner
        self.game = owner.game
        self.shoot_sound0 = Audio("assets/audio/shoot0.wav", autoplay=False, volume=1.0)
        self.shoot_sound1 = Audio("assets/audio/shoot1.wav", autoplay=False, volume=1.0)
        self.landmine_deployer = LandmineDeployer(owner=owner, max_size=10)

        texture_bullet0 = load_texture('assets/images/bullet0.png')
        texture_bullet1 = load_texture('assets/images/bullet1.png')
        def reduce_texture_resolution(texture, factor):
            image = Image.open(texture.path)
            image = image.resize((image.width // factor, image.height // factor), Image.LANCZOS)
            return Texture(image)

        texture_bullet0 = reduce_texture_resolution(texture_bullet0, 5)
        texture_bullet1 = reduce_texture_resolution(texture_bullet1, 5)
        self.bullet_pools = []
        bullet = Bullet(owner=owner, model='quad', 
                   texture=texture_bullet0, 
                   color=color.white, scale=(0.1, 0.1), 
                   z=-0.1, 
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
                   z=-0.1,
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

    @property
    def landmines_count(self):
        return self.landmine_deployer.items_count

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

    def add_landmine(self, owner:Entity):
        self.landmine_deployer.add()
        # add landmine effect to owner

    def deploy_landmine(self, play_sound=False):
        self.landmine_deployer.deploy()

    def add_block(self, owner:Entity):
        pass
