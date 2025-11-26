from engine import engine
from render import render
from datetime import datetime

# define engine
rev_range = [5300, 5800]
rev_max = 6500

motor = engine(["(5.25*sqrt(x))-100", "(5.25*sqrt("+str(rev_range[0])+"))-100", "-0.0002*(x-"+str(rev_range[1])+")**2+(5.25*sqrt("+str(rev_range[0])+"))-100"], [rev_range[0], rev_range[1], rev_max], 1200, 2)

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

now = now_second = datetime.now()
while True:
    # get elapsed time and add to accumulator
    elapsed = (datetime.now()-now).total_seconds()
    acc += elapsed
    
    # calculate physics that happened in accumulated time
    while acc >= dt:
        # physics calculation

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
    display.update_graph()
    # render(interpol(acc / dt))