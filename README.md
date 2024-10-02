# Racing Line Simulation
## Project Overview
This project simulates realistic car physics and collision detection, focusing on calculating and optimizing racing lines. The simulation involves car movement based on velocity and steering angle, and incorporates detailed collision detection that accounts for the car's rotation and environmental factors.

## Features
* Advanced Car Physics: The simulation models realistic acceleration, deceleration, and cornering dynamics, considering factors like throttle position, braking force, and turning radius. The physics system calculates the maximum steering angle based on current velocity, traction, downforce, mass, and wheelbase, ensuring the car handles accurately under different conditions.
* Accurate Collision Detection: Optimized pixel-based collision detection system that accounts for car rotation, checking key points such as the front, sides, and rear of the vehicle.
* Dynamic Track Interaction: The user can draw custom tracks, and the car will respond to the white pixels representing the track boundaries.
## Future Plans
* NEAT Algorithm Integration: Implement machine learning (using the NEAT algorithm) to allow the car to learn and optimize its racing lines autonomously.
* Improved User Interaction: Expand the user interface with features for customizing tracks and simulating different car dynamics.
* Performance Enhancements: Further optimize the physics calculations and collision detection to improve the simulation's real-time performance.
