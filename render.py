import pygame, engine
from datetime import datetime

class render:
    def __init__(self, size: tuple):
        self.size = size
        self.screen = pygame.display.set_mode(size)
        
        # power curve rendering
        self.graph_scale = (1, 1)
        
        # pygame events
        # self.events = None
        
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
        """Updates the framerate value.
        
        Framerate is safed in the ```fps``` variable of this class. The fps value is rounded to the first decimal place.
        
        There are two types of fps values here:
        - fps short: quick, but low accuracy value: the frames rendered in 0.2 seconds
        - fps long: slow, but high accuracy value: the frames rendered in 1 second
        
        The fps is a combination of the short and long fps values. Depending on how many short fps youve counted, thats the percentage of whats added from short fps and what from long fps:
            fps = long_fps*(1-(0.2*short_counted)) + short_fps
        
        For example, if the short fps was counted 3 times, that means we have the fps value for 0.6 seconds, we add only 40% of the long fps.
        This results in a smooth, semi-accurate but quicker fps value.
        
        """
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
        
        self.fps = round(self._fps_prev*(1-(0.2*self._fps_short_counted)) + self._fps_short, 1)    
    
    def get_events(self) -> list[pygame.event.EventType]:
        return pygame.event.get()
        
    def update_graph(self, x=-1):
        self._update_frames()
        
        if not x == -1:
            pygame.draw.line(self.screen, (255, 0, 0), (int(x), 0), (int(x), 10), 5)
        
        pygame.display.update()