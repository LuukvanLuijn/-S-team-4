import customtkinter as ctk
import requests, psycopg2, webbrowser, _json, random, time
from PIL import Image
from io import BytesIO
from voorspellende_stats import main
from paho.mqtt import client as mqtt_client

title_variations = ["Are You Winning?","Level Up Your Game","The Npc's Are Waiting For U", "Unlock New Worlds", "Try Terraria", "Game On", "Let's Play Together", "Get Ready To Play", "Dive Into Action", "Connect With Friends", "Ready Up", "Play, Share, Connect", "Where Gamers Unite", "Just For Fun", "Chill And Play", "Game Time", "Let's Have Some Fun", "Your Next Challenge Awaits", "Rise To The Challenge", "Play Hard, Win Big", "Achieve Your Goals", "The Game Is On", "Discover New Adventures", "Explore The Unknown", "Uncover Hidden Gems", "Your Journey Awaits", "Samuel is brak"]
root = ctk.CTk()
root.geometry("900x700")  
root.title(f"STEAM: {random.choice(title_variations)}")
root.resizable(False, False)

steam_blue = "#1b252e"
button_blue = "#008cff"

list_urls = []
avatar = None
global naam
global friends
friends = []



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
        cursor.execute("SELECT appid FROM games ORDER BY positive_ratings DESC LIMIT 20")
        games = cursor.fetchall()
        conn.close()
        return games
    except Exception as e:
        print(f"Kan geen games ophalen: {e}")
        return []
    
def get_most_played_games():
    conn = connect_to_database()
    if conn is None:
        return []
    try: 
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM games ORDER BY average_playtime DESC LIMIT 20")  # Adjust the query as needed
        most_played_games = cursor.fetchall()
        conn.close()
        return most_played_games
    except Exception as e:
        print(f"Kan geen meest gespeelde games ophalen: {e}")
        return []
most_played_games = get_most_played_games()

def get_steam_news():
    all_games = get_steam_games()
    all_news = []
    
    for game_id in all_games:
        game_id = game_id[0]
        try:
            url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={game_id}&count=5&maxlength=300&format=json"
            response = requests.get(url)
            print(f"Fetching news for game ID {game_id}: {response.status_code}")  # Debugging line
            
            if response.status_code == 200:
                data = response.json()
                # Check if 'appnews' key exists in the response
                if 'appnews' in data and 'newsitems' in data['appnews']:
                    if data['appnews']['newsitems']:
                        all_news.extend(data['appnews']['newsitems'])  # Add news items to the list
                    else:
                        print(f"No news items found for game ID {game_id}.")
                else:
                    print(f"'appnews' key not found in response for game ID {game_id}. Response: {data}")
            else:
                print(f"Failed to fetch news for game ID {game_id}: {response.text}")
        except Exception as e:
            print(f"Error fetching news for game ID {game_id}: {e}")
    
    return all_news

def getimages(id):
    url = f"https://store.steampowered.com/api/appdetails?appids={id}"
    response = requests.get(url)
    data = response.json()
    if data[str(id)]['success'] and data[str(id)]['data']:
        image = data[str(id)]['data']['header_image']
        return image
    else:
        print(data)
        print("Game not found or API request failed.")
        return None

games = get_steam_games()
if games:
    for game in games:
        image_url = getimages(game[0])
        if image_url:
            list_urls.append(image_url)

def donation_button():
    webbrowser.open("https://www.armoedefonds.nl/")

