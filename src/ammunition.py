from ursina import *
from src.effects import BulletEffect
from src.enums import EntityType, CollisionEffect
from src.timer import Timer
from PIL import Image

class Landmine(Entity):
    def __init__(self, owner, **kwargs):
        super().__init__(
            model='quad', 
            texture='assets/images/landmine.png', 
            entity_type=EntityType.LANDMINE,
            collider='box',
            collision_effect=CollisionEffect.NO_EFFECT,
            color=color.white, 
            scale=(0.3, 0.3), 
            z=0, 
            visible=True, 
            effect_strength=50,
            **kwargs
            )
        self.owner = owner
        self.activation_timer = Timer(3, 1, lambda _: None, self.activate)
        self.position = owner.position
    
    def activate(self):
        def _activate():
            self.collision_effect = CollisionEffect.DAMAGE_EXPLOSION
            self.color = color.red
            print("landmine activated")
        self.activation_timer.end_callback = _activate
        self.activation_timer.start()

    def update(self):
        self.activation_timer.update()

class AmmoCatalog:
    def __init__(self, owner:Entity):
        self.shoot_sound0 = Audio("assets/audio/shoot0.wav", autoplay=False, volume=1.0)
        self.shoot_sound1 = Audio("assets/audio/shoot1.wav", autoplay=False, volume=1.0)
        self.landmine_deploy_sound = Audio('assets/audio/landmine_drop.ogg', autoplay=False, volume=1.0)
        self.landmines_count = 0
        self.landmine_activation_timer = Timer(3, 1, lambda _: None, lambda: None)  

        texture_bullet0 = load_texture('assets/images/bullet0.png')
        texture_bullet1 = load_texture('assets/images/bullet1.png')
        def reduce_texture_resolution(texture, factor):
            image = Image.open(texture.path)
            image = image.resize((image.width // factor, image.height // factor), Image.LANCZOS)
            return Texture(image)

        texture_bullet0 = reduce_texture_resolution(texture_bullet0, 5)
        texture_bullet1 = reduce_texture_resolution(texture_bullet1, 5)
        self.bullets = [
            Entity(model='quad', 
                   texture=texture_bullet0,
                   entity_type=EntityType.BULLET, 
                   color=color.yellow, scale=(0.1, 0.1), 
                   z=-0.1, 
                   visible=False, 
                   hit_damage=1, 
                   max_bullets=2, 
                   speed=10, 
                   shoot_sound=self.shoot_sound0),
            Entity(model='quad', 
                   texture=texture_bullet1, 
                   entity_type=EntityType.BULLET, 
                   color=color.yellow, 
                   scale=(0.15, 0.15), 
                   z=-0.1, 
                   visible=False, 
                   hit_damage=2, 
                   max_bullets=1, 
                   speed=5, 
                   shoot_sound=self.shoot_sound1)
        ]

        self.owner = owner
        self.bullet_effect = None
        self.choose_bullet(0)

    def choose_bullet(self, bullet_variant):
        self.bullet = self.bullets[bullet_variant]
        self.chosen_bullet_index = bullet_variant
        if self.bullet_effect is None:
            self.bullet_effect = BulletEffect(self.owner, self.bullet.texture)
        self.bullet_effect.texture = self.bullet.texture

    def next_bullet_variant(self):
        self.chosen_bullet_index += 1
        if self.chosen_bullet_index >= len(self.bullets):
            self.chosen_bullet_index = 0

        self.choose_bullet(self.chosen_bullet_index)

    def shoot_bullet(self, owner:Entity, play_sound=False):
        try:
            bullet = duplicate(self.bullet)  
            bullet.rotation_z = owner.rotation_z
            offset_x = math.sin(math.radians(owner.rotation_z)) * owner.scale_x * 0.65  # Move 0.5 units forward in x
            offset_y = math.cos(math.radians(owner.rotation_z)) * owner.scale_y * 0.65 # Move 0.5 units forward in y
            bullet.position = owner.position + Vec3(offset_x, offset_y, 0)
            bullet.visible = True 
            bullet.velocity = Vec3(sin(math.radians(owner.rotation_z)) * owner.ammunition.bullet.speed,
                                cos(math.radians(owner.rotation_z)) * owner.ammunition.bullet.speed, 0)  # Set bullet velocity
            bullet.owner = owner
            owner.bullets_on_screen += 1
            bullet.hit_damage = self.bullet.hit_damage
            if play_sound:
                self.bullet.shoot_sound.play()
        except Exception as ex:
            print(f"{owner} Object can't shoot the bullet {ex}")

    def add_landmine(self, owner:Entity):
        self.landmines_count += 1
        # add landmine effect to owner

    def subtract_landmine(self, owner:Entity):
        self.landmines_count -= 1
        if self.landmines_count <= 0:
            self.landmines_count = 0
            # remove landmine effect from owner

    def deploy_landmine(self, owner:Entity, play_sound=False):
        if self.landmines_count == 0:
            return
        
        self.subtract_landmine(owner)
        landmine = Landmine(owner)
        if play_sound:
            self.landmine_deploy_sound.play()
        landmine.activate()
