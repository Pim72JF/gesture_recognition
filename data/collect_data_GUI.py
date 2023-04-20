import myo
import numpy as np
import time
import os
import tkinter as tk
from threading import Lock

rec_duration = 6

class EmgCollector(myo.DeviceListener):
    def __init__(self, start, name, forearm_circumference, gesture, gesture_index, root):
        self.name = name
        self.start = start
        self.forearm_circumference = forearm_circumference
        self.gesture = gesture
        self.gesture_index = gesture_index
        self.root = root
        self.emg_data = np.zeros((1, 8))
        self.lock = Lock()
        self.is_recording = False
        self.countdown_label = tk.Label(root, font=("Helvetica", 20))
        self.countdown_label.pack()

    def on_connected(self, event):
        event.device.stream_emg(True)

    def on_emg(self, event):
        if self.is_recording:
            self.emg_data = np.concatenate((self.emg_data, np.reshape(np.array(event.emg), (1, 8))), axis=0)

    def start_recording(self):
        # Start countdown timer
        countdown_secs = 5
        for i in range(countdown_secs):
            self.countdown_label.config(text=f"Recording {self.gesture} in {countdown_secs-i} seconds...")
            time.sleep(1)

        # Start recording
        self.is_recording = True
        self.emg_data = np.zeros((1, 8))
        self.countdown_label.config(text=f"Recording {self.gesture}...")

    def stop_recording(self):
        # Stop recording
        self.is_recording = False
        self.countdown_label.config(text=f"You may relax! Saving {self.gesture} data...")

        # Save EMG data to file
        emg_data_array = np.array(self.emg_data)
        filename = f"{self.name}/{self.gesture}_{self.gesture_index}.npy"
        np.save(filename, emg_data_array)

        # Increment gesture index
        self.countdown_label.config(text="")

def collect_emg_data(name, forearm_circumference, gesture, gesture_index):
    # Create participant directory if it doesn't exist
    if not os.path.exists(name):
        os.makedirs(name)

    # Initialize MYO and start recording
    myo.init(sdk_path='C:\\myo-sdk-win-0.9.0\\')
    hub = myo.Hub()
    for gesture_index in range(5):
        start = time.time()
        listener = EmgCollector(start, name, forearm_circumference, gesture, gesture_index, root)
        try:
            while hub.run(listener.on_event, 500):
                if not listener.is_recording:
                    listener.start_recording()
                else:
                    if len(listener.emg_data) >= 1150:
                        listener.stop_recording()
        except KeyboardInterrupt:
            print('\nQuit')

# Create GUI
root = tk.Tk()
root.title("EMG Data Collection")
root.geometry("400x300")

# Add participant name input
participant_label = tk.Label(root, text="Participant Name:")
participant_label.pack()
participant_entry = tk.Entry(root)
participant_entry.pack()

# Add forearm circumference input
forearm_label = tk.Label(root, text="Forearm Circumference (cm):")
forearm_label.pack()
forearm_entry = tk.Entry(root)
forearm_entry.pack()

# Add gesture dropdown menu
gesture_label = tk.Label(root, text="Gesture:")
gesture_label.pack()
gesture_var = tk.StringVar(root)
gesture_var.set("Neutral")
gesture_menu = tk.OptionMenu(root, gesture_var, "Neutral", "Open Hand", "Closed Hand", "Thumb Abduction", "Thumb Adduction", "Pronation", "Supination", "Pinch", "Tripod", "Point", "Lateral")
gesture_menu.pack()

# Add start button
start_button = tk.Button(root, text="Start", command=lambda: collect_emg_data(participant_entry.get(),
float(forearm_entry.get()),
gesture_var.get(),
0))
start_button.pack()

#Run GUI 
root.mainloop()