from ursina import window

class Settings:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        # Screen settings
        self.screen_left = -7
        self.screen_right = 7
        self.screen_top = 5
        self.screen_bottom = -5
        self.horizontal_game_area = self.screen_right - self.screen_left
        self.vertical_game_area = self.screen_top - self.screen_bottom
        self.camera_fov = 12
        self.fullscreen = True
        self.aspect_ratio = window.aspect_ratio
        self.horizontal_span = self.camera_fov * self.aspect_ratio
        self.vertical_span = self.camera_fov
        self.window_size = (1920, 1080)
        
        # Player stats
        self.player_icon_scale = 0.4

        # Objects
        self.tile_size = 1
