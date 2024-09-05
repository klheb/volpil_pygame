import tkinter as tk

class RoundedButton:
    def __init__(self, parent, text, command):
        self.parent = parent
        self.text = text
        self.command = command

        # Créer un canvas pour dessiner le bouton
        self.canvas = tk.Canvas(parent, width=200, height=60, bg='white', highlightthickness=0)
        self.canvas.pack(pady=20, side=tk.BOTTOM, anchor="center")

        # Dessiner le bouton avec des bords arrondis
        self.draw_button()

        # Ajouter le texte sur le bouton
        self.text_id = self.canvas.create_text(100, 30, text=self.text, fill='white', font=("Montserrat", 20))

        # Lier le clic sur le bouton à la fonction de commande
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_button(self):
        # Couleurs
        button_color = "#8675BA"  # Couleur principale du bouton
        radius = 15  # Rayon des coins arrondis

        # Dessiner les coins arrondis
        self.canvas.create_arc(0, 0, radius * 2, radius * 2, start=90, extent=90, fill=button_color, outline="")
        self.canvas.create_arc(200 - radius * 2, 0, 200, radius * 2, start=0, extent=90, fill=button_color, outline="")
        self.canvas.create_arc(0, 60 - radius * 2, radius * 2, 60, start=180, extent=90, fill=button_color, outline="")
        self.canvas.create_arc(200 - radius * 2, 60 - radius * 2, 200, 60, start=270, extent=90, fill=button_color, outline="")

        # Dessiner le grand rectangle entre les arcs
        self.canvas.create_rectangle(radius, 0, 200 - radius + 1, 60, fill=button_color, outline="")
        
        # Dessiner les petits rectangles entre les arcs et les bords
        self.canvas.create_rectangle(0, radius, radius, 60 - radius + 1, fill=button_color, outline="")
        self.canvas.create_rectangle(200 - radius, radius, 200, 60 - radius + 1, fill=button_color, outline="")

    def on_click(self, event):
        self.command()  # Appeler la commande associée