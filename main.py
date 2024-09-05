import tkinter as tk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from PIL import Image, ImageTk  # Pour manipuler les images
import serial
from roundedButton import RoundedButton
from batteryDisplay import BatteryDisplay

os.environ['TK_SILENCE_DEPRECATION'] = '1'

class GraphDisplay:
    def __init__(self, parent):
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.place(relx=0.5, rely=0.5, relwidth=0.85, relheight=1, anchor='center')

    def update_graph(self, time_axis_values, consumption_values, production_values, time, window_size, update_interval):
        self.ax.clear()
        self.ax.plot(time_axis_values[:len(consumption_values)], consumption_values, label='Consommation', color='#F1C265', linewidth=7)
        self.ax.plot(time_axis_values[:len(production_values)], production_values, label='Production', color='#8675BA', linewidth=7)
        self.ax.set_ylim([0, 12])
        self.ax.set_xlim([(time - window_size) * update_interval / 1000, (time + window_size) * update_interval / 1000])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        # remove axis
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        self.canvas.draw()

class SerialInput:
    def __init__(self, port):
        try:
            self.serial_port = serial.Serial(port, 9600)
        except serial.SerialException:
            print("Erreur : impossible d'ouvrir le port série.")
            self.serial_port = None

    def read_values(self):
        if self.serial_port and self.serial_port.in_waiting > 0:
            line = self.serial_port.readline().decode('utf-8').strip()
            try:
                voltages = list(map(float, line.split(',')))
                if len(voltages) == 2:
                    return voltages[0], voltages[1]
            except ValueError:
                print("Erreur : impossible de convertir les valeurs en float.")
        print("Erreur : impossible de lire les valeurs des batteries.")
        return None, None
    
class TestInput:
    def read_values(self):
        # Générer des valeurs de test aléatoires
        return random.uniform(0, 5), random.uniform(0, 5)

