import pygame
import math

class Car: 
    def __init__(self):
        # Load the car
        self.f1CarImage = pygame.image.load("images/f1Car.png")
        self.f1CarImage = pygame.transform.scale(self.f1CarImage, (50, 25)) 

        # Position
        self.carX = 0
        self.carY = 0
        self.carAngle = 0 # Angle in relation to the screen
        self.currentWheelAngle = 0
        self.maxWheelAngle = math.radians(18)

        self.frontCast = 0
        self.leftCast = 0
        self.rightCast = 0

        # Physics
        # These stats are based on real f1 cars

        # Car's characteristics
        self.mass = 100 #lbs
        self.coefficientOfFriction = 1.5  # Typical for F1 on a dry track
        self.downforce = 5000  # lbs (estimate based on F1 car downforce)
        self.downforceNewtons = self.downforce * 4.44822  # Convert to Newtons
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
            throttleValue = (self.throttlePosition - 0.5) * 2  # Scale to [0, 1]
            self.velocity = min(self.velocity + self.acceleration * dt * throttleValue, self.maxVelocity)
        elif self.throttlePosition < 0.5:
            # Brake (from neutral to full brake)
            brakeValue = (0.5 - self.throttlePosition) * 2  # Scale to [0, 1]
            self.velocity = max(self.velocity - self.deceleration * dt * brakeValue, 0)
        if self.currentWheelAngle < 0:
            self.currentWheelAngle = -min(abs(self.currentWheelAngle), self.calculateMaxSteeringAngle())
        else:
            self.currentWheelAngle = min(self.currentWheelAngle, self.calculateMaxSteeringAngle())
    
    # Calculate maximum lateral acceleration before losing traction. 
    def calculateMaxLateralAcceleration(self):
        # Convert mass to kg
        massKG = self.mass * 0.453592  # Convert lbs to kg
        
        # Gravitational force in m/s²
        g = 9.81

        # Maximum lateral acceleration: a_lat = μ * g + (D / m)
        # D is downforce in Newtons
        lateralAcceleration = (self.coefficientOfFriction * g) + (self.downforceNewtons / massKG)
        return lateralAcceleration  # m/s²
    # Calculate the turning radius based on speed and max lateral acceleration
    def calculateTurningRadius(self):
        # Get maximum lateral acceleration
        maxLateralAceeleration = self.calculateMaxLateralAcceleration()

        # Convert velocity from ft/s to m/s
        velocityMeterSecond = self.velocity * 0.3048

        # Calculate turning radius: R = v² / a_lat
        if maxLateralAceeleration > 0:
            turingRadius = (velocityMeterSecond ** 2) / maxLateralAceeleration
            return turingRadius  # meters
        else:
            return float('inf')  # If lateral acceleration is 0, turning radius is infinite

        # Calculate the max steering angle before losing traction
    def calculateMaxSteeringAngle(self):
        turingRadius = self.calculateTurningRadius()
        if turingRadius == 0:
            return 0
        
        # Steering angle in radians: θ = arctan(L / R)
        steeringAngleRadians = math.atan(self.wheelBase / (turingRadius / 0.3048))  # Convert radius to ft

        if steeringAngleRadians > self.maxWheelAngle:
            return self.maxWheelAngle

        return steeringAngleRadians

    def updateCarPosition(self, dt):
        if self.velocity > 0 and self.currentWheelAngle != 0:
            # Calculate turning radius
            turingRadius = self.wheelBase / math.tan(self.currentWheelAngle)
            
            # Calculate angular velocity (omega)
            angularVelocity = self.velocity / turingRadius * .5 #0.5 is used to scale it down
        else:
            # If the car is stationary or the wheel angle is 0, there should be no turning
            angularVelocity = 0

        # Update heading angle only if there's angular velocity
        if angularVelocity != 0:
            self.carAngle += angularVelocity * dt

        # Update car's position based on the velocity and heading angle
        self.carX += self.velocity * math.cos(self.carAngle) * dt
        self.carY += self.velocity * math.sin(self.carAngle) * dt

    def displayCar(self, screen):
        # Rotate the car image based on the car's current angle (in degrees)
        rotatedCarImage = pygame.transform.rotate(self.f1CarImage, -math.degrees(self.carAngle))

        # Get the rect of the rotated image to center it correctly
        rotatedRect = rotatedCarImage.get_rect(center=(self.carX, self.carY))

        # Blit (draw) the rotated car image on the screen
        screen.blit(rotatedCarImage, rotatedRect.topleft)

    def castLine(self, screen, angleOffset=0, maxDistance=500):
        # Adjust the car's direction by the angle offset (for left or right rays)
        adjustedAngle = self.carAngle + angleOffset

        # Get the direction vector based on the adjusted angle
        directionX = math.cos(adjustedAngle)
        directionY = math.sin(adjustedAngle)

        # Define the color white (255, 255, 255)
        white = (255, 255, 255)

        # Set up the starting position (front of the car)
        startX = self.carX
        startY = self.carY

        # Initialize end point (which will be the first white pixel hit or max distance)
        endX, endY = startX, startY

        # Move along the direction vector, checking for white pixels
        for i in range(maxDistance):
            # Calculate the next point along the line
            currentX = int(startX + directionX * i)
            currentY = int(startY + directionY * i)

            # Check if the point is within the screen bounds
            if 0 <= currentX < screen.get_width() and 0 <= currentY < screen.get_height():
                # Get the pixel color at the current point
                color = screen.get_at((currentX, currentY))

                # Check if the color is white
                if color == white:
                    endX, endY = currentX, currentY
                    break
            else:
                # Stop if we're outside the screen
                break

        # Draw a line from the front of the car to the first white pixel (or max distance)
        pygame.draw.line(screen, (255, 0, 0), (startX, startY), (endX, endY), 2)

        return math.hypot(endX - startX, endY - startY)

    # Wrapper function to cast all three lines (front, left, right)
    def castLines(self, screen):
        # Cast line straight ahead
        self.frontCast = self.castLine(screen)

        # Cast line 45 degrees to the left
        self.leftCast = self.castLine(screen, math.radians(-45))

        # Cast line 45 degrees to the right
        self.rightCast = self.castLine(screen, math.radians(45))