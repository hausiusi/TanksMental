from ursina import *


class Menu(Entity):
    _button_is_blocked = False
    _scroll_is_blocked = False

    def __init__(self, controllers, title, options, parent_menu=None, action_map=None, **kwargs):
        super().__init__(**kwargs)
        self.controllers = controllers
        self.title = title
        self.options = options
        self.parent_menu = parent_menu
        self.action_map = action_map or {}
        self.highlight_index = 0
        self.active = False
        self.text_elements = []
        self.element_switch_delay = 0.3
        self.element_switch_timer = 0

        # Display Title
        self.title_text = Text(text=title, scale=2, position=(-0.13, 0.4), visible=False)

        # Display Options
        for i, option in enumerate(self.options):
            text = Text(
                text=option,
                position=(0, 0.3 - (i * 0.4)),
                origin=(0, 0),
                parent=self,
                scale=(25, 12),
                visible=False
            )
            self.text_elements.append(text)

    def activate(self):
        """Activate this menu."""
        self.active = True
        self.title_text.visible = True
        for text in self.text_elements:
            text.visible = True

    def deactivate(self):
        """Deactivate this menu."""
        self.active = False
        self.title_text.visible = False
        for text in self.text_elements:
            text.visible = False

    def update(self):
        """Update the menu interactions."""
        if not self.active:
            return        

        # Navigation
        scroll_requested = False
        button_pressed = False
        index_limit = len(self.options)
        for controller in self.controllers:
            for i in range(controller.controllers_count):
                buttons_state = controller.get_buttons_state(i)
                if buttons_state['up']:
                    scroll_requested = True
                    if  not Menu._scroll_is_blocked:
                        self.highlight_index = (self.highlight_index - 1) % index_limit
                elif buttons_state['down']:
                    scroll_requested = True
                    if not Menu._scroll_is_blocked:
                        self.highlight_index = (self.highlight_index + 1) % index_limit
                elif buttons_state['shoot']:
                    button_pressed = True
                    if not self._button_is_blocked:
                        selected_option = self.options[self.highlight_index]
                        action = self.action_map.get(selected_option, None)
                        if callable(action):
                            action()  # Perform the assigned action
                elif buttons_state['drop'] and self.parent_menu:
                    button_pressed = True
                    if not self._button_is_blocked:
                        self.deactivate()
                        self.parent_menu.activate()

        # Highlight Selection
        if not Menu._scroll_is_blocked:
            for i, text in enumerate(self.text_elements):
                text.color = color.white if i != self.highlight_index else color.azure
            self.element_switch_timer = 0            

        Menu._scroll_is_blocked = scroll_requested
        Menu._button_is_blocked = button_pressed
