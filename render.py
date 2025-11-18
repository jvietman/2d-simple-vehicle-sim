import pygame, engine
from datetime import datetime

class render:
    def __init__(self, size: tuple):
        self.size = size
        self.screen = pygame.display.set_mode(size)
        
        # power curve rendering
        self.graph_scale = (1, 1)
        
        # performance debugging
        self._frames = 0 # counted frames in timeframe
        self._fps_short = 0 # fps counted in 0.2 seconds
        self._fps_short_counted = 1
        self._fps_begin = datetime.now() # start time of counting for 0.2 seconds
        self._fps_prev = 0
        self.fps = 0

    def power_curve(self, e: engine, step = 1):
        """Calculate and render powercurve.
        
        This method clears the whole screen and calculates and render the powercurve from scratch.
        Because we are doing everything from scratch, calling this method too often may cause performance issues, depending on the scaling.

        Args:
            e (engine): Reference to engine
        """
        self.screen.fill((0, 0, 0))

        scale = self.graph_scale
        
        # scaling
        # steps
        prev, now = (0, self.size[1]), (0, 0)
        for i in range(int(( e._graphs_limits[-1] * scale[0] ) / step)):
            now = (int(i*step), int(self.size[1] - (e._point_at_graph((i/scale[0])*step) * scale[1])))
            pygame.draw.line(self.screen, (0, 0, 255), prev, now, 4)
            prev = now
            
    def set_graph_scale(self, e: engine, size: tuple, step = 1):
        """Set the scale of the graph rendered by giving it width and height in pixels.
        
        Method does not return value, but saves the scale in the ```self._graph_scale``` tuple.

        Args:
            e (engine): Reference to engine
            size (tuple): Width and height in pixels
        """
        
        # calculate x scale
        w = size[0] / e._graphs_limits[-1]
        
        # get maximum
        max = 0
        for i in range(0, int((e._graphs_limits[-1]*w)/step)):
            y = e._point_at_graph((i/w)*step)
            max = y if y > max else max
        
        # calculate y scale and save
        self.graph_scale = (w, size[1] / max)
        
    def _update_frames(self):
        # every 0.2 seconds, the short fps gets calculated with the previous long fps. after a full second you get the high accuracy value.
        # this is for quicker updates without really losing accuracy
        self._frames += 1
        
        elapsed = (datetime.now()-self._fps_begin).total_seconds()
        if elapsed > 0.2*self._fps_short_counted:
            self._fps_short = self._frames
            self._fps_short_counted += 1
        if self._fps_short_counted > 5:
            self._fps_prev = self._frames
            self._fps_short_counted = 1
            self._fps_short = self._frames = 0
            self._fps_begin = datetime.now()
        
        self.fps = self._fps_prev*(1-(0.2*self._fps_short_counted)) + self._fps_short
        
    def update_graph(self, x=-1) -> pygame.event:
        self._update_frames()
        e = pygame.event.poll()
        
        if e.type == pygame.QUIT:
            exit()
        
        if not x == -1:
            pygame.draw.line(self.screen, (255, 0, 0), (int(x), 0), (int(x), 10), 5)
        
        pygame.display.flip()
        return e