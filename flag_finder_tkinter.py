import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os
import tkinter.font as tkFont

# -------------------------
# Setup
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "flags.json"), "r", encoding="utf-8") as f:
    FLAGS = json.load(f)

# Keep references to images to prevent garbage collection
result_images = []

# -------------------------
# Flag image loader
# -------------------------
def load_flag_image(path):
    full_path = os.path.join(BASE_DIR, path)
    try:
        img = Image.open(full_path).resize((80, 50))
    except FileNotFoundError:
        img = Image.new("RGB", (80, 50), color="gray")
        draw = ImageDraw.Draw(img)
        draw.text((5, 20), "No Img", fill="white")
    return img

# -------------------------
# Display flags
# -------------------------
def display_flags(results):
    global result_images
    result_images.clear()

    for widget in flag_frame.winfo_children():
        widget.destroy()

    def redraw(event=None):
        for widget in flag_frame.winfo_children():
            widget.destroy()

        canvas_width = canvas.winfo_width()
        padding = 10  # horizontal padding per flag
        default_flag_width = 80  # image width

        # Prepare font to measure text width
        label_font = tkFont.Font(family="Arial", size=10)

        # Compute max column width dynamically based on flags and names
        max_col_widths = []
        for flag in results:
            text_width = label_font.measure(flag["country"])
            col_width = max(default_flag_width, text_width) + padding
            max_col_widths.append(col_width)

        avg_col_width = max(max_col_widths) if max_col_widths else default_flag_width + padding
        max_columns = max(1, canvas_width // avg_col_width)

        row = 0
        column = 0

        for flag in results:
            img = load_flag_image(flag["file"])
            img_tk = ImageTk.PhotoImage(img)
            result_images.append(img_tk)

            flag_label = ttk.Label(flag_frame, image=img_tk)
            flag_label.grid(row=row, column=column, padx=5, pady=(5,0), sticky="n")

            # <-- Change: set Arial font for country names
            name_label = ttk.Label(flag_frame, text=flag["country"], font=("Arial", 10))
            name_label.grid(row=row+1, column=column, padx=5, pady=(0,5))

            column += 1
            if column >= max_columns:
                column = 0
                row += 2

        flag_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    redraw()
    canvas.bind("<Configure>", lambda e: redraw())

# -------------------------
# Search function
# -------------------------
def search(colours, patterns):
    results = []
    for flag in FLAGS:
        if colours and not all(c in flag["colours"] for c in colours):
            continue
        if patterns and not all(p in flag["patterns"] for p in patterns):
            continue
        results.append(flag)
    return results

def on_search():
    cols = [c.strip().lower() for c in entry_colours.get().split(",") if c.strip()]
    pats = [p.strip().lower() for p in entry_patterns.get().split(",") if p.strip()]
    results = search(cols, pats)
    controls_frame.place_forget()
    show_reset_button()
    display_flags(results)

# -------------------------
# Reset function
# -------------------------
def reset_view():
    global result_images
    result_images.clear()
    hide_reset_button()

    for widget in flag_frame.winfo_children():
        widget.destroy()

    # Show full-screen search again
    controls_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    flag_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# -------------------------
# Fullscreen toggle
# -------------------------
def toggle_fullscreen(event=None):
    is_fullscreen = root.attributes("-fullscreen")
    root.attributes("-fullscreen", not is_fullscreen)
    return "break"

# -------------------------
# Help window
# -------------------------
def show_help():
    help_win = tk.Toplevel(root)
    help_win.title("Help - Colours and Patterns")
    help_win.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    help_win.resizable(True, True)

    colours_container = ttk.Frame(help_win)
    colours_container.pack(side="left", fill="both", expand=True, padx=20, pady=10)
    ttk.Label(colours_container, text="Available Colours:", font=("Arial", 12, "bold")).pack(anchor="w")
    colours_canvas = tk.Canvas(colours_container)
    colours_scrollbar = ttk.Scrollbar(colours_container, orient="vertical", command=colours_canvas.yview)
    colours_canvas.configure(yscrollcommand=colours_scrollbar.set)
    colours_canvas.pack(side="left", fill="both", expand=True)
    colours_scrollbar.pack(side="right", fill="y")
    colours_frame = ttk.Frame(colours_canvas)
    colours_canvas.create_window((0,0), window=colours_frame, anchor="nw")
    colours_frame.bind("<Configure>", lambda e: colours_canvas.configure(scrollregion=colours_canvas.bbox("all")))

    patterns_container = ttk.Frame(help_win)
    patterns_container.pack(side="left", fill="both", expand=True, padx=40, pady=10)
    ttk.Label(patterns_container, text="Available Patterns:", font=("Arial", 12, "bold")).pack(anchor="w")
    patterns_canvas = tk.Canvas(patterns_container)
    patterns_scrollbar = ttk.Scrollbar(patterns_container, orient="vertical", command=patterns_canvas.yview)
    patterns_canvas.configure(yscrollcommand=patterns_scrollbar.set)
    patterns_canvas.pack(side="left", fill="both", expand=True)
    patterns_scrollbar.pack(side="right", fill="y")
    patterns_frame = ttk.Frame(patterns_canvas)
    patterns_canvas.create_window((0,0), window=patterns_frame, anchor="nw")
    patterns_frame.bind("<Configure>", lambda e: patterns_canvas.configure(scrollregion=patterns_canvas.bbox("all")))
    patterns_canvas.bind("<Configure>", lambda e: patterns_canvas.itemconfig(patterns_canvas.find_all()[0], width=e.width))

    help_win.colour_images = []
    help_win.pattern_images = []

    def apply_filter(colours=None, pattern=None):
        help_win.destroy()
        controls_frame.place_forget()
        show_reset_button()
        results = FLAGS
        if colours:
            results = [f for f in FLAGS if all(c in f["colours"] for c in colours)]
        if pattern:
            results = [f for f in results if pattern in f["patterns"]]
        display_flags(results)

    unique_colours = sorted({c for flag in FLAGS for c in flag["colours"]})
    for colour in unique_colours:
        row = ttk.Frame(colours_frame)
        row.pack(anchor="w", pady=5)
        canvas_sample = tk.Canvas(row, width=80, height=50)
        canvas_sample.create_rectangle(0, 0, 80, 50, fill=colour)
        canvas_sample.pack(side="left", padx=(0,5))
        canvas_sample.bind("<Button-1>", lambda e, c=[colour]: apply_filter(colours=c))
        ttk.Label(row, text=colour.capitalize()).pack(side="left", padx=5)

    unique_patterns = sorted({p for flag in FLAGS for p in flag["patterns"]})
    for pattern in unique_patterns:
        row = ttk.Frame(patterns_frame)
        row.pack(anchor="w", pady=5)
        example_flag = next((f for f in FLAGS if pattern in f["patterns"]), None)
        if example_flag:
            img = load_flag_image(example_flag["file"]).resize((80,50))
            img_tk = ImageTk.PhotoImage(img)
            help_win.pattern_images.append(img_tk)
            img_label = ttk.Label(row, image=img_tk)
            img_label.pack(side="left", padx=(0,5))
            img_label.bind("<Button-1>", lambda e, p=pattern: apply_filter(pattern=p))
        ttk.Label(row, text=pattern.capitalize()).pack(side="left")

# -------------------------
# GUI setup
# -------------------------
root = tk.Tk()
root.title("Flag Finder")
root.state("zoomed")
root.resizable(True, True)
root.bind("<Escape>", toggle_fullscreen)

canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.config(yscrollcommand=scrollbar.set)
flag_frame = ttk.Frame(canvas)
canvas.create_window((0,0), window=flag_frame, anchor="nw")
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
flag_frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

controls_frame = ttk.Frame(root, relief="raised", borderwidth=2)
controls_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
controls_inner = ttk.Frame(controls_frame)
controls_inner.place(relx=0.5, rely=0.5, anchor="center")

ttk.Label(controls_inner, text="Colours (check help):", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
entry_colours = ttk.Entry(controls_inner, font=("Arial", 16), width=30)
entry_colours.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(controls_inner, text="Patterns (check help):", font=("Arial", 16)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
entry_patterns = ttk.Entry(controls_inner, font=("Arial", 16), width=30)
entry_patterns.grid(row=1, column=1, padx=10, pady=10)

ttk.Button(controls_inner, text="Search", command=on_search, width=15).grid(row=2, column=0, columnspan=2, pady=(20,10))
ttk.Button(controls_inner, text="Help", command=show_help, width=15).grid(row=3, column=0, columnspan=2, pady=(0,10))

# -------------------------
# Reset button (floating)
# -------------------------
reset_button = tk.Button(
    root,
    text="Reset",
    command=reset_view,
    bg="red",
    fg="white",
    font=("Arial", 16, "bold"),
    padx=20,
    pady=10
)

def show_reset_button():
    reset_button.place(relx=0.98, rely=0.5, anchor="e")  # vertically centered

def hide_reset_button():
    reset_button.place_forget()

root.mainloop()