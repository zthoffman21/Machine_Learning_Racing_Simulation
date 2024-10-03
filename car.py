import pygame
import math

class Car: 
    def __init__(self, x, y):
        # Load the car
        self.f1CarImage = pygame.image.load("images/f1Car.png")
        self.f1CarImage = pygame.transform.scale(self.f1CarImage, (50, 25)) 

        self.crashed = False
        self.firstLap = False
        self.hitFinishLine = False
        self.leftFinishLine = True
        self.lapStart = 0
        self.totalLaps = []

        # Position
        self.carX = x
        self.carY = y
        self.carAngle = 0 # Angle in relation to the screen
        self.currentWheelAngle = 0
        self.maxWheelAngle = math.radians(20)

        self.frontCast = 0
        self.leftCast = 0
        self.rightCast = 0
        self.left30AngleCast = 0
        self.right30AngleCast = 0
        self.left45AngleCast = 0
        self.right45AngleCast = 0

        # Physics
        # These stats are based on real f1 cars, but multipliers added for user experience

        # Car's characteristics
        self.mass = 1760  # lbs
        self.coefficientOfFriction = 1.8
        self.downforce = 4500  # lbs
        self.downforceNewtons = self.downforce * 4.44822  # Convert to Newtons
        self.wheelBase = 8  # ft

        # Car's kinematic characteristics
        self.velocity = 0  # ft/s
        self.minimunVelocity = 200 
        self.maxVelocity = 330 * 1.3  # ft/s (~225 mph) multiplier added for user experience 
        self.passedMin = False
        self.minVelAch = 0

        self.torque = 1000  # lb-ft
        self.brakingPower = 30000  # adjusted to reflect braking forces of 4-5 Gs
        self.wheelRadius = 1.2  # ft
        self.deceleration = self.brakingPower / (self.mass * self.wheelRadius) * 100  # ft/s^2-- multiplier added for user experience
        self.acceleration = self.torque / (self.mass * self.wheelRadius) * 1000  # ft/s^2-- multiplier added for user experience
        self.throttlePosition = .5 # 0-1 with x<.5 = decelerating and x>.5 = accelerating
    
    def updateVelocity(self, dt):
        # Throttle range: [0, 1] where:
        # 0 = full brake, 0.5 = neutral, 1 = full throttle
        if self.throttlePosition > 0.5:
            # Accelerate (from neutral to full throttle)
            throttleValue = (self.throttlePosition - 0.5) * 3  # Scale to [0, 1] and increase multiplier
            self.velocity = min(self.velocity + self.acceleration * dt * throttleValue, self.maxVelocity)
        elif self.throttlePosition < 0.5:
            # Brake (from neutral to full brake)
            brakeValue = (0.5 - self.throttlePosition) * 2  # Scale to [0, 1]
            self.velocity = max(self.velocity - self.deceleration * dt * brakeValue, 0)

        # Forces a min speed
        if self.passedMin:
            self.velocity = max(self.velocity, self.minimunVelocity)
        else:
            self.velocity = max(self.velocity, self.minVelAch)
        if not self.passedMin and self.velocity > self.minimunVelocity:
            self.passedMin = True

        # Update car's wheel angle if it is breaking the calculated max angle based on the new velocity
        self.maxWheelAngle = self.calculateMaxSteeringAngle()
        if self.currentWheelAngle < 0:
                self.currentWheelAngle = max(-self.maxWheelAngle, self.currentWheelAngle)  
        else:
                self.currentWheelAngle = min(self.maxWheelAngle, self.currentWheelAngle)  
    
    # Calculate maximum lateral acceleration before losing traction. 
    def calculateMaxLateralAcceleration(self):
        massKG = self.mass * 0.453592  # Convert lbs to kg
        # Gravitational force in m/s²
        g = 9.81

        # Maximum lateral acceleration: a_lat = μ * g + (D / m)
        lateralAcceleration = (self.coefficientOfFriction * g) + (self.downforceNewtons / (massKG * .075)) # multiplier added to improve user exeperience
        return lateralAcceleration  # m/s²
    def calculateTurningRadius(self):
        # Get maximum lateral acceleration
        maxLateralAceeleration = self.calculateMaxLateralAcceleration()

        # Convert velocity from ft/s to m/s
        velocityMeterSecond = self.velocity * 0.3048

        # Calculate turning radius: R = v²
        if maxLateralAceeleration > 0:
            turingRadius = (velocityMeterSecond ** 2) / maxLateralAceeleration
            return turingRadius  # meters
        else:
            return float('inf')  # If lateral acceleration is 0, turning radius is infinite

        # Calculate the max steering angle before losing traction
    def calculateMaxSteeringAngle(self):
        turingRadius = self.calculateTurningRadius()
        if turingRadius == 0:
            return self.maxWheelAngle
        
        # Steering angle in radians: θ = arctan(L / R)
        steeringAngleRadians = math.atan(self.wheelBase / (turingRadius / 0.3048))  # Convert radius to ft

        # Caps the wheel angle to a maxium of 20 degrees
        if math.degrees(steeringAngleRadians) > 20: 
            return math.radians(20)
        else:
            return steeringAngleRadians

    def updateCarPosition(self, dt):  
        self.updateVelocity(dt)
      
        if self.velocity > 0 and self.currentWheelAngle != 0:
            turingRadius = self.wheelBase / math.tan(self.currentWheelAngle)
            
            # Calculate angular velocity (omega)
            angularVelocity = self.velocity / turingRadius
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

        screen.blit(rotatedCarImage, rotatedRect.topleft)
        self.castLines(screen)

    def castLine(self, screen, angleOffset=0, maxDistance=500):
        adjustedAngle = self.carAngle + angleOffset

        # Get the direction vector based on the adjusted angle
        directionX = math.cos(adjustedAngle)
        directionY = math.sin(adjustedAngle)

        white = (255, 255, 255)

        startX = self.carX
        startY = self.carY
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

                if color == white:
                    endX, endY = currentX, currentY
                    break
            else:
                break

        # ** UNCOMMENT THIS TO SHOW THE RAYS THAT THE COMPUTER SEES **
        # pygame.draw.line(screen, (255, 0, 0), (startX, startY), (endX, endY), 2)

        return math.hypot(endX - startX, endY - startY)

    # Wrapper function to cast all three lines (front, left, right)
    def castLines(self, screen):
        # Cast line straight ahead
        self.frontCast = self.castLine(screen)

        # Cast line 90 degrees to the left
        self.leftCast = self.castLine(screen, math.radians(-90), 100)
        # Cast line 90 degrees to the right
        self.rightCast = self.castLine(screen, math.radians(90), 100)

        # Cast line 45 degrees to the left
        self.left45AngleCast = self.castLine(screen, math.radians(-45), 100)
        # Cast line 45 degrees to the right
        self.right45AngleCast = self.castLine(screen, math.radians(45), 100)

        # Cast line 30 degrees to the left
        self.left30AngleCast = self.castLine(screen, math.radians(-30), 100)
        # Cast line 30 degrees to the right
        self.right30AngleCast = self.castLine(screen, math.radians(30), 100)