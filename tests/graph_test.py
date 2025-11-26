from engine import engine
from render import render

# define engine
rev_range = [5300, 5800]
rev_max = 6500

motor = engine(["(5.25*sqrt(x))-100", "(5.25*sqrt("+str(rev_range[0])+"))-100", "-0.0002*(x-"+str(rev_range[1])+")**2+(5.25*sqrt("+str(rev_range[0])+"))-100"], [rev_range[0], rev_range[1], rev_max], 1200, 2)

# graph config
size = (1000, 500)
step = 0.1
display = render(size)

display.set_graph_scale(motor, size, step)
display.power_curve(motor, step)

# print graph and calc all values with amount of steps
x = 0
while True:
    x += step
    # calculate and print value
    print(str(round(x))+"."+str(x).split(".")[1][0]+"rpm   "+str(motor._point_at_graph(x))+" nm")
    
    # reset graph
    if x > rev_max*display.graph_scale[0]:
        display.power_curve(motor, step)
        x = 0
    
    display.update_graph(x)