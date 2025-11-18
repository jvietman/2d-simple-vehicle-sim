from math import sqrt

class engine:
    def __init__(self, power_graphs: list[str], power_graph_limits: list[float], idle_revs, engine_resistance = 0.9):
        # graph config
        self._revs_idle = idle_revs
        self._res_eng = engine_resistance
        self._revs_speed = 50
        self._graphs = power_graphs # a collection of functions that create one complex function. function variable is x.
        self._graphs_limits = power_graph_limits # the point where a function i ends.
        # the start x value for the next function starts at x > e, e standing for the end of the last function.
        # being in under the limit means x <= e.
        
        # real-time values
        self.revs = self._revs_idle
        self.torque = 0
        self.throttle = 0
    
    def _point_at_graph(self, x: float) -> float:
        if x > self._graphs_limits[-1]:
            x = self._graphs_limits[-1]
        elif x < 0:
            x = 0
        # get the function where x is part of the limits
        f = [i for i in range(len(self._graphs_limits)+1) if x > ([-1]+self._graphs_limits)[i]][-1]
        return eval(self._graphs[f].replace("x", str(x)))
    
    def update_revs(self, throttle: float, resistance) -> float:
        res_eng = self._res_eng*(((self.revs-self._revs_idle)/self._revs_idle) if self.revs < self._revs_idle*2 else 1)
        self.revs += self._revs_speed*(throttle*(1+res_eng)-res_eng)
        self.torque = self._point_at_graph(self.revs)*throttle