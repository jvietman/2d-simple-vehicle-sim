from datetime import datetime
import pygame, engine, json, math, os

class obj(pygame.sprite.Sprite):
    def __init__(self, win_resolution: tuple, textures: dict, pos = [0, 0], size = [1, 1], rotation = 0):
        # super class constructor
        pygame.sprite.Sprite.__init__(self)
        self.res = win_resolution
        
        # sizes and positions are not in specific unit, but in a rather universal unit (you can interpret units as meters, cm, km etc., up to you)
        # how big a unit is on screen is decided by the renderer
        self.pos = pos
        self.size = size
        self.rotation = rotation
        self.state = "default" # states = current texture
        # this is a universal default state which has to be included in any list of textures
        
        self._textures = {}
        for i in textures.keys():
            self._textures[i] = pygame.image.load(textures[i])
        
        # pygame sprite variables
        self.image = pygame.Surface(self.res, pygame.SRCALPHA)
        self.image.blit(self._textures[self.state], pos)
        
        self.rect = self.image.get_rect()
    
    def update(self, pos: tuple, size: tuple, empty = False):
        self.image = pygame.Surface(self.res, pygame.SRCALPHA)
        if not empty:
            # when rotating image, it tries to resize it to fit into the surface. thats why a neat calculation happens in order to resize the image depending on rotation.
            n = 45-abs((self.rotation % 90) - 45)
            p = n/45
            d = math.sqrt(size[0]**2+size[1]**2)
            # tsize = (size[0]*max(abs(math.sin(self.rotation)), abs(math.cos(self.rotation)))**-1, size[1]**max(abs(math.sin(self.rotation)), abs(math.cos(self.rotation)))**-1)
            tsize = (size[0], size[1])
            self.image.blit(pygame.transform.scale(pygame.transform.rotate(self._textures[self.state], 360-self.rotation), tsize), (pos[0]-tsize[0]/2, pos[1]-tsize[1]/2))
            self.rect = self.image.get_rect()

class vehicle(obj):
    def __init__(self, win_resolution: tuple, working_directory: str, pos = [0, 0], rotation = 0):
        # super class constructor
        self.res = win_resolution
        with open(working_directory+"/vehicle.json") as f:
            self.data = json.load(f)
            f.close()
        
        os.chdir(working_directory)
        obj.__init__(self, win_resolution, self.data["textures"], pos, (self.data["width"], self.data["length"]), rotation)

def move_direction(pos, direction_deg, distance) -> list:
    """
    Move from an initial position (x, y) by a certain distance in a specified direction.
    
    :param x: Initial x-coordinate.
    :param y: Initial y-coordinate.
    :param direction_deg: Direction in degrees (0° is along the positive x-axis, increasing clockwise).
    :param distance: Distance to move.
    :return: Tuple (new_x, new_y) representing the new position.
    """
    # Convert direction from degrees to radians
    direction_rad = math.radians(direction_deg-90)
    
    x, y = pos
    # Calculate new coordinates
    new_x = x + distance * math.cos(direction_rad)
    new_y = y + distance * math.sin(direction_rad)
    
    return [new_x, new_y]

class render:
    def __init__(self, size: tuple, cam_pos = [0, 0], cam_zoom = 10):
        # setup
        self.size = size
        self.ratio = size[0]/size[1]
        self.screen = pygame.display.set_mode(size)
        
        # power curve rendering
        self.graph_scale = (1, 1)
        
        # renderer values
        self.cam_pos = cam_pos # middle of camera
        self.cam_zoom = cam_zoom # units in height displayed on screen. width is calculated automatically
        # sprite (object) rendering
        self.all_sprites = pygame.sprite.Group()
        self.objects = {}
        
        # performance debugging
        self._frames = 0 # counted frames in timeframe
        self._fps_short = 0 # fps counted in 0.2 seconds
        self._fps_short_counted = 1
        self._fps_begin = datetime.now() # start time of counting for 0.2 seconds
        self._fps_prev = 0
        self.fps = 0
        
        # graph display, temporary values
        self._graph_y_size = 10
        self._graph_trail_length = 100
        self._tmp_graph_prev = [(-1, -1)]

    # object operations
    def add_object(self, name: str, obj: obj):
        if name in self.objects:
            raise Exception("Object with this name already exists.")
        else:
            self.objects[name] = obj
            self.all_sprites.add(obj)
    
    def get_object(self, name: str) -> obj:
        return self.objects[name]
    
    def move_object(self, name: str, pos: tuple) -> tuple:
        o = self.objects[name]
        o.pos = [o.pos[0]+pos[0], o.pos[1]+pos[1]]
        return o.pos
    
    def move_object_straight(self, name: str, step: int)  -> tuple:
        o = self.objects[name]
        o.pos = move_direction(o.pos, o.rotation, step)
        return o.pos
    
    def rotate_object(self, name: str, degrees: int) -> int:
        o = self.objects[name]
        o.rotation += degrees
        if o.rotation < 0:
            o.rotation += 360
        if o.rotation > 359:
            o.rotation -= 360
        return o.rotation

    # debugging: power curves
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
    
    # debug values: fps
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
    
    # actual renderer shit
    def get_events(self) -> list[pygame.event.EventType]:
        return pygame.event.get()
        
    def update_graph(self, x=-1, y=-1):
        self._update_frames()
        
        prev = self._tmp_graph_prev[0]
        if not x == -1:
            pygame.draw.line(self.screen, (0, 0, 0), (0, 0), (self.size[0], 0), 20)
            pygame.draw.line(self.screen, (255, 0, 0), (int(x), 0), (int(x), 10), 5)
        if not y == -1:
            px, py = x-self._graph_y_size/2, self.size[1]-(y-self._graph_y_size/2)*self.graph_scale[1]
            pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(px, py, self._graph_y_size, self._graph_y_size), self._graph_y_size)
            
        
        self._tmp_graph_prev.append((x, y))
        if len(self._tmp_graph_prev) > self._graph_trail_length:
            if not prev[1] == -1:
                pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(prev[0]-self._graph_y_size/2, self.size[1]-((prev[1]-self._graph_y_size/2)*self.graph_scale[1]), self._graph_y_size, self._graph_y_size), self._graph_y_size)
            del prev
        
        pygame.display.update()
    
    def render(self):
        self._update_frames()
                
        self.screen.fill((255, 255, 255))

        scale = (self.size[0] / (self.cam_zoom*self.ratio), self.size[1] / self.cam_zoom)
        # for i in self.objects.values():
        #     i._img = pygame.Surface((i.size[0]*scale[0], i.size[1]*scale[1]))
        #     i._img.blit(i._textures[i.state], (0, 0))
        
        #     i._rect = i._img.get_rect()
        #     i._rect.x, i._rect.y = (200, 200)
            
            # i._rect.x, i._rect.y = ((i.pos[0]-self.cam_pos[0])*scale[0], (i.pos[1]-self.cam_pos[1])*scale[1])
        
        for i in self.objects.values():
            size = ((i.size[0]*scale[0])*self.ratio, i.size[1]*scale[1])
            pos = ((i.pos[0]-self.cam_pos[0]+(self.size[0]/scale[0])/2)*scale[0], (i.pos[1]-self.cam_pos[1]+(self.size[1]/scale[1])/2)*scale[1])
            outside_cam = pos[0] < -size[0] or pos[0]-size[0]/2 > self.size[0] or -size[1] > pos[1] or pos[1]-size[1]/2 > self.size[1]
            i.update(pos, size, outside_cam)
        self.all_sprites.draw(self.screen)
        pygame.display.update()