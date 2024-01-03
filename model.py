import os

class BeatMakerModel:
    def __init__(self):
        # Initialize your model's data structures here
        self.samples = ["None"]*8
        self.button_states = {}  # Initialize the button states dictionary
        self.sample_files = self.loadSampleFiles("samples")  # Load sample files at initialization
                
    def loadSampleFiles(self, sample_folder):
        # Load the list of .wav files from the specified folder
        sample_path = os.path.join(os.path.dirname(__file__), sample_folder)
        return [file for file in os.listdir(sample_path) if file.endswith(".wav")]

    def refreshSampleFiles(self):
        self.sample_files = self.loadSampleFiles("samples")

    def getSampleFilePath(self, sample_folder, file_name):
        # Return the full file path for the given sample file
        return os.path.join(os.path.dirname(__file__), sample_folder, file_name)

    def getSamples(self):
        # Return the list of sample files
        return self.sample_files
    
    # Methods to manipulate and retrieve data from the model
    def set_sample(self, row, sample):
        self.samples[row] = sample

    def clear_sample(self,row):
        self.samples[row] = "None"

    def clear_all_samples(self):
        self.samples = ["None"]*8
        print("Cleared all assigned samples")

    def toggle_button_state(self, row, col):
        # Toggle the state of the specified button
        if (row, col) not in self.button_states:
            self.button_states[(row, col)] = True  # Default to 'on' if not set
        else:
            self.button_states[(row, col)] = not self.button_states[(row, col)]
        return self.button_states[(row, col)]

    def get_button_state(self, row, col):
        # Return the current state of the specified button
        return self.button_states.get((row, col), False)  # Default to 'off' if not set

    def clear_button_state(self):
        self.button_states = {}
        print("Cleared all beats")
    
    def get_audio_index(self):
        state = self.button_states

        # Filter out the false items
        active_beats = [k for k, v in state.items() if v]

        # Group by row and collect columns
        grouped_by_row = {}
        for row, col in active_beats:
            if row in grouped_by_row:
                grouped_by_row[row].append(col)
            else:
                grouped_by_row[row] = [col]

        # Sort each group's columns and create a sorted list of tuples
        sorted_state = [(row, sorted(cols)) for row, cols in sorted(grouped_by_row.items())]

        return sorted_state

