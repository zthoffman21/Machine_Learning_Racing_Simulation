import pygame
import math

class Car: 
    def __init__(self):
        # Load the car
        self.f1_car_image = pygame.image.load("images/f1Car.png")
        self.f1_car_image = pygame.transform.scale(self.f1_car_image, (50, 25)) 

        # Position
        self.car_x = 0
        self.car_y = 0

        self.currentThrottlePosition = 0 # 0-1
        self.currentBrakePosition = 0 # 0-1

        # Physics
        # These stats are based on real f1 cars
        self.mass = 1759 #lbs
        self.velocity = 0 #ft/s
        self.maxVelocity = 342  #ft/s
        self.torque = 97624 # Calculated from existing mass, accelertaion, and wheel radius
        self.brakingPower = 422160 # Calculated from existing mass, deceleration, and wheel radius
        self.wheelRadius = 1.5 #ft
        self.deceleration = self.brakingPower/ (self.mass * self.wheelRadius) #ft/s^2
        self.acceleration = self.torque/ (self.mass * self.wheelRadius) #ft/s^2
        
        self.angularVelocity = 0
        self.maxAngularVelocity = 50

        self.toPixelMult = .5 # Used to convert distance to pixels

        # Grip and downforce properties
        self.coefficient_of_friction = 1.5  # Typical for F1 on a dry track
        self.downforce = 5000  # lbs (estimate based on F1 car downforce)
        self.downforce_newtons = self.downforce * 4.44822  # Convert to Newtons

    def accelerate(self):
        self.velocity = min(self.velocity + self.acceleration, self.maxVelocity)

    def brake(self):
        self.velocity = max(self.velocity - self.deceleration, 0)

    def pixelsNeededToStop(self):
        timeToStop = self.velocity / self.brakingPower
        distance = self.velocity * timeToStop + .5 * -self.brakingPower * timeToStop**2
        pixelsToStop = distance * self.toPixelMult
        return pixelsToStop
    
    # Calculate maximum lateral acceleration before losing traction. 
    def calculate_max_lateral_acceleration(self):
        # Convert mass to kg
        mass_kg = self.mass * 0.453592  # Convert lbs to kg
        
        # Gravitational force in m/s²
        g = 9.81

        # Maximum lateral acceleration: a_lat = μ * g + (D / m)
        # D is downforce in Newtons
        lateral_acceleration = (self.coefficient_of_friction * g) + (self.downforce_newtons / mass_kg)
        return lateral_acceleration  # m/s²

    # Calculate the turning radius based on speed and max lateral acceleration
    def calculate_turning_radius(self):
        # Get maximum lateral acceleration
        max_lateral_acceleration = self.calculate_max_lateral_acceleration()

        # Convert velocity from ft/s to m/s
        velocity_m_s = self.velocity * 0.3048

        # Calculate turning radius: R = v² / a_lat
        if max_lateral_acceleration > 0:
            turning_radius = (velocity_m_s ** 2) / max_lateral_acceleration
            return turning_radius  # meters
        else:
            return float('inf')  # If lateral acceleration is 0, turning radius is infinite

        # Calculate the max steering angle before losing traction
    def calculate_max_steering_angle(self):
        turning_radius = self.calculate_turning_radius()
        if turning_radius == 0:
            return 0
        
        # Steering angle in radians: θ = arctan(L / R)
        steering_angle_radians = math.atan(self.wheelbase / (turning_radius / 0.3048))  # Convert radius to ft

        # Convert to degrees
        steering_angle_degrees = math.degrees(steering_angle_radians)

        return steering_angle_degrees

    def update_velocity(self, new_velocity):
        # Update the car's velocity (in ft/s)
        self.velocity = min(new_velocity, self.maxVelocity)
