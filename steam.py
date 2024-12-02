import customtkinter as ctk
from PIL import Image
import time

# Configureren van de hoofdfenster
root = ctk.CTk()
root.geometry("900x700")  # Vergroot de breedte van het hoofdfenster
root.title("Gaming Interface")

def mainpage():
    for widget in root.winfo_children():
        widget.destroy()
    # Definiëren van de blauwe kleur
    blue_color = "#3498db"
    #functies knoppen 
    def vriendenknop():
        vriendenpage()
        
    def gamesknop():
        print("Games")

    top_frame = ctk.CTkFrame(root, width=900, height=50, fg_color=blue_color)
    top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(20, 0))
    steam_label = ctk.CTkLabel(top_frame, text="Steam", text_color="white")
    steam_label.pack(side=ctk.LEFT, padx=20, pady=10)
    vrienden_label = ctk.CTkButton(top_frame, text="Vrienden", text_color="white", command=vriendenknop)
    vrienden_label.pack(side=ctk.RIGHT, padx=20, pady=10)

    # Centrale rechthoekige sectie voor games
    games_frame = ctk.CTkFrame(root, width=850, height=200, fg_color=blue_color)
    games_frame.pack(pady=20, fill=ctk.X)
    games_label = ctk.CTkLabel(games_frame, text="'Games'", font=("Arial", 20), text_color="white")
    games_label.pack(pady=10)

    # Voeg vier foto's toe aan het games_frame
    image1 = ctk.CTkImage(Image.open("eldenstink.png"), size=(200, 200))
    image2 = ctk.CTkImage(Image.open("eldenstink.png"), size=(200, 200))
    image3 = ctk.CTkImage(Image.open("eldenstink.png"), size=(200, 200))
    image4 = ctk.CTkImage(Image.open("eldenstink.png"), size=(200, 200))

    label1 = ctk.CTkLabel(games_frame, image=image1)
    label1.pack(side=ctk.LEFT, padx=(30, 5), pady=10)
    label2 = ctk.CTkLabel(games_frame, image=image2)
    label2.pack(side=ctk.LEFT, padx=5, pady=10)
    label3 = ctk.CTkLabel(games_frame, image=image3)
    label3.pack(side=ctk.LEFT, padx=5, pady=10)
    label4 = ctk.CTkLabel(games_frame, image=image4)
    label4.pack(side=ctk.LEFT, padx=(5, 30), pady=10)

    # Onderste secties met geplande spellen en meest gespeelde spellen
    bottom_frame = ctk.CTkFrame(root)
    bottom_frame.pack(pady=(10, 20), fill=ctk.X)

    left_frame = ctk.CTkFrame(bottom_frame, fg_color=blue_color, width=425, height=200)
    left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(10, 5))
    left_frame.pack_propagate(0)  # Houd de afmetingen vast
    planned_label = ctk.CTkLabel(left_frame, text="Wanneer heb je gepland om te gaan spelen? (dd/mm)", text_color="white", anchor="w")
    planned_label.pack(pady=10, padx=10, anchor="w")

    right_frame = ctk.CTkFrame(bottom_frame, fg_color=blue_color, width=425, height=200)
    right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=(5, 10))
    right_frame.pack_propagate(0)  # Houd de afmetingen vast
    most_played_label = ctk.CTkLabel(right_frame, text="Welke spellen worden het meest gespeeld?", text_color="white", anchor="w")
    most_played_label.pack(pady=10, padx=10, anchor="w")

    # Aanbevelingssectie
    recommendation_frame = ctk.CTkFrame(root, fg_color=blue_color, height=100)
    recommendation_frame.pack(pady=(0, 20), fill=ctk.X)
    recommendation_label = ctk.CTkLabel(recommendation_frame, text="Welke aanbevelingen kunnen er gemaakt worden om te spelen?", font=("Arial", 15), text_color="white")
    recommendation_label.pack(pady=20)

def vriendenpage():
    for widget in root.winfo_children():
        widget.destroy()
    
    blue_color = "#3498db"

    top_frame = ctk.CTkFrame(root, width=900, height=50, fg_color=blue_color)
    top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(20, 0))
    terug_label = ctk.CTkButton(top_frame, text="Terug", text_color="white", command=mainpage)
    terug_label.pack(side=ctk.LEFT, padx=20, pady=10)
    vrienden_label = ctk.CTkLabel(top_frame, text="Vrienden", text_color="white")
    vrienden_label.pack(side=ctk.RIGHT, padx=20, pady=10)

    # Vriendenpagina met nieuwe secties
    friends_online_frame = ctk.CTkFrame(root, width=850, height=200, fg_color=blue_color)
    friends_online_frame.pack(pady=20, fill=ctk.X)
    friends_online_label = ctk.CTkLabel(friends_online_frame, text="Wanneer zijn jouw vrienden online?", font=("Arial", 20), text_color="white")
    friends_online_label.pack(pady=50)

    games_friends_play_frame = ctk.CTkFrame(root, width=850, height=200, fg_color=blue_color)
    games_friends_play_frame.pack(pady=20, fill=ctk.X)
    games_friends_play_label = ctk.CTkLabel(games_friends_play_frame, text="Welke games spelen mijn vrienden?", font=("Arial", 20), text_color="white")
    games_friends_play_label.pack(pady=50)

mainpage()
root.mainloop()
