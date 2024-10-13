import tkinter as tk

class RacingConfig():
    def __init__(self):

        self.window = tk.Tk()
        self.window.geometry("800x800")
        self.window.minsize(800, 800)
        self.window.maxsize(800, 800)
        self.window.title("Simulation Configuration")
        self.window.iconphoto(True, tk.PhotoImage(file="images/f1Car.png"))

        self.frames = {}
        
        self.headToHeadMode = None

        # Red Team variables
        self.accelerationMultRed = None
        self.decelerationMultRed = None
        self.downforceMultRed = None
        self.maxSpeedMultRed = None
        # Green Team variables
        self.accelerationMultGreen = None
        self.decelerationMultGreen = None
        self.downforceMultGreen = None
        self.maxSpeedMultGreen = None

        # Both Mode variables
        self.usingExistingTrack = None
        self.existingTrackPath = None
        self.usingExistingNetwork = None
        self.existingNetworkPath = None

        # Configure the grid for the main window to allow frames to expand
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Create and store frames (StartPage, HeadToHeadPage, BestTimePage)
        self.frames["StartPage"] = StartPage(self, self.window)
        self.frames["HeadToHeadPage"] = HeadToHeadPage(self, self.window)
        self.frames["BestTimePage"] = BestTimePage(self, self.window)

        # Show the StartPage frame by default
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Display the frame for the given page name'''
        frame = self.frames[page_name].frame
        frame.tkraise()  # Bring the frame to the top

    def run(self):
        '''Start the main loop of the app'''
        self.window.mainloop()
    
    def returnHeadToHeadInfo(self, accelerationMultRed, decelerationMultRed, downforceMultRed, maxSpeedMultRed, accelerationMultGreen, decelerationMultGreen, downforceMultGreen, maxSpeedMultGreen, usingExistingTrack, existingTrackPath):
        # Red Team variables
        self.accelerationMultRed = accelerationMultRed
        self.decelerationMultRed = decelerationMultRed
        self.downforceMultRed = downforceMultRed
        self.maxSpeedMultRed = maxSpeedMultRed
        # Green Team variables
        self.accelerationMultGreen = accelerationMultGreen
        self.decelerationMultGreen = decelerationMultGreen
        self.downforceMultGreen = downforceMultGreen
        self.maxSpeedMultGreen = maxSpeedMultGreen

        # Both Mode variables
        self.usingExistingTrack = usingExistingTrack
        self.existingTrackPath = existingTrackPath
        self.headToHeadMode = True
        self.window.destroy()

    def returnBestTimeInfo(self, accelerationMult, decelerationMult, downforceMult, maxSpeedMult, usingExistingTrack, existingTrackPath, usingExistingNetwork, existingNetworkPath):
        self.accelerationMult = accelerationMult
        self.decelerationMult = decelerationMult
        self.downforceMult = downforceMult
        self.maxSpeedMult = maxSpeedMult
        self.usingExistingTrack = usingExistingTrack
        self.existingTrackPath = existingTrackPath
        self.usingExistingNetwork = usingExistingNetwork
        self.existingNetworkPath = existingNetworkPath

        self.headToHeadMode = False
        self.window.destroy()

class StartPage():
    def __init__(self, root, window):
        self.frame = tk.Frame(window)
        
        # Configure the grid so the frame expands to fit the window
        self.frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure the layout inside the frame
        total_columns = 5
        total_rows = 15

        # Configure the grid columns and rows to behave as expected
        for i in range(total_columns):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(total_rows):
            self.frame.grid_rowconfigure(i, weight=1)

        # Creating components
        header = tk.Label(self.frame, text="F1 Racing Simulation", font=("Lucida Console", 15))
        head_to_head_button = tk.Button(self.frame, text="Head to Head", command=lambda: root.show_frame("HeadToHeadPage"))
        best_time_button = tk.Button(self.frame, text="Best Time", command=lambda: root.show_frame("BestTimePage"))

        # Placing components on the frame
        header.grid(row=5, column=0, columnspan=total_columns)
        head_to_head_button.grid(row=6, column=2)
        best_time_button.grid(row=7, column=2)

class HeadToHeadPage():
    def __init__(self, root, window):
        self.frame = tk.Frame(window)
        
        # Configure the grid so the frame expands to fit the window
        self.frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure the layout inside the frame
        totalColumns = 5
        totalRows = 15
        
        # Red Team variables
        accelerationMultRed = tk.DoubleVar()
        decelerationMultRed = tk.DoubleVar()
        downforceMultRed = tk.DoubleVar()
        maxSpeedMultRed = tk.DoubleVar()
        # Green Team variables
        accelerationMultGreen = tk.DoubleVar()
        decelerationMultGreen = tk.DoubleVar()
        downforceMultGreen = tk.DoubleVar()
        maxSpeedMultGreen = tk.DoubleVar()

        usingExistingTrack = tk.BooleanVar()
        existingTrackPath = tk.StringVar()        

        # Configure the grid columns and rows to behave as expected
        for i in range(totalColumns):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(totalRows):
            self.frame.grid_rowconfigure(i, weight=1)

        # Creating components
        header = tk.Label(self.frame, text="Head to Head Mode", font=("Lucida Console", 15))
        backButton = tk.Button(self.frame, text="Back to Main Menu", command=lambda: root.show_frame("StartPage"))
        continueButton = tk.Button(self.frame, text="Continue", command=lambda: root.returnHeadToHeadInfo(accelerationMultRed.get(), decelerationMultRed.get(), downforceMultRed.get(), maxSpeedMultRed.get(), accelerationMultGreen.get(), decelerationMultGreen.get(), downforceMultGreen.get(), maxSpeedMultGreen.get(), usingExistingTrack.get(), existingTrackPath.get()))
        redTeamLabel = tk.Label(self.frame, text="Red Team", font=("Lucida Console", 15))
        greenTeamLabel = tk.Label(self.frame, text="Green Team", font=("Lucida Console", 15))
        # Red Team Labels
        accelerationLabelRed = tk.Label(self.frame, text="Acceleration Mult.", font=("Lucida Console", 10))
        decelerationLabelRed = tk.Label(self.frame, text="Deceleration Mult.", font=("Lucida Console", 10))
        downforceLabelRed = tk.Label(self.frame, text="Downforce Mult.", font=("Lucida Console", 10))
        maxSpeedLabelRed = tk.Label(self.frame, text="Max Speed Mult.", font=("Lucida Console", 10))
        # Green Team Labels
        accelerationLabelGreen = tk.Label(self.frame, text="Acceleration Mult.", font=("Lucida Console", 10))
        decelerationLabelGreen = tk.Label(self.frame, text="Deceleration Mult.", font=("Lucida Console", 10))
        downforceLabelGreen = tk.Label(self.frame, text="Downforce Mult.", font=("Lucida Console", 10))
        maxSpeedLabelGreen = tk.Label(self.frame, text="Max Speed Mult.", font=("Lucida Console", 10))

        # Red Team sliders
        acclerationMultSliderRed = tk.Scale(self.frame, variable=accelerationMultRed, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        acclerationMultSliderRed.set(1.0)
        declerationMultSliderRed = tk.Scale(self.frame, variable=decelerationMultRed, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        declerationMultSliderRed.set(1.0)  
        downforceMultSliderRed = tk.Scale(self.frame, variable=downforceMultRed, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        downforceMultSliderRed.set(1.0)
        maxSpeedMultSliderRed = tk.Scale(self.frame, variable=maxSpeedMultRed, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        maxSpeedMultSliderRed.set(1.0)
        # Green Team sliders
        acclerationMultSliderGreen = tk.Scale(self.frame, variable=accelerationMultGreen, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        acclerationMultSliderGreen.set(1.0)
        declerationMultSliderGreen = tk.Scale(self.frame, variable=decelerationMultGreen, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        declerationMultSliderGreen.set(1.0)  
        downforceMultSliderGreen = tk.Scale(self.frame, variable=downforceMultGreen, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        downforceMultSliderGreen.set(1.0)
        maxSpeedMultSliderGreen = tk.Scale(self.frame, variable=maxSpeedMultGreen, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        maxSpeedMultSliderGreen.set(1.0)
        # Existing track 
        usingExistingTrackLabel = tk.Label(self.frame, text="Using Existing Track",  font=("Lucida Console", 12))
        usingExistingTrackCheckbox = tk.Checkbutton(self.frame, text="Yes", variable=usingExistingTrack, onvalue=1, offvalue=0)
        existingTrackPathLaebl = tk.Label(self.frame, text="Track Path",  font=("Lucida Console", 12))
        existingTrackPathLaeblExample = tk.Label(self.frame, text="(ex. images/hardTest.png)",  font=("Lucida Console", 10))
        existingTrackPathEntry = tk.Entry(self.frame, textvariable=existingTrackPath, font=("Lucida Console", 12))


        # Placing the components on the frame
        header.grid(row=0, column=0, columnspan=totalColumns, sticky="ew")
        backButton.grid(row=1, column=0, columnspan=totalColumns)
        continueButton.grid(row=2, column=0, columnspan=totalColumns)
        redTeamLabel.grid(row=3, column=0, columnspan=2)
        greenTeamLabel.grid(row=3, column=3, columnspan=2)

        # Red Team placement
        accelerationLabelRed.grid(row=4, column=0, sticky="e")   
        acclerationMultSliderRed.grid(row=4, column=1, sticky="w")   

        decelerationLabelRed.grid(row=5, column=0, sticky="e")
        declerationMultSliderRed.grid(row=5, column=1, sticky="w")

        downforceLabelRed.grid(row=6, column=0, sticky="e")
        downforceMultSliderRed.grid(row=6, column=1, sticky="w")

        maxSpeedLabelRed.grid(row=7, column=0, sticky="e")
        maxSpeedMultSliderRed.grid(row=7, column=1, sticky="w")

        # Green Team placement
        accelerationLabelGreen.grid(row=4, column=3, sticky="e")   
        acclerationMultSliderGreen.grid(row=4, column=4, sticky="w")   

        decelerationLabelGreen.grid(row=5, column=3, sticky="e")
        declerationMultSliderGreen.grid(row=5, column=4, sticky="w")   

        downforceLabelGreen.grid(row=6, column=3, sticky="e")
        downforceMultSliderGreen.grid(row=6, column=4, sticky="w")

        maxSpeedLabelGreen.grid(row=7, column=3, sticky="e")
        maxSpeedMultSliderGreen.grid(row=7, column=4, sticky="w")

        # Using existing track placement
        usingExistingTrackLabel.grid(row=10, column=0, columnspan=totalColumns, sticky="s")
        usingExistingTrackCheckbox.grid(row=11, column=0, columnspan=totalColumns, sticky="n")
        existingTrackPathLaebl.grid(row=12, column=0, columnspan=totalColumns, sticky="s")
        existingTrackPathLaeblExample.grid(row=14, column=0, columnspan=totalColumns, sticky="n")
        existingTrackPathEntry.grid(row=13, column=0, columnspan=totalColumns)


class BestTimePage():
    def __init__(self, root, window):
        self.frame = tk.Frame(window)
        
        # Configure the grid so the frame expands to fit the window
        self.frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure the layout inside the frame
        totalColumns = 5
        totalRows = 15
        
        accelerationMult = tk.DoubleVar()
        decelerationMult = tk.DoubleVar()
        downforceMult = tk.DoubleVar()
        maxSpeedMult = tk.DoubleVar()

        usingExistingTrack = tk.BooleanVar()
        existingTrackPath = tk.StringVar()        
        usingExistingNetwork = tk.BooleanVar()
        existingNetworkPath = tk.StringVar()


        # Configure the grid columns and rows to behave as expected
        for i in range(totalColumns):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(totalRows):
            self.frame.grid_rowconfigure(i, weight=1)

        # Creating components
        header = tk.Label(self.frame, text="Head to Head Mode", font=("Lucida Console", 15))
        backButton = tk.Button(self.frame, text="Back to Main Menu", command=lambda: root.show_frame("StartPage"))
        continueButton = tk.Button(self.frame, text="Continue", command=lambda: root.returnBestTimeInfo(accelerationMult.get(), decelerationMult.get(), downforceMult.get(), maxSpeedMult.get(), usingExistingTrack.get(), existingTrackPath.get(), usingExistingNetwork.get(), existingNetworkPath.get()))

        accelerationLabel = tk.Label(self.frame, text="Acceleration Mult.", font=("Lucida Console", 10))
        decelerationLabel = tk.Label(self.frame, text="Deceleration Mult.", font=("Lucida Console", 10))
        downforceLabel = tk.Label(self.frame, text="Downforce Mult.", font=("Lucida Console", 10))
        maxSpeedLabel = tk.Label(self.frame, text="Max Speed Mult.", font=("Lucida Console", 10))

        # Red Team sliders
        acclerationMultSlider = tk.Scale(self.frame, variable=accelerationMult, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        acclerationMultSlider.set(1.0)
        declerationMultSlider = tk.Scale(self.frame, variable=decelerationMult, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        declerationMultSlider.set(1.0)  
        downforceMultSlider = tk.Scale(self.frame, variable=downforceMult, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        downforceMultSlider.set(1.0)
        maxSpeedMultSlider = tk.Scale(self.frame, variable=maxSpeedMult, from_=0.1, to=2, resolution=0.1, orient=tk.HORIZONTAL)
        maxSpeedMultSlider.set(1.0)

        # Existing track        
        usingExistingTrackLabel = tk.Label(self.frame, text="Using Existing Track",  font=("Lucida Console", 12))
        usingExistingTrackCheckbox = tk.Checkbutton(self.frame, text="Yes", variable=usingExistingTrack, onvalue=1, offvalue=0)
        existingTrackPathLaebl = tk.Label(self.frame, text="Track Path",  font=("Lucida Console", 12))
        existingTrackPathLaeblExample = tk.Label(self.frame, text="(ex. images/hardTest.png)",  font=("Lucida Console", 10))
        existingTrackPathEntry = tk.Entry(self.frame, textvariable=existingTrackPath, font=("Lucida Console", 12))

        usingExistingNetworkLabel = tk.Label(self.frame, text="Using Existing Network",  font=("Lucida Console", 12))
        usingExistingNetworkCheckbox = tk.Checkbutton(self.frame, text="Yes", variable=usingExistingNetwork, onvalue=1, offvalue=0)
        existingNetworkPathLaebl = tk.Label(self.frame, text="Network Path",  font=("Lucida Console", 12))
        existingNetworkPathLaeblExample = tk.Label(self.frame, text="(ex. checkpoints/129-6.43)",  font=("Lucida Console", 10))
        existingNetworkPathEntry = tk.Entry(self.frame, textvariable=existingNetworkPath, font=("Lucida Console", 12))


        # Placing the components on the frame
        header.grid(row=0, column=0, columnspan=totalColumns, sticky="ew")
        backButton.grid(row=1, column=0, columnspan=totalColumns)
        continueButton.grid(row=2, column=0, columnspan=totalColumns)

        accelerationLabel.grid(row=4, column=1, sticky="e")   
        acclerationMultSlider.grid(row=4, column=3, sticky="w")   

        decelerationLabel.grid(row=5, column=1, sticky="e")
        declerationMultSlider.grid(row=5, column=3, sticky="w")

        downforceLabel.grid(row=6, column=1, sticky="e")
        downforceMultSlider.grid(row=6, column=3, sticky="w")

        maxSpeedLabel.grid(row=7, column=1, sticky="e")
        maxSpeedMultSlider.grid(row=7, column=3, sticky="w")


        # Using existing track placement
        usingExistingTrackLabel.grid(row=10, column=0, columnspan=2, sticky="s")
        usingExistingTrackCheckbox.grid(row=11, column=0, columnspan=2, sticky="n")
        existingTrackPathLaebl.grid(row=12, column=0, columnspan=2, sticky="s")
        existingTrackPathLaeblExample.grid(row=14, column=0, columnspan=2, sticky="n")
        existingTrackPathEntry.grid(row=13, column=0, columnspan=2)
        # Using existing network placement
        usingExistingNetworkLabel.grid(row=10, column=3, columnspan=2, sticky="s")
        usingExistingNetworkCheckbox.grid(row=11, column=3, columnspan=2, sticky="n")
        existingNetworkPathLaebl.grid(row=12, column=3, columnspan=2, sticky="s")
        existingNetworkPathLaeblExample.grid(row=14, column=3, columnspan=2, sticky="n")
        existingNetworkPathEntry.grid(row=13, column=3, columnspan=2)

if __name__ == "__main__":
    # Run the application
    racingConfigWindow = RacingConfig()
    racingConfigWindow.run()