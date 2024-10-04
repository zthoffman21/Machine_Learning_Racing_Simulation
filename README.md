# Racing Line Simulation

![Untitled video - Made with Clipchamp](https://github.com/user-attachments/assets/4ca511d2-efd4-4689-a167-e625abfc2d75)

## Project Overview
This project is a racing line simulation that allows users to draw a track and optimizes the best racing line using machine learning. The simulation incorporates realistic car physics, including velocity, steering angles, and collision detection, to determine the best path around the track.

## Features

### Advanced Car Physics
* Velocity and Steering Angle: The car's movement is calculated based on its current velocity and steering angle.
* Maximum Steering Angle: The steering is limited by physics such as traction, downforce, and mass to ensure realism.
* Throttle Control: The simulation updates the velocity based on throttle position, improving the control and accuracy of acceleration and deceleration.
* Collision Detection: Improved collision detection using masks ensuring accurate detection of crashes, even when the car turns and rotates.

### NEAT Maching Learing Integration
* NEAT Evolutionary Algorithm: Used to evolve a set of cars to optimize the racing line.
* Inputs: The NEAT model currently uses 10 inputs including: velocity, steering angle, max steering angle, and 7 distances to the track walls
* Outputs: It currently only has 2 outputs including throttle position and steering wheel position
* Fitness Evaluation: Primarily based on minimizing lap times while avoiding crashes.

### User Interaction
* Track Drawing: Users can interactively draw custom tracks that the AI will then attempt to optimize the racing line for.

## Planned Features
* UI Enhancements: A more intuitive user interface is planned to allow users to easily draw tracks, view real-time simulation data, and adjust parameters.
* Performance Optimization: Further optimization of car physics and NEAT training to speed up convergence and improve overall racing line accuracy.

## How to Run
1. Clone the repository.
2. Install dependencies:
![image](https://github.com/user-attachments/assets/b1a37e0b-4619-4b8e-8c83-3cdbeba520c6)
3. Run the simulation:
![image](https://github.com/user-attachments/assets/0e81b8fb-419b-4bf9-9bab-e7bd30d170bb)
4. Draw a track and let the AI optimize the racing line!
