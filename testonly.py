import tkinter as tk
import vlc

root = tk.Tk()
root.geometry("800x600")

# Create a frame for the video
video_frame = tk.Frame(root, bg="black")
video_frame.pack(fill=tk.BOTH, expand=1)

# Create a VLC instance and media player
instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new("sample.mp4")
player.set_media(media)

# Get the window id from the Tkinter widget
if hasattr(video_frame, 'winfo_id'):
    win_id = video_frame.winfo_id()
else:
    win_id = video_frame.frame()

# Set the VLC video output window
player.set_hwnd(win_id)  # On Windows; use set_xwindow(win_id) on Linux

player.play()
root.mainloop()
