from ursina import *
from src.enums import EntityType, DropEffect
from src.widgetry.effects import Outline
from src.misc.timer import Timer
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
        super().__init__(color=color.white50, texture="assets/images/gun.png", drop_effect=DropEffect.MISSILE_DAMAGE_INCREASE, **kwargs)
        outline=Outline(parent_entity=self, scale=(1.1, 1.1))

class FastBulletDrop(SupplyDrop):
    def __init__(self, **kwargs):
        super().__init__(color=color.white50, texture="assets/images/fast_bullet.png", drop_effect=DropEffect.MISSILE_SPEED_INCREASE, **kwargs)
        outline=Outline(parent_entity=self, scale=(1.1, 1.1))

class MachineGunDrop(SupplyDrop):
    def __init__(self, **kwargs):
        super().__init__(color=color.white50, texture="assets/images/machine_gun.png", drop_effect=DropEffect.MISSILE_RATE_INCREASE, **kwargs)
        outline=Outline(parent_entity=self, scale=(1.1, 1.1))

class LandmineDrop(SupplyDrop):
    def __init__(self, **kwargs):
        super().__init__(color=color.white50, texture="assets/images/landmine.png", drop_effect=DropEffect.LANDMINE_PICK, **kwargs)
        outline=Outline(parent_entity=self, scale=(1.1, 1.1))

class BuildingBlockDrop(SupplyDrop):
    def __init__(self, **kwargs):
        super().__init__(color=color.white50, texture="assets/images/white_wall.png", drop_effect=DropEffect.BUILDING_BLOCK_PICK, **kwargs)
        outline=Outline(parent_entity=self, scale=(1.1, 1.1))

def randomize_drop(position, game):
    drop_list = [
        GunDrop,
        FastBulletDrop,
        MachineGunDrop,
        LandmineDrop,
        BuildingBlockDrop,
    ]
    
    entity = random.choice(drop_list)(position=position)
    entity.on_destroy = lambda e=entity: game.remove_terrain_entity(e)
    game.terrain_entities.append(entity)
    