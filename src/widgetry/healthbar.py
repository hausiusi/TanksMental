from ursina import *

class HealthBar(Entity):
    def __init__(self, max_health, current_health, parent_entity=None, initial_scale_x=0.4, **kwargs):
        self.initial_scale_x = initial_scale_x
        super().__init__(
            parent=parent_entity,
            model='quad',
            color=color.green,
            scale=(self.initial_scale_x, 0.02, 1),
            position=(0, -0.4, -0.01),  # Adjust z-position slightly forward
            #ignore_scale=True,         # Ignore parent scaling
            **kwargs
        )
        self.max_health = max_health
        self.current_health = current_health

    def update_health(self, new_health):
        self.current_health = max(0, min(new_health, self.max_health))
        self.scale_x = self.initial_scale_x * (self.current_health / self.max_health)
        self.color = color.green if self.current_health > self.max_health * 0.3 else color.red