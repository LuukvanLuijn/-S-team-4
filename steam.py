import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO
import psycopg2

# Configureren van de hoofdfenster
root = ctk.CTk()
root.geometry("900x700")  # Vergroot de breedte van het hoofdfenster
root.title("Gaming Interface")
root.resizable(False, False)

list_urls = []

def imagegrabber(url):
    response = requests.get(url)
    imagedata = response.content
    return Image.open(BytesIO(imagedata))

def connect_to_database():    
    try:        
        conn = psycopg2.connect(            
            dbname="steam",            
            user="postgres",            
            password="123Welkom123!",              
            host="20.58.44.220",            
            port="5432"        
        )
        print("connected")        
        return conn    
    except Exception as e:        
        print(f"Kan geen verbinding maken met de database: {e}")        
        return None

def get_steam_games():
    conn = connect_to_database()
    if conn is None:
        return []
    try: 
        cursor = conn.cursor()
        cursor.execute("SELECT appid FROM games ORDER BY positive_ratings DESC LIMIT 8")
        games = cursor.fetchall()
        conn.close()
        return games
    except Exception as e:
        print(f"Kan geen games ophalen: {e}")
        return []

def getimages(id):
    url = f"https://store.steampowered.com/api/appdetails?appids={id}"
    response = requests.get(url)
    data = response.json()
    if data[str(id)]['success'] and data[str(id)]['data']:
        image = data[str(id)]['data']['header_image']
        print(f"Image URL: {image}")
        return image
    else:
        print("Game not found or API request failed.")
        return None

games = get_steam_games()
if games:
    for game in games:
        image_url = getimages(game[0])
        if image_url:
            list_urls.append(image_url)

def mainpage():
    for widget in root.winfo_children():
        widget.destroy()
    steam_blue = "#1b252e"
    button_blue = "#008cff"

    top_frame = ctk.CTkFrame(root, width=900, height=50, fg_color=steam_blue)
    top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(20, 0))
    steam_label = ctk.CTkLabel(top_frame, text="Steam", text_color="white")
    steam_label.pack(side=ctk.LEFT, padx=20, pady=10)
    vrienden_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="Vrienden", text_color="white", command=vriendenpage)
    vrienden_label.pack(side=ctk.RIGHT, padx=20, pady=10)

    games_frame = ctk.CTkFrame(root, width=850, height=200, fg_color=steam_blue)
    games_frame.pack(pady=20, fill=ctk.X)
    games_label = ctk.CTkLabel(games_frame, text="Games", font=("bold", 40), text_color="white")
    games_label.pack(pady=10)

    right_label = ctk.CTkButton(games_frame, fg_color=button_blue, text=">", text_color="white", width=20, command=rechts)
    right_label.pack(side=ctk.RIGHT, padx=(5, 5))
    left_label = ctk.CTkButton(games_frame, fg_color=button_blue, text="<", text_color="white", width=20, command=links)
    left_label.pack(side=ctk.LEFT, padx=(5, 5))

    global image1, image2, image3, image4
    image1 = ctk.CTkImage(imagegrabber(list_urls[0]), size=(207, 97))
    image2 = ctk.CTkImage(imagegrabber(list_urls[1]), size=(207, 97))
    image3 = ctk.CTkImage(imagegrabber(list_urls[2]), size=(207, 97))
    image4 = ctk.CTkImage(imagegrabber(list_urls[3]), size=(207, 97))

    label1 = ctk.CTkLabel(games_frame, image=image1)
    label1.pack(side=ctk.LEFT, padx=(0, 2), pady=10)
    label2 = ctk.CTkLabel(games_frame, image=image2)
    label2.pack(side=ctk.LEFT, padx=2, pady=10)
    label3 = ctk.CTkLabel(games_frame, image=image3)
    label3.pack(side=ctk.LEFT , padx=2, pady=10)
    label4 = ctk.CTkLabel(games_frame, image=image4)
    label4.pack(side=ctk.LEFT, padx=(2, 0), pady=10)

    bottom_frame = ctk.CTkFrame(root)
    bottom_frame.pack(pady=(10, 20), fill=ctk.X)

    left_frame = ctk.CTkFrame(bottom_frame, fg_color=steam_blue, width=425, height=200)
    left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(10, 5))
    left_frame.pack_propagate(0)  # Houd de afmetingen vast
    planned_label = ctk.CTkLabel(left_frame, text="Wanneer heb je gepland om te gaan spelen? (dd/mm)", text_color="white", anchor="w")
    planned_label.pack(pady=10, padx=10, anchor="w")

    right_frame = ctk.CTkFrame(bottom_frame, fg_color=steam_blue, width=425, height=200)
    right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=(5, 10))
    right_frame.pack_propagate(0)  # Houd de afmetingen vast
    most_played_label = ctk.CTkLabel(right_frame, text="Welke spellen worden het meest gespeeld?", text_color="white", anchor="w")
    most_played_label.pack(pady=10, padx=10, anchor="w")

    recommendation_frame = ctk.CTkFrame(root, fg_color=steam_blue, height=100)
    recommendation_frame.pack(pady=(0, 20), fill=ctk.X)
    recommendation_label = ctk.CTkLabel(recommendation_frame, text="Welke aanbevelingen kunnen er gemaakt worden om te spelen?", font=("Arial", 15), text_color="white")
    recommendation_label.pack(pady=20)

