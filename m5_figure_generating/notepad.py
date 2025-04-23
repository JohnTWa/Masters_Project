from _SETUP_ import set_directory
set_directory()

import os
import tkinter as tk
import threading
import time

from m1_transmitting.FSK_main import FSK_main

def notepad(text_file_path):
    # Ensure the directory for the file exists
    dir_path = os.path.dirname(text_file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    root = tk.Tk()
    root.title("Notepad")

    # Add a small grey border to the edge of the Text widget
    border_frame = tk.Frame(root, bg='lightgrey')
    border_frame.pack(expand=True, fill='both', padx=2, pady=2)

    # Create a Text widget for writing notes and pack into the border frame
    text_widget = tk.Text(border_frame, wrap='word')
    text_widget.pack(expand=True, fill='both', padx=1, pady=1)

    # Define save functionality
    def save_file():
        content = text_widget.get("1.0", tk.END)
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Autosave function: update file every 1 second
    def autosave():
        save_file()
        root.after(1000, autosave)  # Save every 1 second

    # Window close event
    def on_close():
        save_file()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Create the menubar
    menubar = tk.Menu(root)

    # File menu
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Save", command=save_file)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=on_close)
    menubar.add_cascade(label="File", menu=filemenu)

    # Edit menu
    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Cut", command=lambda: text_widget.event_generate("<<Cut>>"))
    editmenu.add_command(label="Copy", command=lambda: text_widget.event_generate("<<Copy>>"))
    editmenu.add_command(label="Paste", command=lambda: text_widget.event_generate("<<Paste>>"))
    menubar.add_cascade(label="Edit", menu=editmenu)

    # Format menu (no actions)
    formatmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Format", menu=formatmenu)

    # View menu (no actions)
    viewmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="View", menu=viewmenu)

    # Help menu (no actions)
    helpmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=helpmenu)

    # Configure the menubar
    root.config(menu=menubar)

    # Start the autosave loop
    autosave()

    # Start the Tkinter event loop (this call blocks until the window is closed)
    root.mainloop()

def notepad_and_FSK_transmission(text_file_path):
    """
    Runs the notepad and continuously monitors the text file for changes.
    FSK_main is executed only if the file has been updated (i.e. the user has started typing)
    and if a previous FSK transmission is not still running.
    """
    # Lock to ensure only one instance of FSK_main is running at a time.
    fsk_lock = threading.Lock()

    # Initialize last_content with the file's current contents.
    try:
        with open(text_file_path, "r", encoding="utf-8") as f:
            last_content = f.read()
    except Exception:
        last_content = ""

    # Event to signal the monitoring thread to stop once notepad is closed.
    stop_event = threading.Event()

    def monitor_file():
        nonlocal last_content
        while not stop_event.is_set():
            time.sleep(1)  # Poll the file every second.
            # Skip checking if FSK_main is currently running.
            if fsk_lock.locked():
                continue

            try:
                with open(text_file_path, "r", encoding="utf-8") as f:
                    current_content = f.read()
            except Exception:
                current_content = ""

            # Only run FSK_main if the file content has changed (i.e. user began typing/updated it)
            if current_content != last_content:
                last_content = current_content
                if fsk_lock.acquire(blocking=False):
                    try:
                        print("File updated; starting FSK transmission...")
                        FSK_main()
                        print("FSK transmission complete.")
                    finally:
                        fsk_lock.release()
                else:
                    print("FSK_main already running; skipping this update.")

    # Start the file monitoring thread as a daemon.
    monitor_thread = threading.Thread(target=monitor_file, daemon=True)
    monitor_thread.start()

    # Run the notepad (blocking call).
    notepad(text_file_path)

    # Once the notepad window is closed, signal the monitor thread to stop.
    stop_event.set()
    monitor_thread.join()


# Example usage:
notepad_and_FSK_transmission('files/t1_transmission_text.txt')