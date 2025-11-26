from math import sqrt

class engine:
    def __init__(self, power_graphs: list[str], power_graph_limits: list[float], idle_revs, engine_resistance = 0.9):
        # graph config
        self._revs_idle = idle_revs
        self._res_eng = engine_resistance # in percentage (0-1) of max revs
        self._revs_speed = 50
        self._graphs = power_graphs # a collection of functions that create one complex function. function variable is x.
        self._graphs_limits = power_graph_limits # the point where a function i ends.
        # the start x value for the next function starts at x > e, e standing for the end of the last function.
        # being in under the limit means x <= e.
        # torque maximum
        self._vmax = 0
        for i in range(self._graphs_limits[-1]):
            y = self._point_at_graph(i)
            self._vmax = y if y > self._vmax else self._vmax
        
        # real-time values
        self.revs = self._revs_idle
        self.torque = 0
        self.throttle = 0
        self.momentum = 0
    
    def _point_at_graph(self, x: float) -> float:
        """Calculates the point x on one of the functions, where the x value is in.
        
        The power curve is realized as multiple functions that create one big function.
        The functions are seperated (when one function begins and where it ends) by using maximum values.
        This method automatically decided which function to choose to calculate the value.

        Args:
            x (float): point on graph

        Returns:
            float: calculated y value of one of the functions, where x is in
        """
        if x > self._graphs_limits[-1]:
            x = self._graphs_limits[-1]
        elif x < 0:
            x = 0
        # get the function where x is part of the limits
        f = [i for i in range(len(self._graphs_limits)+1) if x > ([-1]+self._graphs_limits)[i]][-1]
        return eval(self._graphs[f].replace("x", str(x)))
    
    # depricated, this is for rising or falling revs
    def update_revs(self, throttle: float, resistance: float):
        """Update current engine revs and torque output based on throttle and evironmental effects (downforce, windresistance, grip).

        No values returned, they are directly set to ```self.revs``` and ```self.torque```.

        Args:
            throttle (float): Throttle in percentage
            resistance (float): Environmental effects
        """

        max_revs = self._graphs_limits[-1]

        # create a value as a base, then change that value and add to total revs at the end
        
        # the base is the revs we wanna get to (percentage of max revs)
        # substracted by the current revs, so it can rev down again when no throttle
        revs = base = self._revs_idle+((max_revs-self._revs_idle)*throttle)-self.revs
        
        # engine resistance
        # reving up = more resistance (also based of torque) = engine braking
        # reving down (towards idle), if no resistance, slowly go towards idle revs, decelerating
        revs -= (base*(1-self._res_eng))
        
        # environmental resistance (mass/ downforce, drag, grip, etc.)
        # accelerates and decelerates vehicle **momentum**.
        # unlike revs, we are pushing an object with a force (twisting to be percise), it keeps rolling and decelerates on its own
        # properties
        # - slowly rise revs
        #   - overcome resistance with higher torque
        # - hinders revs going down
        # - if resistance too high, cant rev up (not enough engine power to move)
        # - too high res doesnt mean instead deceleration
        #   => but just harder acceleration
        #   => and carries way more momentum (resists against windresistance, but thats what the physics module decides)
        # that means here you convert that revs that add to the total revs into a momentum, that means we need extra variables
        
        # max_reached = (self.torque/2)/self._vmax
        # env_res = (resistance/self.torque)*max_reached
        # print(env_res)
        # revs *= 0.1
        
        self.revs += revs
        if self.revs < 0: self.revs = 0
        if self.revs > max_revs: self.revs = max_revs
        self.torque = self._point_at_graph(self.revs)*throttle
        
        # res_eng = self._res_eng*(((self.revs-self._revs_idle)/self._revs_idle) if self.revs < self._revs_idle*2 else 1)
        # self.revs += revs
        # self.torque = self._point_at_graph(self.revs)*throttle