def mainpage():
    for widget in root.winfo_children():
        widget.destroy()

    top_frame = ctk.CTkFrame(root, width=900, height=50, fg_color=steam_blue)
    top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(20, 0))
    steam_label = ctk.CTkLabel(top_frame, text="Steam", text_color="white", font=("bold", 30))
    steam_label.pack(side=ctk.LEFT, padx=20, pady=10)
    vrienden_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="Vrienden", text_color="white", command=vriendenpage)
    vrienden_label.pack(side=ctk.RIGHT, padx=(5, 20), pady=10)
    donation_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="Doneer", text_color="white", command=donation_button)
    donation_label.pack(side=ctk.RIGHT, padx=2, pady=10)
    stats_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="%",font=("arial", 20), text_color="white", width=30, height=30)
    stats_label.pack(side=ctk.RIGHT, padx=2, pady=10)
    MiniSteam_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="TI",font=("arial", 20), text_color="white",command=SteamMini_page, width=30, height=30)
    MiniSteam_label.pack(side=ctk.RIGHT, padx=2, pady=10)


    # Add the new AI stats button
    ai_stats_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="AI", font=("arial", 20), text_color="white", width=30, height=30, command=ai_statistics_page)
    ai_stats_label.pack(side=ctk.RIGHT, padx=2, pady=10)

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

    label1 = ctk.CTkLabel(games_frame, image=image1, text="")
    label1.pack(side=ctk.LEFT, padx=(0, 2), pady=10)
    label2 = ctk.CTkLabel(games_frame, image=image2, text="")
    label2.pack(side=ctk.LEFT, padx=2, pady=10)
    label3 = ctk.CTkLabel(games_frame, image=image3, text="")
    label3.pack(side=ctk.LEFT , padx=2, pady=10)
    label4 = ctk.CTkLabel(games_frame, image=image4, text="")
    label4.pack(side=ctk.LEFT, padx=(2, 0), pady=10)

    bottom_frame = ctk.CTkFrame(root)
    bottom_frame.pack(pady=(10, 20), fill=ctk.X)

    left_frame = ctk.CTkScrollableFrame(bottom_frame, fg_color=steam_blue, width=425, height=200, label_text="Steam News", label_font=("bold", 20))
    left_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(10, 5))
    news_items = get_steam_news()
    news_label = ctk.CTkLabel(left_frame, text="Steam News", text_color="white",font=("bold", 20), anchor="w")
    news_label.pack(pady=10, padx=10, anchor="w")

    for item in news_items:
        if isinstance(item, dict):
            title = item.get('title', 'No Title')
            news_url = item.get('url', None)  # Assuming 'url' key exists

            # Create a clickable label for the news title
            news_item_label = ctk.CTkButton(left_frame, text=title, text_color="white", command=lambda url=news_url: webbrowser.open(url))
            news_item_label.pack(pady=2, padx=10, anchor="w")

        else:
            print("Unexpected item format:", item)

    right_frame = ctk.CTkScrollableFrame(bottom_frame, fg_color=steam_blue, width=425, height=400, label_text="Meest gespeelde spellen", label_font=("bold", 20))
    right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=(5, 10))

    for game in most_played_games:
        most_played_label = ctk.CTkLabel(right_frame, text=game[0], text_color="white")
        most_played_label.pack(pady=2, padx = "10", anchor="w")

def links():
    setImages(list_urls[0], list_urls[1], list_urls[2], list_urls[3])

