# -*- coding: utf-8 -*-
import time

class MainLoop(object):
    '''Implements the main loop of application'''

    def __init__(self, fps=60, physics_update=None, draw=None):
        self.fps = fps
        self.dt = 1.0 / self.fps
        self.physics_update = physics_update
        self.draw = draw
        self._continue = True
        
        # Atrasa importação para evitar dependências circulares
        from FGAme.backends import get_screen, get_input_listener
        self._get_screen = get_screen
        self._get_input_listener = get_input_listener
        

    def run(self, timeout=None, phys_timeout=None):
        self._continue = True        
        sleep = time.sleep
        gettime = time.time
        screen = self._get_screen()
        listener = self._get_input_listener()

        while self._continue:
            t0 = gettime()
            listener.step()
            self.physics_update(self.dt)
            screen.clear((255, 255, 255))
            self.draw(screen)
            screen.show()
            sleep(max(self.dt - (gettime() - t0), 0))

    def stop(self):
        self._continue = False
        
