import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Optional, Tuple

def select_project() -> Tuple[Optional[Path], Optional[Path]]:
    """
    Opens GUI dialogs for selecting:
    1. Project folder to analyze
    2. Optional output file location
    
    Returns:
        Tuple[Optional[Path], Optional[Path]]: (project_path, output_path)
        Both paths will be None if user cancels the first dialog.
        output_path will be None if user cancels the second dialog.
    """
    # Hide the main tkinter window
    root = tk.Tk()
    root.withdraw()

    # Select project folder
    project_path = filedialog.askdirectory(
        title='Select Project to Analyze',
        mustexist=True
    )
    
    if not project_path:
        root.destroy()
        return None, None
        
    project_path = Path(project_path)
    
    # Ask if user wants to save analysis
    save_analysis = tk.messagebox.askyesno(
        "Save Analysis",
        "Would you like to save the analysis to a file?"
    )
    
    output_path = None
    if save_analysis:
        # Select output file location
        output_path = filedialog.asksaveasfilename(
            title='Save Analysis As',
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
            initialdir=str(project_path),
            initialfile='analysis.json'
        )
        if output_path:
            output_path = Path(output_path)
    
    root.destroy()
    return project_path, output_path
