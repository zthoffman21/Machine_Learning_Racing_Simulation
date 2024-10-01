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
        self.carAngle = 0 # Angle in relation to the screen
        self.currentWheelAngle = 0
        self.maxWheelAngle = math.radians(18)

        # Physics
        # These stats are based on real f1 cars

        # Car's characteristics
        self.mass = 100 #lbs
        self.coefficient_of_friction = 1.5  # Typical for F1 on a dry track
        self.downforce = 5000  # lbs (estimate based on F1 car downforce)
        self.downforce_newtons = self.downforce * 4.44822  # Convert to Newtons
        self.wheelBase = 8 #ft

        # Car's kinematic characteristics
        self.velocity = 0 #ft/s
        self.maxVelocity = 342 #ft/s
        self.torque = 97624 # Calculated from existing mass, accelertaion, and wheel radius
        self.brakingPower = 42216 # Calculated from existing mass, deceleration, and wheel radius
        self.wheelRadius = 1.5 #ft
        self.deceleration = self.brakingPower/ (self.mass * self.wheelRadius) #ft/s^2
        self.acceleration = self.torque/ (self.mass * self.wheelRadius) #ft/s^2
        self.throttlePosition = .5 # 0-1 with x<.5 = decelerating and x>.5 = accelerating
        

        self.toPixelMult = .5 # Used to convert distance to pixels

    def updateVelocity(self, dt):
        # Throttle range: [0, 1] where:
        # 0 = full brake, 0.5 = neutral, 1 = full throttle
        if self.throttlePosition > 0.5:
            # Accelerate (from neutral to full throttle)
            throttle_value = (self.throttlePosition - 0.5) * 2  # Scale to [0, 1]
            self.velocity = min(self.velocity + self.acceleration * dt * throttle_value, self.maxVelocity)
        elif self.throttlePosition < 0.5:
            # Brake (from neutral to full brake)
            brake_value = (0.5 - self.throttlePosition) * 2  # Scale to [0, 1]
            self.velocity = max(self.velocity - self.deceleration * dt * brake_value, 0)
    
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
        steering_angle_radians = math.atan(self.wheelBase / (turning_radius / 0.3048))  # Convert radius to ft

        # Convert to degrees
        steering_angle_degrees = math.degrees(steering_angle_radians)

        if steering_angle_radians > self.maxWheelAngle:
            return self.maxWheelAngle

        return steering_angle_degrees

    def update_car_position(self, dt):
         # Limit the steering angle to a reasonable range (30 degrees in radians)
        # self.currentWheelAngle = max(-self.maxWheelAngle, min(self.currentWheelAngle, self.maxWheelAngle))

        if self.velocity > 0 and self.currentWheelAngle != 0:
            # Calculate turning radius
            turning_radius = self.wheelBase / math.tan(self.currentWheelAngle)
            
            # Calculate angular velocity (omega)
            angular_velocity = self.velocity / turning_radius * .5 #0.5 is used to scale it down
        else:
            # If the car is stationary or the wheel angle is 0, there should be no turning
            angular_velocity = 0

        # Update heading angle only if there's angular velocity
        if angular_velocity != 0:
            self.carAngle += angular_velocity * dt

        # Update car's position based on the velocity and heading angle
        self.car_x += self.velocity * math.cos(self.carAngle) * dt
        self.car_y += self.velocity * math.sin(self.carAngle) * dt

    def display_car(self, screen):
        # Rotate the car image based on the car's current angle (in degrees)
        rotated_car_image = pygame.transform.rotate(self.f1_car_image, -math.degrees(self.carAngle))

        # Get the rect of the rotated image to center it correctly
        rotated_rect = rotated_car_image.get_rect(center=(self.car_x, self.car_y))

        # Blit (draw) the rotated car image on the screen
        screen.blit(rotated_car_image, rotated_rect.topleft)

    def cast_line_to_first_white_pixel(self, screen, angle_offset=0, max_distance=500):
        # Adjust the car's direction by the angle offset (for left or right rays)
        adjusted_angle = self.carAngle + angle_offset

        # Get the direction vector based on the adjusted angle
        direction_x = math.cos(adjusted_angle)
        direction_y = math.sin(adjusted_angle)

        # Define the color white (255, 255, 255)
        white = (255, 255, 255)

        # Set up the starting position (front of the car)
        start_x = self.car_x
        start_y = self.car_y

        # Initialize end point (which will be the first white pixel hit or max distance)
        end_x, end_y = start_x, start_y

        # Move along the direction vector, checking for white pixels
        for i in range(max_distance):
            # Calculate the next point along the line
            current_x = int(start_x + direction_x * i)
            current_y = int(start_y + direction_y * i)

            # Check if the point is within the screen bounds
            if 0 <= current_x < screen.get_width() and 0 <= current_y < screen.get_height():
                # Get the pixel color at the current point
                color = screen.get_at((current_x, current_y))

                # Check if the color is white
                if color == white:
                    end_x, end_y = current_x, current_y
                    break
            else:
                # Stop if we're outside the screen
                break

        # Draw a line from the front of the car to the first white pixel (or max distance)
        pygame.draw.line(screen, (255, 0, 0), (start_x, start_y), (end_x, end_y), 2)

        return math.hypot(end_x - start_x, end_y - start_y)

    # Wrapper function to cast all three lines (front, left, right)
    def cast_lines(self, screen):
        # Cast line straight ahead
        front = self.cast_line_to_first_white_pixel(screen)

        # Cast line 45 degrees to the left
        left = self.cast_line_to_first_white_pixel(screen, math.radians(-45))

        # Cast line 45 degrees to the right
        right = self.cast_line_to_first_white_pixel(screen, math.radians(45))
        
        return front,left,right