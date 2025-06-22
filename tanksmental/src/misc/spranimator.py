import os
import time as pytime
from collections import deque
from ursina import *

def wait(duration):
    """Coroutine function to wait for a specified duration."""
    start_time = pytime.time()
    while pytime.time() - start_time < duration:
        yield  # Yield control back to the coroutine manager.

class SpriteAnimator:
    def __init__(self, frames_dir, delay=0.1):
        # Load textures from the specified directory.
        self.frames = [
            texture for texture in 
            (load_texture(os.path.join(frames_dir, f.split('.')[0]))
            for f in os.listdir(frames_dir)
            if os.path.isfile(os.path.join(frames_dir, f)))
            if texture is not None
        ]
        self.frames.sort(key=lambda x: int(x.name.split('.')[0]))
        self.delay = delay
        self.active_coroutines = deque()  # Use deque for efficient coroutine management.

    def animate(self, entity, callback=None):
        """Start animation for the given entity."""
        entity._original_z = entity.z
        entity.z = -0.1
        entity.render_queue = 2
        def run_animation():
            for frame in self.frames:
                entity.texture = frame  # Update texture
                yield from wait(self.delay)  # Wait for the delay duration.
            # Wait extra time after animation finishes
            yield from wait(0.1)
            if callable(callback):
                callback()

        self.active_coroutines.append(run_animation())

    def update(self):
        """Update all active coroutines."""
        for _ in range(len(self.active_coroutines)):
            coroutine = self.active_coroutines.popleft()
            try:
                next(coroutine)
                # Put it back in the queue if still active.
                self.active_coroutines.append(coroutine)  
            except StopIteration:
                # Coroutine is done; do not re-add it to the deque.
                pass 

class AnimatedTile(Entity):
    def __init__(self, position, animation_frames, duration):
        super().__init__(model="quad", texture=animation_frames[0], position=position, scale=1)
        self.frames = animation_frames
        self.duration = duration
        self.current_frame = 0
        self.timer = 0

    def update(self):
        self.timer += time.dt
        if self.timer >= self.duration:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.texture = self.frames[self.current_frame]

       
if __name__ == '__main__':
    app = Ursina()
    entity = Entity(model='quad', color=color.white, visible=True)
    animator = SpriteAnimator('assets/animations/landmine_explosion', delay=0.04)
    animator.animate(entity)

    def update():
        animator.update()
    
    app.run()