class ElectricGame:
    def __init__(self, root, test_mode=False, update_interval=10, game_duration=10, window_size_second=3):
        self.root = root
        self.update_interval = update_interval
        self.game_duration = game_duration
        self.window_size_second = window_size_second
        self.test_mode = test_mode
        self.root.attributes('-fullscreen', True)
        self.start_frame = tk.Frame(root, bg='white')
        self.game_frame = None
        self.battery1 = None
        self.battery2 = None
        self.countdown_time = 3  # Temps pour le compte à rebours
        self.score_label = None  # Ajoutez ceci pour le score
        self.scores = []  # Liste pour stocker les scores
        self.score_history = []  # Historique des scores
        self.input_handler = TestInput() if test_mode else SerialInput('/dev/tty.usbmodem1101')
        self.player1_voltage = 0
        self.player2_voltage = 0
        self.show_start_screen()

    def show_start_screen(self):
        # Supprimer tous les widgets de l'écran de début avant de le réafficher
        for widget in self.start_frame.winfo_children():
            widget.destroy()

        self.start_frame.pack(fill=tk.BOTH, expand=True)
        self.root.configure(bg='white')

        # Ajouter le logo en haut
        logo_image = Image.open("./Splash_Volpil.png")
        logo_image = logo_image.resize((244, 300))  # Redimensionner le logo si nécessaire
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(self.start_frame, image=logo_photo, bg='white')
        logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
        logo_label.pack(pady=20)

        # Création d'un frame pour le contenu principal (texte + vidéo)
        content_frame = tk.Frame(self.start_frame, bg='white')
        content_frame.pack(expand=True, fill=tk.BOTH)

        # Ajouter le texte sur comment jouer (à gauche), en décalant à droite pour éviter la pile
        text_label = tk.Label(content_frame, text="Chaque joueur utilise une dynamo pour produire de l'énergie.\n\n"
                                                  "L'objectif est de faire en sorte que la somme de votre production \n"
                                                  "suive la courbe de consommation.\n\n"
                                                  "Vous devez éviter de tomber en dessous de la courbe de consommation.\n\n"
                                                  "Tournez vos dynamos ensemble et ajustez votre production pour \n"
                                                  "maintenir l'équilibre!\n\n"
                                                  "Bonne chance et amusez-vous bien!",
                              font=("Montserrat", 24), bg='white', fg='black', justify=tk.LEFT)
        text_label.pack(side=tk.LEFT, padx=(200, 200), pady=20)  # Décalage à droite

        # Ajout des batteries pour l'entraînement
        # self.battery1 = BatteryDisplay(self.start_frame, relx=0.05, rely=0.65, anchor='center', label_text="Joueur 1")
        # self.battery2 = BatteryDisplay(self.start_frame, relx=0.95, rely=0.65, anchor='center', label_text="Joueur 2")

        # Affichage du bouton Jouer avec style
        start_button = RoundedButton(self.start_frame, "Jouer !", self.start_game)

        # Démarrer la boucle de dessin des batteries
        # self.update_batteries()

    def update_batteries(self):
        # Lecture des valeurs des batteries à partir de l'Arduino
        player1_voltage, player2_voltage = self.input_handler.read_values()

        if player1_voltage is not None and player2_voltage is not None:
            self.battery1.draw_battery(player1_voltage)
            self.battery2.draw_battery(player2_voltage)

        # Répéter la mise à jour des batteries toutes les 500 ms
        self.root.after(self.update_interval, self.update_batteries)

    def start_game(self):
        self.start_frame.pack_forget()  # Cache l'écran de début
        self.game_frame = tk.Frame(self.root, bg='white')
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        # Initialisation des batteries et du graphique
        self.battery1 = BatteryDisplay(self.game_frame, relx=0.05, rely=0.65, anchor='center', label_text="Joueur 1")
        self.battery2 = BatteryDisplay(self.game_frame, relx=0.95, rely=0.65, anchor='center', label_text="Joueur 2")
        self.graph = GraphDisplay(self.game_frame)

        self.time = 0
        total_points = int(self.game_duration * 1000 / self.update_interval)  # Nombre total de points pour la durée du jeu
        self.consumption_values = self.generate_continuous_curve(total_points, 5, 10)
        self.production_values = []

        # Créer le label de compte à rebours une seule fois
        self.countdown_label = tk.Label(self.game_frame, font=("Arial", 100), bg='white', fg='black')
        self.countdown_label.pack(side=tk.TOP, pady=25)  # Placer en haut de l'écran

        # Créer le label pour le score
        self.score_label = tk.Label(self.game_frame, font=("Arial", 40), bg='white', fg='black')
        self.score_label.pack(side=tk.TOP)  # Placer juste en dessous du compte à rebours

        self.countdown_time = 3  # Initialiser le temps de compte à rebours
        self.countdown_label.config(text=f"{self.countdown_time}")  # Mettre à jour le texte du label
        self.countdown_time -= 1

        self.update()

    def update(self):
        self.time += 1  # Incrémenter le temps en centièmes de seconde
        elapsed_time = int(float(self.time) * float(self.update_interval) / 100)  # Temps écoulé en secondes

        if elapsed_time >= self.game_duration:  # Vérifier si le temps de jeu est écoulé
            self.show_end_screen()
            return

        # Gestion du compte à rebours
        if self.countdown_time > 0:
            if elapsed_time >= 3 - self.countdown_time:  # Décrémenter chaque seconde
                self.countdown_label.config(text=f"{self.countdown_time}")  # Mettre à jour le texte du label
                self.countdown_time -= 1

        # Vérifie si le compte à rebours est terminé
        elif self.countdown_time <= 0 and self.countdown_label and elapsed_time >= 3:
            self.countdown_label.pack_forget()  # Retirer le compte à rebours
            self.countdown_label = None  # Supprimer la référence pour libérer la mémoire

        # Lecture des valeurs des batteries à partir de l'Arduino
        player1_voltage, player2_voltage = self.input_handler.read_values()
        if player1_voltage is None or player2_voltage is None:
            player1_voltage, player2_voltage = self.player1_voltage, self.player2_voltage

        if player1_voltage is not None and player2_voltage is not None:
            self.player1_voltage = player1_voltage
            self.player2_voltage = player2_voltage
            self.battery1.draw_battery(player1_voltage)
            self.battery2.draw_battery(player2_voltage)

            production = player1_voltage + player2_voltage
            self.production_values.append(production)

            window_size = int(300 / self.update_interval)  # 3 secondes

            # Définir les indices de début et de fin pour l'intervalle de 3 secondes autour du temps présent
            start_index = max(0, self.time - window_size)
            end_index = min(len(self.consumption_values) - 1, self.time + window_size)

            # Extraire les valeurs de consommation et de production pour cet intervalle
            consumption_values = self.consumption_values[start_index:end_index + 1]
            production_values = self.production_values[start_index:end_index + 1]

            # Ajuster les valeurs de l'axe des temps pour l'intervalle de 3 secondes
            time_axis_values = [t * self.update_interval / 1000 for t in range(start_index, end_index + 1)]

            # Mettre à jour le graphique avec les valeurs extraites
            self.graph.update_graph(time_axis_values, consumption_values, production_values, self.time, window_size, self.update_interval)

            # Calculer le score seulement après le compte à rebours
            if not self.countdown_label:
                current_consumption = consumption_values[-1] if consumption_values else 0
                score = (production - current_consumption) / current_consumption * 100

                # Appliquer un malus ou calculer le score en fonction de la différence
                if score < 0:  # Si le score est négatif (en dessous de la courbe de production)
                    score *= -3  # Appliquer un malus de x3

                # Stocker le score
                self.scores.append(score)

                # Mettre à jour le label de score
                self.update_score_label(score)

        self.root.after(self.update_interval, self.update)  # Mettre à jour selon l'intervalle défini

    def generate_continuous_curve(self, length, min_value, max_value, smoothness=0.3):
        values = []
        current_value = random.uniform(min_value, max_value)
        for _ in range(length):
            change = random.uniform(-smoothness, smoothness)
            current_value += change
            current_value = max(min_value, min(current_value, max_value))
            values.append(current_value)
        return values
    
    def update_score_label(self, score):
        # Mettre à jour le texte du label
        self.score_label.config(text=f"{score:.2f}%")

        # Changer la couleur en fonction du score
        if score >= 100 and score <= 120:
            self.score_label.config(fg='green')  # Production entre 100% et 120%
        elif score > 120 and score <= 150:
            self.score_label.config(fg='orange')  # Production supérieure à 120%
        else:
            self.score_label.config(fg='red')  # Production inférieure à 100%

    def show_end_screen(self):
        # Cache le jeu actuel
        self.game_frame.pack_forget()

        # Calculer le score final et l'historique
        average_score = sum(self.scores) / len(self.scores) if self.scores else 0
        self.score_history.append(average_score)

        # Créer un nouvel écran de fin
        end_frame = tk.Frame(self.root, bg='white')
        end_frame.pack(fill=tk.BOTH, expand=True)

        # Frame pour afficher le score et le classement au centre
        score_frame = tk.Frame(end_frame, bg='white')
        score_frame.pack(pady=20)

        # Afficher le score final et le classement du joueur
        scores_sorted = sorted(self.score_history, reverse=True)
        player_ranking = scores_sorted.index(average_score) + 1  # +1 pour le classement humain

        # Frame gauche pour le texte explicatif
        left_frame = tk.Frame(end_frame, bg='white')
        left_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)

        # Image de fin pour le texte détaillé
        end_image = Image.open("./Volpil_Prof.png")
        end_image = end_image.resize((233, 200))  # Redimensionner l'image si nécessaire
        end_photo = ImageTk.PhotoImage(end_image)
        end_label = tk.Label(left_frame, image=end_photo, bg='white')
        end_label.image = end_photo  # Conserver une référence pour éviter la collecte des déchets
        end_label.pack(pady=10)

        # Texte détaillé sur les problèmes de flexibilité
        detailed_text = (
            "La gestion de la consommation d'électricité est cruciale pour les producteurs.\n\n"
            "Les fluctuations de la demande et les variations des sources d'énergie rendent\n"
            "difficile la prévision et l'ajustement en temps réel. Une flexibilité insuffisante\n"
            "peut entraîner des pertes financières et des inefficacités dans le réseau.\n\n"
            "Il est essentiel d'optimiser la gestion des ressources pour répondre à ces défis"
        )
        problem_text = tk.Label(left_frame, text=detailed_text, font=("Montserrat", 24), bg='white', fg='black', wraplength=600)
        problem_text.pack(expand=True, pady=10)  # Centrer le texte verticalement

        # Frame droite pour le tableau des scores
        right_frame = tk.Frame(end_frame, bg='white')
        right_frame.pack(side=tk.RIGHT, padx=20, fill=tk.BOTH, expand=True)

        # Afficher le titre du tableau des scores
        scores_label = tk.Label(right_frame, text="Scores :", font=("Arial", 32), bg='white', fg='black')
        scores_label.pack(pady=10)

        # Créer une zone pour afficher les scores
        scores_display = tk.Frame(right_frame, bg='white')
        scores_display.pack(pady=10)

        # Afficher chaque score dans le tableau avec classement
        for i, score in enumerate(scores_sorted):
            score_color = "black"
            if score == average_score:  # Highlight le score actuel
                score_color = "green"  # Couleur pour mettre en surbrillance le score du joueur
            score_entry = tk.Label(scores_display, text=f"{i + 1}      {score:.2f}", font=("Montserrat", 24), bg='white', fg=score_color)
            score_entry.pack(pady=2, anchor="center")  # Centrer en Y

        # Centrer le bouton Rejouer en bas
        restart_button_frame = tk.Frame(end_frame, bg='white')
        restart_button_frame.place(relx=0.5, rely=0.95, anchor="center")

        restart_button = RoundedButton(restart_button_frame, "Rejouer", lambda: self.restart_game(end_frame))

    def restart_game(self, end_frame):
        # Cache l'écran de fin
        end_frame.pack_forget()

        # Réinitialiser le jeu
        self.reset_game()

        # Retourne à l'écran de début
        self.show_start_screen()

    def reset_game(self):
        # Réinitialiser les variables de jeu
        self.time = 0
        self.consumption_values = []
        self.production_values = []
        self.scores = []  # Réinitialiser les scores

        # # Si les batteries sont présentes, redessiner
        # if self.battery1 and self.battery2:
        #     self.battery1.draw_battery(0)
        #     self.battery2.draw_battery(0)

        # # Si le graphique est présent, le réinitialiser
        # if hasattr(self, 'graph'):
        #     self.graph.update_graph([], [], [], 0, 30)  # Réinitialiser le graphique

if __name__ == "__main__":
    root = tk.Tk()
    game = ElectricGame(root, test_mode=False, update_interval=10, game_duration=30)
    root.mainloop()