def rechts():
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

    top_frame = ctk.CTkFrame(root, width=900, height=50, fg_color=steam_blue)
    top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(20, 0))
    terug_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="Terug", text_color="white", command=mainpage)
    terug_label.pack(side=ctk.LEFT, padx=20, pady=10)
    vrienden_label = ctk.CTkLabel(top_frame, text="Vrienden", text_color="white")
    vrienden_label.pack(side=ctk.RIGHT, padx=60, pady=10)
    while True:
        if avatar != None:
            avatarimg = ctk.CTkImage(imagegrabber(avatar), size=(184, 184))
        else: avatarimg = ctk.CTkImage(imagegrabber("https://static.thenounproject.com/png/4595376-200.png"), size=(184, 184))
        break
    login_frame = ctk.CTkFrame(root, width=850, height=150, fg_color=steam_blue)
    login_frame.pack(pady=20, fill=ctk.X)
    login_label = ctk.CTkLabel(login_frame, text="Voer je SteamID/Vanity in.", font=("Arial", 20), text_color="white")
    login_label.pack(pady=10)
    username_entry = ctk.CTkEntry(login_frame, width=300, font=("Arial", 20), text_color="black")
    username_entry.pack(pady=10)

    print(avatar)
    def loginuser():
        vanity_url = username_entry.get()
        if vanity_url:
            # Check if the input is a numeric ID
            if vanity_url.isdigit():
                # If it's a numeric ID, use it directly
                steam_id = vanity_url
                print(f"Using numeric Steam ID: {steam_id}")
            else:
                # If it's not numeric, treat it as a vanity URL
                api_url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=4BD36C0BE91A8BD89F7A8B730DC93ADC&vanityurl={vanity_url}"
                response = requests.get(api_url)
                
                # Print the raw response text for debugging
                print(f"Response for vanity URL '{vanity_url}': {response.text}")
                
                # Check if the response status code is OK
                if response.status_code != 200:
                    print(f"Error: Received status code {response.status_code} for vanity URL '{vanity_url}'")
                    return
                
                # Try to parse the JSON response
                try:
                    data = response.json()
                except ValueError:
                    print("Response is not valid JSON:", response.text)
                    return
                
                # Check if the response indicates success
                if data['response']['success'] == 1:
                    steam_id = data['response']['steamid']
                    print(f"Logged in with Steam ID: {steam_id}")
                else:
                    print("Failed to log in. Invalid username.")
                    return
            
            apiResponseplayer = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=4BD36C0BE91A8BD89F7A8B730DC93ADC&steamids={steam_id}")
            apiResponsefriends = requests.get(f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=4BD36C0BE91A8BD89F7A8B730DC93ADC&steamid={steam_id}&relationship=friend")
            dataplayer = apiResponseplayer.json()
            datafriends = apiResponsefriends.json()
            global avatar, naam, friends_usernames, friends
            avatar = dataplayer['response']['players'][0]['avatarfull']
            naam = dataplayer['response']['players'][0]['personaname']
            if 'friendslist' in datafriends and 'friends' in datafriends['friendslist']:
                friends = [friend['steamid'] for friend in datafriends['friendslist']['friends']]
            friends_usernames = []

            for friend in friends:
                friend_summary_response = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=4BD36C0BE91A8BD89F7A8B730DC93ADC&steamids={friend}")
                friend_data = friend_summary_response.json()
                if friend_data['response']['players']:
                    friend_username = friend_data['response']['players'][0]['personaname']
                    friends_usernames.append(friend_username)
            print(f"logged in as: {naam}")
            vriendenpage()
        else:
            print("Please enter a username.")
    login_image = ctk.CTkImage(imagegrabber("https://community.fastly.steamstatic.com/public/images/signinthroughsteam/sits_01.png"), size=(180, 35))
    login_button = ctk.CTkButton(login_frame, text="", image=login_image, text_color="white", command=loginuser, fg_color=steam_blue)
    login_button.pack(pady=10)
    profile_frame = ctk.CTkFrame(root, width=450, height=150, fg_color=steam_blue)
    profile_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, pady=20, padx=(10,5))
    avatar_label = ctk.CTkLabel(profile_frame, image=avatarimg, text="")
    avatar_label.pack(side=ctk.LEFT,pady=10, padx=10)
    name = ctk.CTkLabel(profile_frame, text=naam, font=("Arial", 30), text_color="white")
    name.pack(side=ctk.LEFT, pady=10, padx=(10, 0))
    friends_frame = ctk.CTkScrollableFrame(root, width=450, height=150, fg_color=steam_blue)
    friends_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, pady=20, padx=10)
    friends_label = ctk.CTkLabel(friends_frame, text="Vrienden", font=("Arial", 20), text_color="white")
    friends_label.pack(pady=10, padx=(5,10))
    if friends_usernames:
        for friend in friends_usernames:
            friends_label = ctk.CTkLabel(friends_frame, text=friend, text_color="white", font = ("bold", 25))
            friends_label.pack(pady=10)
    else:
        lonely_label = ctk.CTkLabel(friends_frame, text="je hebt geen vrienden of", text_color="white", font=("Arial", 20))
        lonely_label2 = ctk.CTkLabel(friends_frame, text="je moet je friendlist op public zetten", text_color="white", font=("Arial", 20))
        lonely_label.pack(pady=(10, 0))
        lonely_label2.pack(pady=2)

