from ursina import *

class SpriteAnimator:
    def __init__(self, frames_dir, delay=0.1):
        self.frames = [
            load_texture(os.path.join(frames_dir, f.split('.')[0]))
            for f in os.listdir(frames_dir)
            if os.path.isfile(os.path.join(frames_dir, f))
        ]
        self.frames.sort(key=lambda x: x.name)
        self.delay =delay

    def animate(self, entity:Entity, callback=None):
        for i in range(len(self.frames)):
            invoke(setattr, entity, 'texture', self.frames[i], delay=i*self.delay)
        if callback is not None:
            invoke(callback, delay=(len(self.frames) + 1)*self.delay)

        
if __name__ == '__main__':
    app = Ursina()
    entity = Entity(model='quad', color=color.white, visible=True)

    animator = SpriteAnimator('assets/animations/landmine_explosion', delay=0.03)
    animator.animate(entity)
    app.run()