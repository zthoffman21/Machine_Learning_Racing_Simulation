# Racing Line Simulation

![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)
![Pygame Version](https://img.shields.io/badge/Pygame-2.0%2B-green)
![NEAT-Python](https://img.shields.io/badge/NEAT--Python-2.12.0-brightgreen)
![Tkinter](https://img.shields.io/badge/Tkinter-Standard%20Library-blue)

![Project Image](https://github.com/user-attachments/assets/77353796-b563-40ac-98d0-ff4d32da28bc)

## Table of Contents
- [Project Overview](#project-overview)
- [Main Menus](#main-menus)
- [Modes](#modes)
  - [Best Time](#best-time)
  - [Head-to-Head](#head-to-head)
- [Features](#features)
  - [Advanced Car Physics](#advanced-car-physics)
  - [NEAT Machine Learning Integration](#neat-machine-learning-integration)
  - [Custom Track Creation](#custom-track-creation)
- [How to Run](#how-to-run)
- [Usage](#usage)
- [Contributing](#contributing)

## Project Overview
This project is a racing line simulation that allows users to draw a track and optimizes the best racing line using machine learning. The simulation incorporates realistic car physics, including velocity, steering angles, and collision detection, to determine the best path around the track.

## Main Menus
![Main Menus](https://github.com/user-attachments/assets/8b309275-7b8e-47ca-a3fa-f3b16fd46234)
![Main Menus](https://github.com/user-attachments/assets/f4c35741-9e2f-49f4-b308-e4c4e2a406b4)
![Main Menus](https://github.com/user-attachments/assets/a1ea3461-7efe-4640-b951-c7834583e5b9)

## Modes

### Best Time
Watch as AI-controlled cars strive for record-breaking lap times using advanced NEAT-driven neural networks.  
Best Time Mode focuses on optimizing speed, precision, and efficiency, showcasing the pinnacle of AI performance as it navigates tracks with unparalleled agility.

### Head-to-Head
Engage in competitive racing as the Red and Green AI teams battle it out on the track. Head-to-Head Mode allows you to customize key parameters for both teams' cars, enabling tailored strategies and performance adjustments. Watch as the NEAT-driven neural networks simultaneously train and evolve for each team, with real-time visualizations showcasing their progress and interactions. Experience dynamic races where strategy meets evolution, providing insightful comparisons of AI-driven performance.

## Features

### Advanced Car Physics
* **Velocity and Steering Angle:** The car's movement is calculated based on its current velocity and steering angle.
* **Maximum Steering Angle:** The steering is limited by physics such as traction, downforce, and mass to ensure realism.
* **Throttle Control:** The simulation updates the velocity based on throttle position, improving the control and accuracy of acceleration and deceleration.
* **Collision Detection:** Improved collision detection using masks ensuring accurate detection of crashes, even when the car turns and rotates.

### NEAT Machine Learning Integration
* **NEAT Evolutionary Algorithm:** Used to evolve a set of cars to optimize the racing line.
* **Inputs:** The NEAT model currently uses 10 inputs including: velocity, steering angle, max steering angle, and 7 distances to the track walls.
* **Outputs:** It currently only has 2 outputs including throttle position and steering wheel position.
* **Fitness Evaluation:** Primarily based on minimizing lap times while avoiding crashes.

### Custom Track Creation
![Custom Track Creation](https://github.com/user-attachments/assets/15144a13-b725-4ee4-a65a-be9bcb6d0447)
<br>
Create and design your own racing tracks with our intuitive track creation tool. Customize every curve and straight to challenge the AI and optimize your racing strategies.

## How to Run
1. **Clone the Repository**
    ```bash
    git clone https://github.com/zthoffman21/racing-line-simulation.git
    cd racing-line-simulation
    ```

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Simulation**
    ```bash
    python main.py
    ```

4. **Draw a Track and Optimize**
    - Use the track creation tool to design your racing track.
    - Select the desired mode (Best Time or Head-to-Head) and let the AI optimize the racing line.

## Usage

### Best Time Mode
1. Select **Best Time Mode** from the main menu.
2. Observe as AI-controlled cars attempt to achieve the fastest lap times.
3. Monitor the AI's progress and view lap statistics.

### Head-to-Head Mode
1. Select **Head-to-Head Mode** from the main menu.
2. Customize key parameters for both the Red and Green AI teams.
3. Start the simulation to watch both teams compete simultaneously.
4. Analyze real-time visualizations to compare performance metrics.

### Custom Track Creation
1. Navigate to the **Custom Track Creation** section.
2. Use the drawing tools to design your unique racing track.
3. Save and start simulations on your custom track.
4. Hit 1-5 to change brush size, 'w' for white and 'b' for black, and 'c' to clear 

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the Repository**
2. **Create a Feature Branch**
    ```bash
    git checkout -b feature/YourFeature
    ```
3. **Commit Your Changes**
    ```bash
    git commit -m "Add your feature"
    ```
4. **Push to the Branch**
    ```bash
    git push origin feature/YourFeature
    ```
5. **Open a Pull Request**
