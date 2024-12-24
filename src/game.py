from ursina import *
from src.settings import Settings
from src.types import CollisionEffect

class Game:
    def __init__(self):
        self.settings = Settings()

        aspect_ratio = window.aspect_ratio  # Aspect ratio of the window
        self.left_edge = -0.5 * aspect_ratio
        self.right_edge = 0.5 * aspect_ratio
        self.no_barrier_entities = []

        self.directions = {
            # Multiple variants for the same directions
            # With numbers
            0  : Vec3(0, 1, 0),  # Up
            1  : Vec3(1, 0, 0),  # Right
            2  : Vec3(0, -1, 0), # Down
            3  : Vec3(-1, 0, 0),  # Left
            # With keyboard letters
            'w': Vec3(0, 1, 0),  # Up
            'd': Vec3(1, 0, 0),  # Right
            's': Vec3(0, -1, 0), # Down
            'a': Vec3(-1, 0, 0),  # Left
        }

        self.max_enemy_tanks = 30

    def update_no_barrier_entities(self):
        self.no_barrier_entities = [e for e in scene.entities if hasattr(e, "collision_effect") and e.collision_effect != CollisionEffect.BARRIER]

    def update_barrier_entities(self):
        self.barrier_entities = [e for e in scene.entities if hasattr(e, "collision_effect") and e.collision_effect == CollisionEffect.BARRIER]

    def show_game_over(self):
        background = Entity(
        model='quad',
        scale=(1.5, 1),             
        color=color.black66,        
        position=(0, 0)             
        )
        game_over_text = Text(
        text='Game Over',            
        scale=2,                    
        position=(0, 0),            
        color=color.red,            
        origin=(0, 0)
        )
        return background, game_over_text

    def is_on_screen(self, entity: Entity):
        """Check if an entity is within fixed screen bounds."""
        position = entity.position
        return self.is_position_on_screen(position)

    def is_position_on_screen(self, position):
        return (
        self.settings.screen_left <= position.x <= self.settings.screen_right and
        self.settings.screen_bottom <= position.y <= self.settings.screen_top
        )

    def get_collided_entity(self, entity:Entity, direction:Vec3, distance:float):
        """Gets the entity that was collided with passed entity"""
        try:
            ray = raycast(entity.position, direction, ignore=[entity], distance=distance, debug=False)
            if ray.hit:
                return ray.entity
        except Exception as ex:
            pass
        return None
    
    def get_collided_entity_at_pos(self, entity, position, direction : Vec3, distance: float):
        try:
            ray = raycast(position, direction, ignore=[entity], distance=distance, debug=False)
            if ray.hit:
                return ray.entity
        except Exception as ex:
            pass
        return None
    
    def get_collided_entities_at_position(self, entity: Entity, position):
        """
        This method is a working alternative and workaround for raycasting that doesn't work with
        entities that are already on NOT barrier surface
        """
        collided_entities = []

        # Save the original position of the entity
        original_position = entity.position

        # Temporarily move the entity to the desired position
        entity.position = position

        # Check for collisions at the new position
        for e in scene.entities:
            if entity != e and e.collider:
                if entity.intersects(e).hit:
                    collided_entities.append(e)

        # Restore the entity's original position
        entity.position = original_position

        return collided_entities
    
    def get_collided_barriers(self, entity : Entity):
        colliding_entities = []
        for e in self.barrier_entities:
            if e == None:
                self.barrier_entities.remove(e)
                continue
            if entity.intersects(e):
                colliding_entities.append(e)

        return colliding_entities

