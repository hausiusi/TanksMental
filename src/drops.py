from ursina import *
from src.types import EntityType, DropEffect
from src.timer import Timer
import random

class SupplyDrop(Entity):
    def __init__(self, **kwargs):
        super().__init__(entity_type=EntityType.SUPPLY_DROP,
                         model='quad',
                         scale=(0.7, 0.7),
                         collider='box',
                         **kwargs)
        
        self.destroy_timer = Timer(7, 1, lambda _: None, self.self_destroy)
        self.destroy_timer.start()

    def update(self):
        self.destroy_timer.update()


    def self_destroy(self):
        destroy(self)

class GunDrop(SupplyDrop):
    def __init__(self, **kwargs):
        super().__init__(color=color.white, texture="assets/images/gun.png", drop_effect=DropEffect.MISSILE_DAMAGE_INCREASE, **kwargs)

class FastBulletDrop(SupplyDrop):
    def __init__(self, **kwargs):
        super().__init__(color=color.white, texture="assets/images/fast_bullet.png", drop_effect=DropEffect.MISSILE_SPEED_INCREASE, **kwargs)

class MachineGunDrop(SupplyDrop):
    def __init__(self, **kwargs):
        super().__init__(color=color.white, texture="assets/images/machine_gun.png", drop_effect=DropEffect.MISSILE_RATE_INCREASE, **kwargs)


def randomize_drop(position):
    drop_list = [
        GunDrop,
        FastBulletDrop,
        MachineGunDrop
    ]

    random.choice(drop_list)(position=position)
    