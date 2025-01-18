from ursina import*

from src.game_save import SaveManager
from src.settings import Settings
from src.controller import PS4Controller, KeyboardController, BaseController
from src.misc.utils import get_files_in_folder, json_load
from src.character import IronGuard, TrailBlazer, PlayerCharacter
from src.menu.menuentry import Menu

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
        self.keyboardcontroller = KeyboardController()
        self.ps4controller = PS4Controller()
        self.keyboardcontroller.initialize_controller()
        self.ps4controller.initialize_controller()        
        self.controllers_count = len(self.ps4controller.controllers)
        self.init_menus()
        
        #self._display_home_menu()

    def init_menus(self):
        # Main Menu Actions
        main_menu = Menu(
            controllers=[self.keyboardcontroller, self.ps4controller],
            title="Main Menu",
            options=["Start", "Continue", "Settings", "Exit"],
            action_map={
                "Exit": self._exit,
            },
        )
        
        files = get_files_in_folder('saves/game')

        options = []
        for file in files:
            file_name, _ = file
            options.append(file_name)
        continue_menu = Menu(
            controllers=[self.keyboardcontroller, self.ps4controller],
            title="Continue",
            options=options,
            parent_menu=main_menu
        )

        action_map = {}
        for file in files:
            file_name, file_path = file         
            action_map[file_name] = lambda: [continue_menu.deactivate(), self._load_saved_game(file_path=file_path)]
        continue_menu.action_map = action_map

        settings_menu = Menu(
            controllers=[self.keyboardcontroller, self.ps4controller],
            title="Settings",
            options=["Screen resolution", "Enable friendly fire", "Game difficulty", "Controller settings"],
            parent_menu=main_menu
        )

        controller_menu = Menu(
            controllers=[self.keyboardcontroller, self.ps4controller],
            title="Controller Settings",
            options=["Shoot", "Switch bullet", "Switch droppable", "Drop"],
            parent_menu=settings_menu
        )

        # Link Submenus to Actions
        main_menu.action_map.update({
            "Start"   : lambda: [main_menu.deactivate(), self._display_setup_new_game(self)],
            "Continue": lambda: [main_menu.deactivate(), continue_menu.activate()],
            "Settings": lambda: [main_menu.deactivate(), settings_menu.activate()],
        })

        settings_menu.action_map.update({
            "Controller settings": lambda: [settings_menu.deactivate(), controller_menu.activate()],
        })

        # Activate Main Menu
        main_menu.activate()

    def _load_saved_game(self, file_path):
        print(f"Loading the saved game {file_path}")
        players, level = SaveManager().load_game(self.game, file_path, [self.keyboardcontroller, self.ps4controller])
        self.continue_game_callback(os.path.basename(file_path), players, level)

    def _exit(self, sender):
        exit()

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
        keyboard = KeyboardAvatar(
            scale=(avatar_width + 0.2, avatar_width + 0.2),
            id = 0, # The keyboard is the first controller always
            color = color.white,
            controller = self.keyboardcontroller,
            on_controller_moving = self.on_controller_moving,
            on_controller_deselecting = self.on_controller_deselecting,
            on_controller_selecting = self.on_controller_selecting,
            position = (start_x, -1))
        self.startmenu_elements.append(keyboard)
        self.controller_avatars.append(keyboard)
        # Starting joystick controller from 1 as the first is the keyboard controller        
        for i in range(1, self.controllers_count + 1):
            controller = ControllerAvatar(
                scale=(avatar_width + 0.2, avatar_width + 0.2),
                id = i-1,
                color = self.colors[i-1],
                controller = self.ps4controller,
                on_controller_moving = self.on_controller_moving,
                on_controller_deselecting = self.on_controller_deselecting,
                on_controller_selecting = self.on_controller_selecting,
                position = (start_x + i * distance, -1))
            controller.outline.visible = False
            self.startmenu_elements.append(controller)
            self.controller_avatars.append(controller)

        pos_x = start_x + self.controllers_count * distance
        
        keyboard.outline.visible = False
        

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
