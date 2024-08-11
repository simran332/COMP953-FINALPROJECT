from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from tkcalendar import DateEntry
import os
import ctypes
from datetime import date
import image_lib
import apod_desktop

# Initialize the APOD cache
apod_desktop.init_apod_cache()

# Create the main window
root = Tk()
root.title("Astronomy Picture of the Day Viewer")
root.geometry('900x800')
#root.minsize(850,600)
root.columnconfigure(0, weight=50)
root.columnconfigure(1, weight=50)
root.rowconfigure(0, weight=100)

# Set the application icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('COMP593.APODViewer')
root.iconbitmap(os.path.join(apod_desktop.SCRIPT_DIR, 'nasa_logo.ico'))

# Create the frames
frame_image = ttk.Frame(root)
frame_image.columnconfigure(0, weight=1)
frame_image.rowconfigure(0, weight=1)
frame_image.grid(row=0, columnspan=2, padx=10, pady=10, sticky=NSEW)

frame_image.columnconfigure(0, weight=1)
frame_image.rowconfigure(0, weight=1)

frame_explanation = ttk.Frame(root)
frame_explanation.columnconfigure(0, weight=1)
frame_explanation.rowconfigure(0, weight=1)
frame_explanation.grid(row=1, columnspan=2, padx=10, sticky=NSEW)

frame_select = ttk.LabelFrame(root, text="Select APOD")
frame_select.grid(row=2, column=0, padx=(10,5), pady=10, sticky=NSEW)

frame_download = ttk.LabelFrame(root, text="Download APOD")
frame_download.grid(row=2, column=1, padx=(5,10), pady=10, sticky=NSEW)

# Populate the frames with widgets
default_image_path = os.path.join(apod_desktop.SCRIPT_DIR, 'nasa_logo.ico')
image_apod = Image.open(default_image_path)
desired_size = (400, 300)  # Adjust these dimensions as needed
image_apod_resized = image_apod.resize(desired_size, Image.LANCZOS)
photo_apod = ImageTk.PhotoImage(image_apod_resized)
label_apod = ttk.Label(frame_image, image=photo_apod)
label_apod.grid(row=0)



label_explanation = ttk.Label(frame_explanation, wraplength=980)
label_explanation.grid(row=0)

label_select_apod = ttk.Label(frame_select, text="Select APOD:")
label_select_apod.grid(row=0, column=0, padx=(10,5), pady=10)

combo_select_apod = ttk.Combobox(frame_select, state='readonly', width=45)
combo_select_apod['values'] = apod_desktop.get_all_apod_titles()
combo_select_apod.set("Select an APOD")

def handle_select_apod(event):
    global selected_apod_info
    apod_index = event.widget.current() + 1
    selected_apod_info = apod_desktop.get_apod_info(apod_index)
    label_explanation['text'] = selected_apod_info['explanation']
    global image_apod, image_size, photo_apod
    apod_path = selected_apod_info['file_path']
    image_apod = Image.open(apod_path)
    image_size = image_lib.scale_image(image_apod.size, (frame_image.winfo_width(), frame_image.winfo_height()))
    photo_apod = ImageTk.PhotoImage(image_apod.copy().resize(image_size, Image.LANCZOS))
    label_apod.configure(image=photo_apod)
    button_set_desktop.state(['!disabled'])

combo_select_apod.bind('<<ComboboxSelected>>', handle_select_apod)
combo_select_apod.grid(row=0, column=1, pady=10)

txt_set_desktop = 'Set as Desktop'
button_set_desktop = ttk.Button(frame_select, text=txt_set_desktop, width=len(txt_set_desktop) + 2)
button_set_desktop.state(['disabled'])

def handle_set_desktop():
    if selected_apod_info is None:
        return
    image_lib.set_desktop_background_image(selected_apod_info['file_path'])

button_set_desktop['command'] = handle_set_desktop
button_set_desktop.grid(row=0, column=2, padx=10, pady=10)

label_select_date = ttk.Label(frame_download, text="Select Date:")
label_select_date.grid(row=0, column=0, padx=(10,5), pady=10)

calendar_select_date = DateEntry(frame_download, showweeknumbers=False, locale='en_CA')
calendar_select_date['maxdate'] = date.today()
calendar_select_date['mindate'] = date.fromisoformat("1995-06-16")
calendar_select_date.grid(row=0, column=1, pady=10)

txt_download_apod = 'Download APOD'
button_download_apod = ttk.Button(frame_download, text=txt_download_apod, width=len(txt_download_apod) + 2)

def handle_download_apod():
    selected_date = calendar_select_date.get_date()
    apod_id = apod_desktop.add_apod_to_cache(selected_date)
    if apod_id != 0:
        combo_select_apod['values'] = apod_desktop.get_all_apod_titles()
        combo_select_apod.current(newindex=apod_id-1)
        combo_select_apod.event_generate('<<ComboboxSelected>>')

button_download_apod['command'] = handle_download_apod
button_download_apod.grid(row=0, column=2, padx=10, pady=10, sticky=W)

def handle_resize_window(event):
    label_explanation['wraplength'] = frame_explanation.winfo_width()
    new_size = image_lib.scale_image(image_apod.size, (frame_image.winfo_width(), frame_image.winfo_height()))
    image_size = image_lib.scale_image(image_apod.size, (400, 300))
    if new_size != image_size:
        image_size = new_size
        global photo_apod
        photo_apod = ImageTk.PhotoImage(image_apod.copy().resize(image_size, Image.LANCZOS))
        label_apod.configure(image=photo_apod)

root.bind("<Configure>", handle_resize_window)

root.mainloop()
