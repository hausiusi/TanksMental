from ursina import *

class WetEffect(Entity):
    def __init__(self, parent_entity=None, **kwargs):
        super().__init__(
            parent=parent_entity,
            texture='assets/images/wet_effect.png',
            model='quad',
            color=color.Color(1, 1, 1, 0.5),
            z=-0.01,
            visible=False,
            **kwargs
        )

class FireEffect(Entity):
    def __init__(self, parent_entity=None, **kwargs):
        super().__init__(
            parent=parent_entity,
            texture='assets/images/fire_effect.png',
            model='quad',
            color=color.Color(1, 1, 1, 0.5),
            z=-0.01,
            visible=False,
            **kwargs
        )

class BulletEffect(Entity):
    def __init__(self, parent_entity=None, texture="", **kwargs):
        super().__init__(
            parent=parent_entity,
            texture=texture,
            model='quad',
            color=color.Color(1, 1, 1, 1),
            scale=(0.1, 0.1),
            position=(0, -0.2),
            z=-0.01,
            visible=True,
            **kwargs
        )