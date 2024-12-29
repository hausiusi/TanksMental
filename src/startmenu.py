from ursina import*
from src.settings import Settings
from src.controller import PS4Controller, KeyboardController

class StartMenuElement(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.scale = (0.5, 0.5)
        self.color = color.white
        self.collider = 'box'
        self.z = -1

class Outline(Entity):
    def __init__(self, parent_entity, **kwargs):
        super().__init__(
                parent=parent_entity,
                texture='../assets/images/joystick_outline.png',
                model='quad',
                color=color.green,
                scale=(1.1, 1.1),
                position=(0, 0, -0.01),
                visible=True,
                **kwargs
            )
        
    def update_visibility(self, visible):
        self.visible = visible

class ControllerAvatar(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outline = Outline(self)

    def update(self):
        pass
       

class TankAvatar(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            texture='../assets/images/player_tank.png',
            **kwargs)

        # Outline entity
        self.outline = Outline(self)

    # def update(self):
    #    self.outline.visible = self.hovered


class StartMenu:
    def __init__(self):
        self.colors = [
            color.white,
            color.gray,
            color.pink,
            color.green,
        ]
        self.settings = Settings()
        self._display_tank_avatars()
        self.ps4controller = PS4Controller()
        self.keyboardcontroller = KeyboardController()
        self.keyboardcontroller.initialize_controller()
        self.ps4controller.initialize_controller()
        
        pos_x = -0.75
        
        self.controllers_count = len(self.ps4controller.controllers)
        for i in range(self.controllers_count):
            controller = ControllerAvatar(
                texture = '../assets/images/joystick.png', 
                model = 'quad',
                scale=(1.4, 1.4),
                id = i,
                color = self.colors[i],
                controller = self.ps4controller,
                position = (pos_x, 0))
            pos_x += 2.5
            controller.outline.update_visibility(True)

    def _display_tank_avatars(self):
        avatar_width = 1.5
        tanks_count = len(self.colors)
        distance = avatar_width + 0.5
        avatars_span = tanks_count * distance
        start_x = -avatars_span / 2 + avatar_width / 2
        for i in range(tanks_count):
            TankAvatar(model='quad', color=self.colors[i], scale=(avatar_width, avatar_width), position=(start_x + i * distance, 2.5))


if __name__ == '__main__':
    app = Ursina()
    EditorCamera(enabled=True)
    start_menu = StartMenu()
    app.run()