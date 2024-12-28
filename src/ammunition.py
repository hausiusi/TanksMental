from ursina import *
from src.effects import BulletEffect
from src.types import EntityType

class AmmoCatalog:
    def __init__(self, owner:Entity):
        self.shoot_sound0 = Audio("assets/audio/shoot0.wav", autoplay=False, volume=1.0)
        self.shoot_sound1 = Audio("assets/audio/shoot1.wav", autoplay=False, volume=1.0)
        self.bullets = [
            Entity(model='quad', texture='assets/images/bullet0.png', entity_type=EntityType.BULLET, color=color.yellow, scale=(0.1, 0.1), z=-0.1, visible=False, hit_damage=1, max_bullets=2, speed=10, shoot_sound=self.shoot_sound0),
            Entity(model='quad', texture='assets/images/bullet1.png', entity_type=EntityType.BULLET, color=color.yellow, scale=(0.15, 0.15), z=-0.1, visible=False, hit_damage=2, max_bullets=1, speed=5, shoot_sound=self.shoot_sound1)
        ]

        self.chosen_bullet_index = 0
        self.bullet = self.bullets[self.chosen_bullet_index]
        self.bullet_effect = BulletEffect(owner, self.bullet.texture)


    def choose_bullet(self, bullet_variant):
        self.bullet = self.bullets[bullet_variant]
        self.chosen_bullet_index = bullet_variant
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
            print(f"Object can't shoot the bullet {ex}")