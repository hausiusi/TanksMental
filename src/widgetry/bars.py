from ursina import *

class BaseBar(Entity):
    def __init__(self,  max, count, icon_scale=(0.15, 0.15), bar_scale=(1, 0.1), **kwargs):
        super().__init__(self, **kwargs)
        self.max = max
        self.ammos = []

        self.icon = Entity(
            parent=self,
            model='quad',
            texture=self.texture,
            scale=icon_scale,
        )

        self.bar_container = Entity(
                parent=self,
                model='quad',
                color=color.gray,
                scale=bar_scale,
                position=(icon_scale[0]/2 + bar_scale[0]/2 + 0.05, 0, 0),
            )
        
        self.bar_selection = Entity(
            parent=self,
                model='quad',
                color=color.light_gray,
                scale=(bar_scale[0] + icon_scale[0]/2, icon_scale[1]),
                position=(icon_scale[0]/2 + bar_scale[0]/2 + 0.05, 0, 0.1),
                visible=False,
        )
        
        self.init_bars(count)

    def select(self, do_select):
        self.bar_selection.visible = do_select

    def clear_bars(self):
        for bar in self.ammos:
            destroy(bar)
        self.ammos = []

    def init_bars(self, count):
        """Create bars based on current count."""
        self.clear_bars()
        self.bar_width = 1 / self.max # Each bar's width is proportional to max
        self.bar_distance = 1 / (self.max * 4)
        self.bar_current_x = -0.5 + self.bar_width / 2  # Start position for the first bar

        for i in range(count):
            self._create_bar(i)

    def _create_bar(self, index):
        amount_bar = Entity(
                parent=self.bar_container,
                model='quad',
                color=color.green,
                scale=(self.bar_width - self.bar_distance, 0.9),
                position=(self.bar_current_x + index * self.bar_width, 0, 0),
                z=-0.1,
            )
        self.ammos.append(amount_bar)

    def remove_bars(self, count):
        for i in range(count):
            if len(self.ammos) > 0:
                destroy(self.ammos.pop())

    def add_bars(self, count):
        for i in range(count):
            if len(self.ammos) >= self.max:
                return
            self._create_bar(self.count)

    def set_ammo_bars(self, amount):
        if len(self.ammos) > amount:
            self.remove_bars(len(self.ammos) - amount)
        elif len(self.ammos) < amount:
            self.add_bars(amount)

    @property
    def count(self):
        return len(self.ammos)

class LandmineBar(BaseBar):
    def __init__(self,  max=10, count=0, icon_scale=(0.15, 0.15), bar_scale=(1, 0.1), **kwargs):
        super().__init__(max=max, count=count, icon_scale=icon_scale, bar_scale=bar_scale, texture='assets/images/landmine.png', **kwargs)

class BuildingBlockBar(BaseBar):
    def __init__(self,  max=10, count=0, icon_scale=(0.15, 0.15), bar_scale=(1, 0.1), **kwargs):
        super().__init__(max=max, count=count, icon_scale=icon_scale, bar_scale=bar_scale, texture='assets/images/white_wall.png', **kwargs)


if __name__ == '__main__':
    app = Ursina()
    def input(key):
        if key == 'space':  # Press space to reduce ammo
            ammo_bar.remove_bars(1)
        if key == 'a':
            ammo_bar.add_bars(5)

    ammo_bar = LandmineBar(
    count=5,
    max=10,
    position=(0, 0, 0)  # Path to your ammo icon texture
    )

    app.run()