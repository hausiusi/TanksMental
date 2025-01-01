from ursina import*
if __name__ == '__main__':
    from settings import Settings
    from controller import PS4Controller, KeyboardController, BaseController
else:
    from src.settings import Settings
    from src.controller import PS4Controller, KeyboardController, BaseController

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
                visible=False,
                **kwargs
            )
        
class BaseControllerAvatar(Entity):
    def __init__(self, controller:BaseController, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.controller = controller
        self.outline = Outline(self)
        self.buttons_move_timeout = 0
        self.buttons_move_timeout_max = 0.2
        self.original_position = self.position
        self.original_scale = self.scale
        self._drop_allowed = True
        self._select_allowed = True
        
    def update(self):
        self.buttons_move_timeout += time.dt
        buttons_state = self.controller.get_buttons_state(self.id)
        if buttons_state['drop'] and self._drop_allowed:
            if self.parent is not scene:
                self.on_controller_deselecting(self)
                self._drop_allowed = False
        elif not buttons_state['drop']:
            self._drop_allowed = True

        if buttons_state['shoot'] and self._select_allowed:
            if self.parent is not scene:
                self.on_controller_selecting(self)
                self._select_allowed = False
        elif not buttons_state['shoot']:
            self._select_allowed = True
        
        # While the controller is selected, it can't move
        if self.outline.visible:
            return
        
        if ((buttons_state['left'] or buttons_state['right'])
            and self.buttons_move_timeout > self.buttons_move_timeout_max):
            self.buttons_move_timeout = 0
            self.on_controller_moving(self, 'left' if buttons_state['left'] else 'right')


class ControllerAvatar(BaseControllerAvatar):
    def __init__(self, controller:BaseController, **kwargs):
        super().__init__(
            texture='../assets/images/joystick.png',
            controller=controller,
            **kwargs)

class KeyboardAvatar(BaseControllerAvatar):
    def __init__(self, controller:BaseController, **kwargs):
        super().__init__(
            texture='../assets/images/keyboard.png',
            controller=controller,
            **kwargs)

class TankAvatar(Entity):
    def __init__(self, controller_id = -1, **kwargs):
        super().__init__(
            texture='../assets/images/player_tank.png',
            **kwargs)
        self.controller_id = controller_id
        self.outline = Outline(self)

class StartMenu:
    def __init__(self, all_tanks_selected_callback=None):
        self.colors = [
            color.white,
            color.gray,
            color.pink,
            color.green,
        ]
        self.all_tanks_selected_callback = all_tanks_selected_callback
        self.settings = Settings()
        self.startmenu_elements = []
        self.tank_avatars = []
        self.controller_avatars = []
        self._display_title()
        self._display_tank_avatars()
        self.ps4controller = PS4Controller()
        self.keyboardcontroller = KeyboardController()
        self.keyboardcontroller.initialize_controller()
        self.ps4controller.initialize_controller()        
        self.controllers_count = len(self.ps4controller.controllers)
        self._display_controller_avatars()

    def find_next_tank_avatar(self, parent_id):
        r = self._get_circular_range(0, len(self.tank_avatars), parent_id)
        for i in r:
            tank_avatar = self.tank_avatars[i]
            if tank_avatar.controller_id == -1:
                return tank_avatar
        
        print('No tank avatar available')
        return tank_avatar
    
    def destroy_startmenu_elements(self):
        for element in self.startmenu_elements:
            destroy(element)
        self.startmenu_elements.clear()
            
    def find_previous_tank_avatar(self, parent_id):
        r = self._get_circular_range(0, len(self.tank_avatars), parent_id, reverse=True)
        for i in r:
            tank_avatar = self.tank_avatars[i]
            if tank_avatar.controller_id == -1:
                return tank_avatar
        
        print('No tank avatar available')
        return tank_avatar           

    def on_controller_moving(self, controller_avatar, direction):
        print(f'Controller moved {direction}')
        if controller_avatar.parent is scene:
            parent_id = -1
        else:
            parent_id = controller_avatar.parent.id

        if direction == 'left':
            tank_avatar = self.find_previous_tank_avatar(parent_id)
        elif direction == 'right':
            tank_avatar = self.find_next_tank_avatar(parent_id)

        # Reset the controller ID for the previous tank avatar if it was assigned
        if controller_avatar.parent is not scene:
            controller_avatar.parent.controller_id = -1

        controller_avatar.parent = tank_avatar
        tank_avatar.controller_id = controller_avatar.id
        controller_avatar.position = (0, -tank_avatar.scale[1] / 2 - 0.1)
        controller_avatar.scale = (0.7, 0.7)

        print(f'Controller {tank_avatar.controller_id} assigned to tank {tank_avatar.id}')

    def on_controller_selecting(self, controller_avatar):
        controller_avatar.outline.visible = True
        controller_avatar.parent.outline.visible = True
        all_are_selected = True
        for tank_avatar in self.tank_avatars:
            if tank_avatar.controller_id != -1 and not tank_avatar.outline.visible:
                all_are_selected = False
                break
        
        if all_are_selected:
            print('All tanks are selected')
            if self.all_tanks_selected_callback:
                self.all_tanks_selected_callback(
                    [_controller_avatar for _controller_avatar in self.controller_avatars if _controller_avatar.outline.visible])

    def on_controller_deselecting(self, controller_avatar):
        if controller_avatar.outline.visible:
            controller_avatar.outline.visible = False
            controller_avatar.parent.outline.visible = False
            return
        
        controller_avatar.parent.controller_id = -1
        controller_avatar.parent = scene
        controller_avatar.position = controller_avatar.original_position    
        controller_avatar.scale = controller_avatar.original_scale    

    def _display_controller_avatars(self):
        avatar_width = 1.2
        distance = avatar_width + 0.5
        avatar_span = (1 + self.controllers_count) * distance 
        start_x = -avatar_span / 2 + avatar_width / 2        
        for i in range(self.controllers_count):
            controller = ControllerAvatar(
                scale=(avatar_width + 0.2, avatar_width + 0.2),
                id = i,
                color = self.colors[i],
                controller = self.ps4controller,
                on_controller_moving = self.on_controller_moving,
                on_controller_deselecting = self.on_controller_deselecting,
                on_controller_selecting = self.on_controller_selecting,
                position = (start_x + i * distance, -1))
            controller.outline.visible = False
            self.startmenu_elements.append(controller)
            self.controller_avatars.append(controller)

        pos_x = start_x + self.controllers_count * distance
        keyboard = KeyboardAvatar(
            scale=(avatar_width + 0.2, avatar_width + 0.2),
            id = self.controllers_count, # The keyboard is the last controller always
            color = color.white,
            controller = self.keyboardcontroller,
            on_controller_moving = self.on_controller_moving,
            on_controller_deselecting = self.on_controller_deselecting,
            on_controller_selecting = self.on_controller_selecting,
            position = (pos_x, -1))
        keyboard.outline.visible = False
        self.startmenu_elements.append(keyboard)
        self.controller_avatars.append(keyboard)

    def _display_tank_avatars(self):
        avatar_width = 1.7
        tanks_count = len(self.colors)
        distance = avatar_width + 0.5
        avatars_span = tanks_count * distance
        start_x = -avatars_span / 2 + avatar_width / 2
        
        for i in range(tanks_count):
            self.tank_avatars.append(TankAvatar(
                model='quad',
                id = i,
                color=self.colors[i],
                scale=(avatar_width, avatar_width),
                position=(start_x + i * distance, 2.5))
            )
            self.startmenu_elements.append(self.tank_avatars[i])
    
    def _display_title(self):
        self.title = Text(
            text='TanksMental',
            scale=2,
            position=(0, 0.45),
            color=color.red,
            origin=(0, 0))
        self.startmenu_elements.append(self.title)

    @staticmethod
    def _get_circular_range(start, stop, index, reverse=False):
        length = stop - start
        index = (index - start) % length  # Adjust index to fit within the range
        
        if reverse:
            return [(start + (index - i) % length) for i in range(length)]
        else:
            return [(start + (i + index) % length) for i in range(length)]


if __name__ == '__main__':
    app = Ursina()
    EditorCamera(enabled=True)
    start_menu = StartMenu()
    app.run()