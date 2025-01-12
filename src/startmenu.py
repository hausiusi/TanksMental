from ursina import*

from src.game_save import SaveManager
from src.settings import Settings
from src.controller import PS4Controller, KeyboardController, BaseController
from src.misc.utils import get_files_in_folder, json_load
from src.character import IronGuard, TrailBlazer, PlayerCharacter

class StartMenuElement(Entity):
    def __init__(self, scale=(0.5, 0.5), **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.scale = scale
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
    def __init__(self, character:PlayerCharacter, controller_id = -1,  **kwargs):
        super().__init__(
            texture=character.initial_texture,
            **kwargs)
        self.controller_id = controller_id
        self.outline = Outline(self)
        self.character = character

class HomeMenuItems(Entity):
    def __init__(self, controllers, **kwargs):
        super().__init__(model='quad', color=color.gray, **kwargs)
        self.controllers = controllers
        self.element_switch_delay = 0.3
        self.element_switch_timer = 0
        self.selected_index = -1
        self.selected_item = None
        self.scroll_is_blocked = False

    def select_element(self):
        for menu_item in self.children:
            if menu_item.menu_index == self.selected_index:
                menu_item.color = color.black33
                menu_item.is_selected = True
                self.selected_item = menu_item
            else:
                menu_item.color = color.black
                menu_item.is_selected = False

    def update(self):
        index_limit = len(self.children)
        self.element_switch_timer += time.dt
        if self.element_switch_timer > self.element_switch_delay:            
            self.scroll_is_blocked = False
            self.element_switch_timer = 0

        scroll_requested = False
        for controller in self.controllers:
            for i in range(controller.controllers_count):
                buttons_state = controller.get_buttons_state(i)
                if buttons_state['up']:
                    scroll_requested = True
                    if  not self.scroll_is_blocked:
                        self.selected_index = (self.selected_index - 1) % index_limit
                elif buttons_state['down']:
                    scroll_requested = True
                    if not self.scroll_is_blocked:
                        self.selected_index = (self.selected_index + 1) % index_limit
                elif buttons_state['shoot']:
                    if self.selected_item is not None:
                        self.selected_item.enter_callback(self)
                elif buttons_state['drop']:
                    if self.selected_item is not None:
                        self.selected_item.exit_callback(self)

        if not self.scroll_is_blocked:
            self.select_element()
            self.element_switch_timer = 0

        self.scroll_is_blocked = scroll_requested

class HomeMenuText(Entity):
    def __init__(self, text, enter_callback, menu_index, exit_callback=None, **kwargs):
        super().__init__(model='quad', **kwargs)
        self.enter_callback = enter_callback
        self.exit_callback = exit_callback
        self.is_selected = False        
        self.text_entity = Text(
            parent=self,
            text=text,
            position=(-0.5, 0.1, -0.1),
            color=color.red,
            scale=(5, 10, 5)
        )
        self.menu_index = menu_index
        print(f"Added text {text}")
        print(f"Parent scale: {self.scale}")
        print(f"Text entity scale: {self.text_entity.scale}")
        

class StartMenu:
    def __init__(self, game, start_game_callback=None, continue_game_callback=None):
        self.colors = [
            color.white,
            color.gray,
            color.pink,
            color.green,
        ]
        self.game = game
        self.start_new_game_callback = start_game_callback
        self.continue_game_callback = continue_game_callback
        self.settings = Settings()
        self.startmenu_elements = []
        self.tank_avatars = []
        self.controller_avatars = []
        self.home_menu_selected_id = 0
        self._display_title()
        self.ps4controller = PS4Controller()
        self.keyboardcontroller = KeyboardController()
        self.keyboardcontroller.initialize_controller()
        self.ps4controller.initialize_controller()        
        self.controllers_count = len(self.ps4controller.controllers)
        self._display_home_menu()

    def _load_saved_game(self, sender):
        if not getattr(getattr(sender, 'selected_item', None), 'file_path', None):
            print("Error: no file path has been provided to load the game")
            return
        file_path = sender.selected_item.file_path
        print(f"Loading the saved game {file_path}")
        players, level = SaveManager().load_game(self.game, file_path, [self.ps4controller, self.keyboardcontroller])
        self.continue_game_callback(players, level)

    def _display_continue_game(self, sender):
        self.destroy_startmenu_elements()
        self._display_title()
        print("Continue the saved game")
        self.continue_game_holder = HomeMenuItems(
            controllers=[self.keyboardcontroller, self.ps4controller],
            scale=(5, 5)
            )
        
        files = get_files_in_folder('saves/game')
        for i, file in enumerate(files):
            file_name, file_path = file
            text_entity = HomeMenuText(text=file_name,                         
                                       enter_callback=self._load_saved_game,
                                       menu_index=i,
                                       texture='assets/images/black.png',
                                       parent=self.continue_game_holder,
                                       position=(0, 0.38 - i * 0.25, -0.05),
                                       scale=(0.9, 0.23),
                                       file_path=file_path
                                       )

        self.startmenu_elements.append(self.continue_game_holder)

    def _display_options(self, sender):
        print("Change settings")

    def _exit(self, sender):
        exit()

    def _display_home_menu(self):
        menu_options = {
            "Start Game" : self._display_setup_new_game, 
            "Continue Game" : self._display_continue_game, 
            "Options" : self._display_options,
             "Exit" : self._exit}
        
        self.home_menu_holder = HomeMenuItems(
            controllers=[self.keyboardcontroller, self.ps4controller],
            scale=(5, 5)
            )
        
        for i, (text, callback) in enumerate(menu_options.items()):
            text_entity = HomeMenuText(text=text,                         
                                       enter_callback=callback,
                                       menu_index=i,
                                       texture='assets/images/black.png',
                                       parent=self.home_menu_holder,
                                       position=(0, 0.38 - i * 0.25, -0.05),
                                       scale=(0.9, 0.23),
                                       )
        self.startmenu_elements.append(self.home_menu_holder)


    def _display_setup_new_game(self, sender):
        self.destroy_startmenu_elements()
        self._display_tank_avatars()
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
            if self.start_new_game_callback:
                self.start_new_game_callback(
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
        characters = [
            IronGuard,
            TrailBlazer]
        avatar_width = 1.7
        tanks_count = len(self.colors) * len(characters)
        distance = avatar_width + 0.5
        avatars_span = tanks_count * distance
        start_x = -avatars_span / 2 + avatar_width / 2
        
        for character_index, character in enumerate(characters):
            for i in range(len(self.colors)):
                avatar_id = (len(self.colors) * character_index) + i
                tank_avatar = TankAvatar(
                    character=character,
                    model='quad',
                    id = avatar_id,
                    color=self.colors[i],
                    scale=(avatar_width, avatar_width),
                    position=(start_x + avatar_id * distance, 2.5))
                self.tank_avatars.append(tank_avatar)
                self.startmenu_elements.append(tank_avatar)
    
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
