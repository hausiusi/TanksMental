from ursina import*

from .game_save import SaveManager
from .settings import Settings
from .controller import PS4Controller, KeyboardController, BaseController
from .misc.utils import get_files_in_folder,  json_load, get_save_folder, to_resource_name
from .character import IronGuard, TrailBlazer, PlayerCharacter
from .menu.menuentry import Menu
from .widgetry.effects import Outline

class StartMenuElement(Entity):
    def __init__(self, scale=(0.5, 0.5), **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.scale = scale
        self.color = color.white
        self.collider = 'box'
        self.z = -1
        
class BaseControllerAvatar(Entity):
    def __init__(self, controller:BaseController, **kwargs):
        super().__init__(**kwargs)
        self.model = 'quad'
        self.controller = controller
        self.buttons_move_timeout = 0
        self.buttons_move_timeout_max = 0.2
        self.original_position = self.position
        self.original_scale = self.scale
        self._drop_allowed = True
        self._select_allowed = True
        self.selected = False
        
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
        if self.selected:
            return
        
        if ((buttons_state['left'] or buttons_state['right'])
            and self.buttons_move_timeout > self.buttons_move_timeout_max):
            self.buttons_move_timeout = 0
            self.on_controller_moving(self, 'left' if buttons_state['left'] else 'right')

class JoystickAvatar(BaseControllerAvatar):
    def __init__(self, controller:BaseController, **kwargs):
        super().__init__(
            texture='assets/images/joystick.png',
            controller=controller,
            **kwargs)

class KeyboardAvatar(BaseControllerAvatar):
    def __init__(self, controller:BaseController, **kwargs):
        tex = load_texture('images/kb.png')
        print('Loaded texture object:', tex)
        super().__init__(
            texture=tex,
            controller=controller,
            **kwargs)

class TankAvatar(Entity):
    def __init__(self, character:PlayerCharacter, controller_id = -1,  **kwargs):
        super().__init__(
            texture=character.initial_texture,
            **kwargs)
        self.controller_id = controller_id
        self.outline = Outline(self, scale=(1.1, 1.5), position=(0, -0.2, -0.01), color=color.white, visible=False)
        self.character = character

    @property
    def selected(self):
        return self.outline.visible and self.outline.color == color.green

    def select(self):
        self.outline.visible = True
        self.outline.color = color.green

    def mark(self):
        self.outline.visible = True
        self.outline.color = color.white

    def deselect(self):
        self.outline.visible = False
        self.outline.color = color.white

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
        self.controllers = [self.keyboardcontroller, self.ps4controller]
        self.keyboardcontroller.initialize_controller()
        self.ps4controller.initialize_controller()        
        self.controllers_count = len(self.ps4controller.controllers)
        self.init_menus()
        self.show_main_menu()
        
        #self._display_home_menu()

    def init_menus(self):
        # Main Menu
        self.main_menu = Menu(
            controllers=self.controllers,
            title="Main Menu",
            options=["Start", "Continue", "Settings", "Exit"],
            action_map={
                "Exit": self._exit,
            },
        )
        
        files = get_files_in_folder(get_save_folder())

        options = []
        for file in files:
            file_name, _ = file
            options.append(file_name)
        self.continue_menu = Menu(
            controllers=self.controllers,
            title="Continue",
            options=options,
            parent_menu=self.main_menu
        )

        action_map = {}
        for file in files:
            file_name, file_path = file         
            action_map[file_name] = lambda: [self.continue_menu.deactivate(), self._load_saved_game(file_path=file_path)]
        self.continue_menu.action_map = action_map

        self.settings_menu = Menu(
            controllers=self.controllers,
            title="Settings",
            options=["Screen resolution", "Enable friendly fire", "Game difficulty", "Controller settings"],
            parent_menu=self.main_menu
        )

        self.controller_menu = Menu(
            controllers=self.controllers,
            title="Controller Settings",
            options=["Shoot", "Switch bullet", "Switch droppable", "Drop"],
            parent_menu=self.settings_menu
        )

        self.main_menu.action_map.update({
            "Start"   : lambda: [self.main_menu.deactivate(), self._display_setup_new_game(self)],
            "Continue": lambda: [self.main_menu.deactivate(), self.continue_menu.activate()],
            "Settings": lambda: [self.main_menu.deactivate(), self.settings_menu.activate()],
        })

        self.settings_menu.action_map.update({
            "Controller settings": lambda: [self.settings_menu.deactivate(), self.controller_menu.activate()],
        })

        # Pause menu
        self.pause_background = Entity(model='quad', 
                                  scale=(self.settings.horizontal_game_area + 1, self.settings.vertical_game_area + 1), 
                                  color=color.black66,
                                  transparent=True,
                                  z=-0.1,
                                  render_queue=3,
                                  visible=False)
        self.pause_menu = Menu(
        controllers=self.controllers,
        title="Game paused",
        options=["Continue", "Restart level", "Settings", "Return to main menu"],
        )
            
        self.pause_menu.action_map.update({
            "Continue": lambda: self.game.toggle_pause(),
            "Restart level": lambda: [self.game.toggle_pause(), self.game.restart_level()],
            "Return to main menu": lambda: [self.hide_pause_menu(), self.game.toggle_pause(), self.game.total_cleanup(), self.show_main_menu()],
        })

        # Game over menu
        self.game_over_background = Entity(model='quad', 
                                  scale=(self.settings.horizontal_game_area + 1, self.settings.vertical_game_area + 1), 
                                  color=color.black66,
                                  transparent=True,
                                  z=-0.1,
                                  render_queue=3,
                                  visible=False)
        self.game_over_menu = Menu(
            controllers=self.controllers,
            title="Game Over",
            options=["Restart level", "Return to main menu"],
        )
        self.game_over_menu.title_text.color = color.red

        self.game_over_menu.action_map.update({
            "Restart level": lambda: [self.hide_game_over_menu(), self.game.restart_level()],
            "Return to main menu": lambda: [self.hide_game_over_menu(), self.game.total_cleanup(), self.show_main_menu()],
        })

    def show_main_menu(self):
        self.main_menu.activate()

    def show_pause_menu(self):
        self.pause_menu.activate()
        self.pause_background.visible = True

    def hide_pause_menu(self):
        self.pause_menu.deactivate()
        self.pause_background.visible = False

    def show_game_over_menu(self):
        self.game_over_menu.activate()
        self.game_over_background.visible = True
        self.game.over = True

    def hide_game_over_menu(self):
        self.game_over_menu.deactivate()
        self.game_over_background.visible = False
        self.game.over = False
        

    def _load_saved_game(self, file_path):
        print(f"Loading the saved game {file_path}")
        players, level = SaveManager().load_game_from_file(self.game, file_path, self.controllers)
        self.continue_game_callback(os.path.basename(file_path), players, level)

    def _exit(self):
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
            controller_avatar.parent.deselect()
            controller_avatar.parent.controller_id = -1

        controller_avatar.parent = tank_avatar
        tank_avatar.mark()
        tank_avatar.controller_id = controller_avatar.id
        controller_avatar.position = (0, -tank_avatar.scale[1] / 2 + 0.15)
        controller_avatar.scale = (0.7, 0.7)

        print(f'Controller {tank_avatar.controller_id} assigned to tank {tank_avatar.id}')

    def on_controller_selecting(self, controller_avatar):
        controller_avatar.selected = True
        controller_avatar.parent.select() 
        all_are_selected = True
        for tank_avatar in self.tank_avatars:
            if tank_avatar.controller_id != -1 and not tank_avatar.selected:
                all_are_selected = False
                break
        
        if all_are_selected:
            print('All tanks are selected')
            if self.start_new_game_callback:
                self.start_new_game_callback(
                    [_controller_avatar for _controller_avatar in self.controller_avatars if _controller_avatar.selected])

    def on_controller_deselecting(self, controller_avatar):
        if controller_avatar.selected:
            controller_avatar.selected = False
            controller_avatar.parent.mark()
            return
        
        controller_avatar.parent.controller_id = -1
        controller_avatar.parent.deselect()
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
            position = (start_x, -3))
        self.startmenu_elements.append(keyboard)
        self.controller_avatars.append(keyboard)
        # Starting joystick controller from 1 as the first is the keyboard controller        
        for i in range(1, self.controllers_count + 1):
            controller = JoystickAvatar(
                scale=(avatar_width + 0.2, avatar_width + 0.2),
                id = i-1,
                color = self.colors[i-1],
                controller = self.ps4controller,
                on_controller_moving = self.on_controller_moving,
                on_controller_deselecting = self.on_controller_deselecting,
                on_controller_selecting = self.on_controller_selecting,
                position = (start_x + i * distance, -3))
            controller.selected = False
            self.startmenu_elements.append(controller)
            self.controller_avatars.append(controller)
        
        keyboard.selected = False
        
    def _display_tank_avatars(self):
        characters = [
            IronGuard,
            TrailBlazer]
        avatar_width = 1.7
        tanks_count = len(self.colors) * len(characters)
        distance = avatar_width + 0.5
        avatars_span = len(self.colors) * distance
        start_x = -avatars_span / 2 + avatar_width / 2
        start_y = 2.5
        
        for character_index, character in enumerate(characters):
            x_index = 0
            for i in range(len(self.colors)):                
                avatar_id = (len(self.colors) * character_index) + i
                tank_avatar = TankAvatar(
                    character=character,
                    model='quad',
                    id = avatar_id,
                    color=self.colors[i],
                    scale=(avatar_width, avatar_width),
                    position=(start_x + x_index * distance, start_y))
                self.tank_avatars.append(tank_avatar)
                self.startmenu_elements.append(tank_avatar)
                x_index += 1

            start_y -= (avatar_width + 0.9)
    
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
