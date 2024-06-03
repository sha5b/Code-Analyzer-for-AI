
### file_structure_generator.py
```python
import os
import tkinter as tk
from tkinter import filedialog

def generate_file_structure(root_folder, output_file):
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(root_folder):
            level = root.replace(root_folder, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write('{}{}/\n'.format(indent, os.path.basename(root)))
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                f.write('{}{}\n'.format(sub_indent, file))

def select_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

def save_file_structure():
    output_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt"),
                                                          ("All files", "*.*")])
    if output_file:
        generate_file_structure(folder_path.get(), output_file)
        status_label.config(text=f"File structure saved to: {output_file}")

app = tk.Tk()
app.title("File Structure Generator")

folder_path = tk.StringVar()

frame = tk.Frame(app)
frame.pack(pady=20)

select_button = tk.Button(frame, text="Select Folder", command=select_folder)
select_button.grid(row=0, column=0, padx=10)

folder_entry = tk.Entry(frame, textvariable=folder_path, width=50)
folder_entry.grid(row=0, column=1, padx=10)

save_button = tk.Button(app, text="Save File Structure", command=save_file_structure)
save_button.pack(pady=10)

status_label = tk.Label(app, text="")
status_label.pack(pady=10)

app.mainloop()
