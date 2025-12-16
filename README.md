# 2d-simple-vehicle-sim
Semi-realistic dynamic vehicle simulator in top-down 2D space.

## Developer notes
### Todo
- [X] basic engine methods
    - [X] one graph out of multiple functions
    - [X] calculate point at function
- [X] Powercurve rendering
- [X] handler
- [ ] implement reving (0-1 instantly, times resistance and throttle)
    - [X] controls (eventhandler)
        - [X] get events
        - [X] get binds from json
        - [X] when bound button pressed, set as true
    - [X] do action (here its calculate reving)
        - [X] simple reving
        - [ ] advanced rev calculation (simulating) using update_revs
            - [ ] debugging
                - [X] add y point on graph for debugging
                - [ ] add trail behind it
            - [ ] rev up on throttle percentage
            - [ ] engine resistance
            - [ ] environmental resistance, vehicle momentum
                - [ ] clutch
                - [ ] accelerate, decelerate
                - [ ] gears
- [X] keybinder (for getting pressed keys to set as binds)
- [ ] simulation
    - [ ] configs
        - [ ] session
        - [ ] car
            - [ ] engines
            - [ ] transmissions
        - [ ] tires
        - [ ] maps
    - [ ] renderer
        - [ ] load objects (with textures and values)
        - [ ] set units and scales
        - [ ] render objects
        - [ ] render states
            - [ ] add states to render queue
            - [ ] render states from queue
            - [ ] render states inbetween states, async
    - [ ] physics
        - [ ] take inputs
        - [ ] calculate next state
        - [ ] return state
    - [ ] controls
        - [ ] calculate input behaviour (smooth/ sharp steering, slow trailing, threshold braking, etc.)

1. [X] Fix scaling (one zoom value)
    - [X] zoom for height, width scale automatically calculated
2. [X] Fix object scaling
    - [ ] vehicle size is not image size
3. [X] Fix out of cam (relative pos of cam and position of car)
4. [ ] obj class that others inherit
    - vehicle
    - map
5. [ ] map
    - [X] display map
    - [ ] fix zooming and position  
6. [ ] Fix rotation
7. [X] Basic movement
8. [ ] Advanced movement (front wheels steering and driving)

### Performance fixes
- graph printing
    - determine points to calculate on pixels that can be displayed
- graph finding
    - save next and previous limit in cache
        -> when value to high or to low switch between the graphs next to eachother
        -> you dont have to check all graphs to find the limit, just check the ones next to each other

### Problems
- [X] fix rendering
    - when async: calls method, but doesnt render (freezes)
    --> FIXED (temporarily and poorly)! Just dont do it async :3
- [X] rendering lag is ok, but physics lag not (not getting to hz)
    => try minimizing physics lag so it doesnt even happen
    => make async or whatever (idk)
    --> FIXED! update accumulated time in the loop so it knows if it did all the calculations it had to do
- [ ] on too low fps, fps is inaccurate
    => try implementing check, if taking too long to generate 0.2, then just print 1 second fps
- [ ] get events all the time, dont miss events because you calculate some bs
    => async events.get()?
- [ ] rendering problem
    - how do sprites work?
    - what is the order all the things are executed?
    - fix code in mainloop, check objects list etc
- [ ] render car object in middle
- [ ] blit all objects (except map) on one surface

### Update Revs
How do the revs update? How do they increase and decrease over time with certain inputs?
Properties
- [X] throttle zeigt position in revs, wo man hin will
- [X] 0 resistance = instantly oben
- [X] nicht instant fall der revs, sondern langsam richtung idle
- [X] Powerkurve Höhe (Torque) abhängig von wie viel % throttle
- [ ] mehr torque = schnelleres hochrevven
- [ ] höhere resistance bei hohen Drehzahlen (engine breaking)