def ai_statistics_page():
    for widget in root.winfo_children():
        widget.destroy()

    # Top frame met navigatie
    top_frame = ctk.CTkFrame(root, width=900, height=50, fg_color=steam_blue)
    top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(20, 0))
    
    terug_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="Terug", text_color="white", command=mainpage)
    terug_label.pack(side=ctk.LEFT, padx=20, pady=10)
    
    stats_label = ctk.CTkLabel(top_frame, text="Voorspellende Statistieken (AI)", text_color="white", font=("bold", 30))
    stats_label.pack(side=ctk.RIGHT, padx=60, pady=10)

    # Frame voor voorspellende statistieken
    content_frame = ctk.CTkFrame(root, width=850, height=600, fg_color=steam_blue)
    content_frame.pack(pady=20, fill=ctk.BOTH, expand=True)

    # Creëer een scrollbaar frame voor de statistieken
    pred_frame = ctk.CTkScrollableFrame(content_frame, fg_color=steam_blue, width=800, height=550)
    pred_frame.pack(pady=10, padx=10, fill=ctk.BOTH, expand=True)

    # Haal voorspellende statistieken op
    predictions = main()

    # Toon de resultaten
    title_label = ctk.CTkLabel(pred_frame, text="Voorspelde Statistieken", font=("bold", 24), text_color="white")
    title_label.pack(pady=(0, 20))

    for pred_name, pred_value in predictions.items():
        pred_label = ctk.CTkLabel(pred_frame, text=f"{pred_name}: {pred_value}", text_color="white", font=("Arial", 16), anchor="w", wraplength=800)
        pred_label.pack(pady=5, padx=10, anchor="w")




broker = 'broker.hivemq.com'
port = 1883
topic = "SteamIdSTeam"
client_id = f'publish-{random.randint(0, 1000)}'
username = 'emqx'
password = 'public'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, msg):
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def SteamMini_Connection():
    steam_id = SteamID_entry.get()
    publish(mqtt_client_instance, steam_id)

def SteamMini_page():
    global mqtt_client_instance
    mqtt_client_instance = connect_mqtt()
    mqtt_client_instance.loop_start()

    for widget in root.winfo_children():
        widget.destroy()

    top_frame = ctk.CTkFrame(root, width=900, height=50, fg_color=steam_blue)
    top_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(20, 0))
    
    terug_label = ctk.CTkButton(top_frame, fg_color=button_blue, text="Terug", text_color="white", command=mainpage)
    terug_label.pack(side=ctk.LEFT, padx=20, pady=10)
    
    ti_label = ctk.CTkLabel(top_frame, text="Connecteer aan de SteamMini (TI)", text_color="white", font=("bold", 30))
    ti_label.pack(side=ctk.LEFT, padx=40, pady=10)

    # Frame voor de SteamMini connectie
    sLogin_frame = ctk.CTkFrame(root, width=850, height=150, fg_color=steam_blue)
    sLogin_frame.pack(pady=20, fill=ctk.X)

    sLogin_label = ctk.CTkLabel(sLogin_frame, text="Voer je SteamID/Vanity in.", font=("Arial", 20), text_color="white")
    sLogin_label.pack(pady=10)

    global SteamID_entry
    SteamID_entry = ctk.CTkEntry(sLogin_frame, width=300, font=("Arial", 20), text_color="black")
    SteamID_entry.pack(pady=10)

    sLogin_button = ctk.CTkButton(sLogin_frame, text="Login button", text_color="white", command=SteamMini_Connection, fg_color=steam_blue)
    sLogin_button.pack(pady=10)

    Uitleg_frame = ctk.CTkFrame(root, width=850, height=150, fg_color=steam_blue)
    Uitleg_frame.pack(pady=20, fill=ctk.X)

    uitleg_lable = ctk.CTkLabel(Uitleg_frame, text="De SteamMini is een klein apparaatje dat je kan verbinden met je Steam account. \nZo Kun je je vrienden zien, je games en meer! Op de Mini Steam device ga naar Kolom 3 Rij 3, Connect. Wacht tot het schermpje MQTT Data Check laat zien en stuur dan de nieuwe steam ID met de login button.", text_color="white", font=("Arial", 20), wraplength=800)
    uitleg_lable.pack(pady=10)

mainpage()
root.mainloop()