def links():
    print("links\n\n\n")
    setImages(list_urls[0], list_urls[1], list_urls[2], list_urls[3])

def rechts():
    print("rechts\n\n\n")
    setImages(list_urls[4], list_urls[5], list_urls[6], list_urls[7])

def setImages(image1_text, image2_text, image3_text, image4_text):
    global image1, image2, image3, image4
    image1.configure(light_image=imagegrabber(image1_text).resize((180, 180)))
    image2.configure(light_image=imagegrabber(image2_text).resize((180, 180)))
    image3.configure(light_image=imagegrabber(image3_text).resize((180, 180)))
    image4.configure(light_image=imagegrabber(image4_text).resize((180, 180)))

def vriendenpage():
    for widget in root.winfo_children():
        widget.destroy()
    
    blue = "#1b252e"
    button_blue = "#008cff"

    top_frame = ctk.CTkFrame(root, width=900, height=50, fg_color=blue)
    top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(20, 0))
    terug_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="Terug", text_color="white", command=mainpage)
    terug_label.pack(side=ctk.LEFT, padx=20, pady=10)
    vrienden_label = ctk.CTkLabel(top_frame, text="Vrienden", text_color="white")
    vrienden_label.pack(side=ctk.RIGHT, padx=60, pady=10)

    friends_online_frame = ctk.CTkFrame(root, width=850, height=200, fg_color=blue)
    friends_online_frame.pack(pady=20, fill=ctk.X)
    friends_online_label = ctk.CTkLabel(friends_online_frame, text="Wanneer zijn jouw vrienden online?", font=("Arial", 20), text_color="white")
    friends_online_label.pack(pady=50)

    games_friends_play_frame = ctk.CTkFrame(root, width=850, height=200, fg_color=blue)
    games_friends_play_frame.pack(pady=20, fill=ctk.X)
    games_friends_play_label = ctk.CTkLabel(games_friends_play_frame, text="Welke games spelen mijn vrienden?", font=("Arial", 20), text_color="white")
    games_friends_play_label.pack(pady=50)

    search_frame = ctk.CTkFrame(root, width=850, height=200, fg_color=blue)
    search_frame.pack(pady=20, fill=ctk.X)
    search_label = ctk.CTkLabel(search_frame, text="Zoek naar vrienden", font=("Arial", 20), text_color="white")
    search_label.pack(pady=50)

mainpage()
root.mainloop()
