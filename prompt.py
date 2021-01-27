import os
from tkinter import Tk, filedialog

def prompt_save_location():
    """Prompt the user for a directory to save output files"""
    curr_directory = os.getcwd()  # will get current working directory
    root = Tk()
    root.withdraw()
    root.filename = filedialog.askdirectory(
        initialdir = curr_directory,
        title="Select save location"
    )
    return root.filename


if __name__ == "__main__":
    l = prompt_save_location()
    print(l)