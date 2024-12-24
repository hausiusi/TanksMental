from ursina import *

class Bullet:
    def __init__(self):
        self.bullets = [
            Entity(model='quad', texture='assets/images/bullet0.png', color=color.yellow, scale=(0.1, 0.1), z=-0.1, visible=False, hit_damage=1, max_bullets=2),
            Entity(model='quad', texture='assets/images/bullet1.png', color=color.yellow, scale=(0.15, 0.15), z=-0.1, visible=False, hit_damage=2, max_bullets=1)
        ]

        self.chosen_bullet = 0
        self.bullet = self.bullets[self.chosen_bullet]

    def choose_bullet(self, bullet_variant):
        self.bullet = self.bullets[bullet_variant]
        self.chosen_bullet = bullet_variant

    def next_bullet_variant(self):
        self.chosen_bullet += 1
        if self.chosen_bullet >= len(self.bullets):
            self.chosen_bullet = 0

        self.choose_bullet(self.chosen_bullet)

    def shoot_bullet(self, owner:Entity):
        try:
            bullet = duplicate(self.bullet)  
            bullet.rotation_z = owner.rotation_z
            offset_x = math.sin(math.radians(owner.rotation_z)) * 0.5  # Move 0.5 units forward in x
            offset_y = math.cos(math.radians(owner.rotation_z)) * 0.5  # Move 0.5 units forward in y
            bullet.position = owner.position + Vec3(offset_x, offset_y, 0)
            bullet.visible = True 
            bullet.velocity = Vec3(sin(math.radians(owner.rotation_z)) * owner.bullet_speed,
                                cos(math.radians(owner.rotation_z)) * owner.bullet_speed, 0)  # Set bullet velocity
            bullet.owner = owner
            owner.bullets_on_screen += 1
            bullet.hit_damage = self.bullet.hit_damage 
        except Exception as ex:
            print(f"Object can't shoot the bullet {ex}")