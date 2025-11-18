from engine import engine
from render import render
from datetime import datetime
import random, threading

# define engine
rev_range = [5300, 5800]
rev_max = 6500

motor = engine(["(5.25*sqrt(x))-100", "(5.25*sqrt("+str(rev_range[0])+"))-100", "-0.0002*(x-"+str(rev_range[1])+")**2+(5.25*sqrt("+str(rev_range[0])+"))-100"], [rev_range[0], rev_range[1], rev_max], 1200, 2)

# define renderer
size = (1000, 500)
display = render(size)

# handler
acc = 0
hz = 100
dt = 1/hz #100hz
actions = 0

workers = []
def run_async(method):
    global workers
    workers.append(threading.Thread(target=method))
    workers[-1].start()

now = now_second = datetime.now()
while True:
    # get elapsed time and add to accumulator
    elapsed = (datetime.now()-now).total_seconds()
    acc += elapsed
    
    # calculate physics that happened in accumulated time
    while acc >= dt:
        # physics calculation
        for i in range(30):
            x = motor._point_at_graph(i)
        actions += 1
        
        acc -= dt
    
    # reset elapsed time
    if not elapsed == 0: now = datetime.now()
    if (datetime.now()-now_second).total_seconds() > 1: # this if for debugging
        print(str(actions)+" "+str(display.fps)+" fps "+str(dt)+" dt")
        actions = 0
        now_second = datetime.now()
    
    # render frames async
    run_async(display.update_graph)
    # render(interpol(acc / dt))