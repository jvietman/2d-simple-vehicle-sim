from engine import engine
from render import render
from datetime import datetime
from typing import final
import threading, pygame, json

# define engine
rev_range = [5300, 5800]
rev_max = 6500
engine_resistance = 0.1

motor = engine(["(5.25*sqrt(x))-100", "(5.25*sqrt("+str(rev_range[0])+"))-100", "-0.0002*(x-"+str(rev_range[1])+")**2+(5.25*sqrt("+str(rev_range[0])+"))-100"], [rev_range[0], rev_range[1], rev_max], 1200, engine_resistance)

# define renderer
size = (1000, 500)
step = 1
display = render(size)

display.set_graph_scale(motor, size, step)
display.power_curve(motor, step)

# handler values
acc = 0
hz = 100
dt = 1/hz #100hz
actions = 0
with open("config.json") as f:
    config = json.load(f)
    f.close()
# run thread is for terminating loops in threads
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
            smth_happened = True if i.type == pygame.KEYDOWN or i.type == pygame.KEYUP else False
            if smth_happened:
                if i.__dict__["key"] in binds:
                    # get the event you bound the key to, then set the state of event
                    events[binds[i.__dict__["key"]]] = i.type == pygame.KEYDOWN

# testing values
brake = 0

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
                motor.throttle = 0.7
            elif events["brake_50"]:
                motor.throttle = 0.5
            elif events["brake_100"]:
                motor.throttle = 0.2
            else:
                motor.throttle = 0
            
            # physics module calculations
            motor.update_revs(0.9)
            # when braking: motor.update_revs(1, x), x is resistance coming from braking

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
        # render(interpol(acc / dt))
        display.update_graph(motor.revs*display.graph_scale[0])
        run_eventhandler(display.get_events()) # hand over events to eventhandler
except KeyboardInterrupt:
    # termination
    run_thread.clear()
    pass