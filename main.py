from physics import physics
from engine import engine
from render import render, vehicle, map
from datetime import datetime
from typing import final
import threading, pygame, json, os

# load configs
configs = {}
with open("config.json", "r") as f:
    config = json.load(f)
    f.close()

with open("session.json", "r") as f:
    configs["session"] = json.load(f)
    f.close()

with open("vehicles/engines.json", "r") as f:
    configs["engines"] = json.load(f)
    f.close()
    
with open("vehicles/transmissions.json", "r") as f:
    configs["transmissions"] = json.load(f)
    f.close()

# setup physics simulation
sim = physics()

# load engine
# load car
with open("vehicles/"+configs["session"]["vehicle"]+"/vehicle.json", "r") as f:
    vehicledata = json.load(f)
    f.close()

cur_engine = configs["engines"][vehicledata["engine"]]
cur_trans = configs["transmissions"][vehicledata["transmission"]]
motor = engine(cur_engine["functions"], cur_engine["limits"], cur_engine["idle_revs"], cur_engine["resistance"])

# setup renderer
display = render(tuple(config["resolution"]))
display.add_object("map", map(display.size, "city_carpet.jpg", [1201, 801])) # main vehicle object
display.add_object("main", vehicle(display.size, os.getcwd()+"/vehicles/"+configs["session"]["vehicle"], [0, 0], 0)) # main vehicle object
# display.add_object("map", obj(display.size, os.getcwd()+"/vehicles/city carpet", [-100, -100], (1201, 801)))

# mainloop handler values
acc = 0
hz = config["hertz"]
dt = 1/hz #100hz
actions = 0
# "run_thread" is for terminating loops in threads
run_thread = threading.Event()
run_thread.set()


# events
running = True
events = {}
binds: final = {}
# events is the thing you should use. it saves the states of the binds, example: throttle = True. Its a simple way of seeing if your event is fulfilled
# setup binds (flip all keys with elements, so you can find event by giving the key pressed)
for i in config["binds"].keys():
    binds[config["binds"][i]] = str(i)
# setup events dict where you can read out, if an event is fulfilled (if button bound to it is pressed)
for i in config["binds"].keys():
    events[i] = False

def run_eventhandler(events_list: list, in_async = False):
    """**Takes a list of pygame events and sorts out the keys pressed, where the key is bound to an event and organizes them into a dictionary.**\n
    
    The dictionary ```binds``` holds bindings between a keyboard key and a specific event. For example the W key bound to the event of moving forward.
    Once a key, where an event is bound to it, is pressed, the event in the "events" dictionary turns True.
    The other way around, when you release that key, the event turns to False.\n
    
    **In short:** after running this method and giving it the list of pygame events, it neatly organizes the events
    that are actually triggered in the ```events``` dictionary, where they can be easily checked by using ```events[<event>]```

    Args:
        events_list (list): List of pygame events
        in_async (bool, optional): This is for recursion purposes only. Defaults to False.
    """
    global events, running
    
    if not in_async:
        # restart yourself as async, so you dont hold up the rest
        threading.Thread(target=run_eventhandler, args=(events_list, True)).start()
    else:
        for i in events_list:
            # when closing window/ quitting, throw this to end mainloop
            if i.type == pygame.QUIT: running = False
            
            # if key was down or up <=> if key was pressed
            if i.type == pygame.KEYDOWN or i.type == pygame.KEYUP:
                if i.__dict__["key"] in binds:
                    # get the event you bound the key to, then set the state of event
                    events[binds[i.__dict__["key"]]] = i.type == pygame.KEYDOWN

### start of testing values ###
steer = 0
speed = 0
brake = 0
reverse = 0

pos = (0, 0)
rotation = 0

# setup
display.cam_zoom = 1200
display.cam_pos = [0, 0]

# config
turnspeed = 0.5
reversespeed = 0.05
accel = 0.0015
decel = 0.0003
brakeforce = 0.0013
### end of testing values ###

now = now_second = datetime.now()
try:
    while True:
        # if pygame window is closed, exit by using an exception, which is catched
        if not running: raise KeyboardInterrupt
        
        # get elapsed time and add to accumulator
        elapsed = (datetime.now()-now).total_seconds()
        acc += elapsed
        
        # calculate physics that happened in accumulated time
        while acc >= dt:
            # controls module
            if events["throttle_100"]:
                motor.throttle = 1
            elif events["throttle_50"]:
                motor.throttle = 0.5
            else:
                motor.throttle = 0
            
            if events["brake_100"]:
                brake = 1
            elif events["brake_50"]:
                brake = 0.5
            else:
                brake = 0
                
            if events["left_100"]:
                steer = -1
            elif events["left_50"]:
                steer = -0.5
            elif events["right_50"]:
                steer = 0.5
            elif events["right_100"]:
                steer = 1
            else:
                steer = 0
            
            # engine calculations
            ## calculate resistence with physics module (breaking, environmental factors)
            ## when braking: motor.update_revs(1, x), x is resistance coming from braking
            # calculate engine revs
            motor.update_revs(0)
            # calculate actual output (through transmission, with all resistences)
            ## motor.transmission method to be implemented
            
            # physics calculations
            ## calculate next state
            ## state = sim.next(motor)
            if motor.throttle:
                speed += accel*motor.throttle
            elif brake and speed > 0:
                speed -= brakeforce*brake
            elif speed > 0:
                speed -= decel
            if not speed > 0 and not motor.throttle:
                if brake:
                    speed = -reversespeed*brake
                else:
                    speed = 0
            
            pos, rotation = display.move_object_straight("main", speed), display.rotate_object("main", turnspeed*steer)
            display.cam_pos = pos
            
            actions += 1
            acc -= dt
            acc += ((datetime.now()-now).total_seconds()) - elapsed
        
        # reset elapsed time
        if not elapsed == 0: now = datetime.now()
        if (datetime.now()-now_second).total_seconds() > 1: # this if for debugging
            print(str(actions)+" "+str(display.fps)+" fps ")
            actions = 0
            now_second = datetime.now()
        
        # render frames (async)
        ## render inbetween states, async: render(interpol(acc / dt))
        display.render()
        run_eventhandler(display.get_events()) # hand over events to eventhandler
except KeyboardInterrupt:
    # termination
    run_thread.clear()
    pass