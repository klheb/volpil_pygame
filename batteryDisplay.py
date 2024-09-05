import tkinter as tk
from tkinter import Canvas

class BatteryDisplay:
    def __init__(self, parent, relx, rely, anchor, label_text):
        self.canvas = Canvas(parent, bg='white', highlightthickness=0)
        self.canvas.place(relx=relx, rely=rely, relwidth=0.05, relheight=0.5, anchor=anchor)
        self.label = tk.Label(parent, text=label_text, font=("Arial", 16), bg='white', fg='black')
        self.label.place(relx=relx, rely=rely + 0.28, anchor=anchor)
        self.production_label = tk.Label(parent, text="0.0W", font=("Arial", 16), bg='white', fg='black')
        self.production_label.place(relx=relx, rely=rely - 0.28, anchor=anchor)

    def draw_battery(self, voltage, max_voltage=5):
        self.canvas.delete('all')
        canvas_height = self.canvas.winfo_height()
        canvas_width = self.canvas.winfo_width()
        
        border_offset = 5
        top_height = 10

        # Draw the battery outline
        self.canvas.create_rectangle(border_offset, top_height + border_offset,
                                     canvas_width - border_offset, canvas_height - border_offset,
                                     outline='black', width=3)
        
        # Calculate the height of the current level
        height = (voltage / max_voltage) * (canvas_height - 2 * border_offset - top_height)

        # Draw the battery top
        self.canvas.create_rectangle(canvas_width * 0.25, border_offset,
                                     canvas_width * 0.75, border_offset + top_height,
                                     fill='black', outline='black')

        # Draw the gradient
        self.draw_gradient_rectangle(border_offset + 1, canvas_height - height - border_offset - top_height,
                                     canvas_width - border_offset - 1, canvas_height - border_offset, 
                                     height, canvas_height - 2 * border_offset - top_height)

        # Draw the lightning bolt
        self.draw_lightning(canvas_width * 0.5, canvas_height * 0.5)

        # Update the production label
        self.production_label.config(text=f"{voltage:.1f}W")

    def draw_gradient_rectangle(self, x1, y1, x2, y2, current_height, max_height):
        for i in range(max_height):
            ratio = i / max_height
            if ratio < 0.5:
                r = int(255 * (ratio * 2))
                g = 255
                b = 0
            else:
                r = 255
                g = int(255 * (1 - ((ratio - 0.5) * 2)))

            fill_color = f'#{r:02x}{g:02x}{b:02x}'
            if i < current_height:
                self.canvas.create_line(x1, y2 - i, x2, y2 - i, fill=fill_color)

    def draw_lightning(self, x, y):
        lightning_points = [
            (x + 10, y - 20),
            (x - 10, y + 3),
            (x - 3, y + 3),
            (x - 10, y + 20),
            (x + 10, y - 3),
            (x + 3, y - 3),
            (x + 10, y - 20),
        ]
        self.canvas.create_polygon(lightning_points, fill='black', outline='black')