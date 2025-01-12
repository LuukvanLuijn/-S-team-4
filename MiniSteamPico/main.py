from machine import Pin, Timer, SPI, ADC
import time, network, socket, rp2, sys, requests, json
from neopixel import Neopixel
import st7789py as st7789
import vga1_16x32 as font
import vga1_8x16 as fontSmall
from rotary_irq_rp2 import RotaryIRQ
import gc
import datetime
import ubinascii
from umqtt_simple import MQTTClient
import steamloadscreen_bitmap as LoadScreen


# Definities van pins scherm:
BL = 15
CS = 13
DC = 12
RST = 14
SDA = 11
SCL = 10

# Neopixel:
numpix = 8
strip = Neopixel(numpix, 1, 0, "GRB")

# Kleuren neopixel.
black = (0, 0, 0)
red = (255, 0, 0)
orange = (255, 165, 0)
yellow = (255, 150, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
indigo = (75, 0, 130)
violet = (138, 43, 226)
pink = (255, 105, 180)
colors_rgb = (red, orange, yellow, green, blue, indigo, violet)

colors = colors_rgb
strip.brightness(42)

# Bewegingssensor:
MSensor = Pin(1, Pin.IN)

# SPI:
spi = SPI(1, baudrate=40000000, polarity=1, phase=1, sck=Pin(SCL), mosi=Pin(SDA))

# WiFi:
NetworkTry = 1

# Encoder-pinnen:
clk = Pin(16, Pin.IN, Pin.PULL_UP)
dt = Pin(17, Pin.IN, Pin.PULL_UP)
encoder_switch = Pin(18, Pin.IN, Pin.PULL_UP)
mode_switch = Pin(19, Pin.IN, Pin.PULL_UP)

# Display:
display = st7789.ST7789(
        spi, 240, 320,
        reset=Pin(RST, Pin.OUT),
        dc=Pin(DC, Pin.OUT),
        cs=Pin(CS, Pin.OUT),
        rotation=-1)

# Variabelen:
current_row = 0
current_column = 0
mode = "row"
Active = False
beweging = False
StartTime = 0
EndTime = 0
Selected = False
SelectedPage = None
SelectedRow = None
APIKey = "AA22DEB7678B22A8B918FB7BD1122681"
SteamID = "76561199156245614"
fgColor = st7789.YELLOW
bgColor = st7789.BLACK

# variabelen voor MQTT
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC_SteamID = b'SteamIdSTeam'
last_SteamID = None

# Pagina's:
Page11 = "Recent Games"
Page12 = "Owned Games"
Page13 = "Achievements"
Page21 = "Friend List"
Page22 = "Friends Online"
Page23 = "Friends Played"
Page31 = "Player Summary"
Page32 = "Debug"
Page33 = "Connect"

Pages0 = {0 : Page11, 1 : Page12, 2 : Page13}
Pages1 = {0 : Page21, 1 : Page22, 2 : Page23}
Pages2 = {0 : Page31, 1 : Page32, 2 : Page33}

PageList = [Pages0, Pages1, Pages2]

# Encoder instellingen:
r = RotaryIRQ(pin_num_clk=clk,
              pin_num_dt=dt,
              min_val=0,
              max_val=2,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_WRAP)
val_old = r.value()
   
def NextWiFi():
    global NetworkTry
    global ssid
    global password
    if NetworkTry == 1:
        ssid = 'Hot Signals In Your Area'
        password = 'FreeWifiIG'
        NetworkTry = NetworkTry + 1
    elif NetworkTry == 2:
        ssid = 'Daniel'
        password = 'Helloworld'
        NetworkTry = NetworkTry + 1
    else:
        NetworkTry = 1
    print(ssid)
    
def connect():
    NextWiFi()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    wlan.connect(ssid, password)
    max_retries = 5
    retries = 0
    display.fill(bgColor)
    while not wlan.isconnected() and retries < max_retries:
        retries += 1
        time.sleep(1)
        display.text(font,"WiFi connection:",10,10,fgColor, bgColor)
        display.text(font,f"Connecting to:",10,40,fgColor, bgColor)
        display.text(font,f"{ssid}",10,70,fgColor, bgColor)
        display.text(font,f"Retry {retries}/{max_retries}",10,100,fgColor, bgColor)
        print(f"Connecting to Wi-Fi... Retry {retries}/{max_retries}")
    if wlan.isconnected():
        # extract from the returnvalue of the wlan.ifconfig() method the IP-address 
        ip = "192.168.155.163"
        print('Connected to Wi-Fi:', ip)
        display.fill(bgColor)
        display.text(font,f"Connected to:",10,10,fgColor, bgColor)
        display.text(font,f"{ssid}",10,40,fgColor, bgColor)
        display.text(font,f"ip: {ip}",10,70,fgColor, bgColor)
        time.sleep(3)
        
        return True
    else:
        print(f'Failed to connect to {ssid}')
        connect()
        
 


def sub_callback(topic, msg):
    global last_SteamID
    global SteamID
    global MessageReceived
    print((topic, msg))
    if topic == TOPIC_SteamID:
        if msg == last_SteamID:
            print("same as last, no update.")
        else:
            last_SteamID = msg.decode()
            print(f"Steam ID updated: {last_SteamID}")
            
    print("Message received")
    MessageReceived = True
    print(f"Steam ID = {last_SteamID}")
    SteamID = last_SteamID
    

def MQTTconnect():
    global MessageReceived
    MessageReceived = False
    Loop = True
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(sub_callback)
    try:
        # Verbind met MQTT Broker
        client.connect()
        print('Connected to MQTT Broker:', MQTT_BROKER)
        
        # Scherm: Verbonden
        display.fill(bgColor)
        display.text(font, "MQTT Verbinding:", 10, 10, fgColor, bgColor)
        display.text(fontSmall, f"Broker: {MQTT_BROKER}", 10, 40, fgColor, bgColor)
        display.text(fontSmall, "Verbonden!", 10, 60, fgColor, bgColor)
        display.text(fontSmall, f"Topic: {TOPIC_SteamID.decode()}", 10, 80, fgColor, bgColor)
        time.sleep(2)

        client.subscribe(TOPIC_SteamID)
        print('Subscribed to topics:', TOPIC_SteamID)
        
        # Wacht op data
        display.fill(bgColor)
        display.text(font, "MQTT Data Check", 10, 10, fgColor, bgColor)
        display.text(fontSmall, "Wacht op berichten...", 10, 40, fgColor, bgColor)
        display.text(fontSmall, "Druk op encoder", 10, 60, fgColor, bgColor)
        display.text(fontSmall, "om te stoppen", 10, 80, fgColor, bgColor)

        while Loop:
            print("Check")
            client.check_msg() 
            
            if MessageReceived == True:
                print("New SteamID")
                display.fill(bgColor)
                Loop = False
                display.text(fontSmall, "Nieuwe SteamID", 10, 60, fgColor, bgColor)
                display.fill(bgColor)                
            
            # Encoder knop indrukken om te stoppen
            if encoder_switch.value() == 0:
                print("Switchpressed")
                Loop = False
            time.sleep(0.5)
        display.fill(bgColor)
    except Exception as e:
        # Scherm: Foutmelding
        print('Failed to connect to MQTT Broker:', e)
        display.fill(bgColor)
        display.text(font, "MQTT Error:", 10, 10, fgColor, bgColor)
        display.text(fontSmall, "Kan niet verbinden", 10, 40, fgColor, bgColor)
        display.text(fontSmall, "met broker", 10, 60, fgColor, bgColor)
        display.text(fontSmall, f"Error: {str(e)}", 10, 80, fgColor, bgColor)
        time.sleep(3)




def Neopixels(column, mode):
    strip.fill(black)
    strip.show()
    if column == 0:
        pixel = 1
    elif column == 1:
        pixel = 3
    elif column == 2:
        pixel = 5
    strip.set_pixel(pixel, yellow)
    strip.show()


# Functie voor Actieve user detectie.
def ActiveUser():
    global Active, beweging, StartTime, EndTime
    global was_active  # Variabele om de vorige status van Active bij te houden
    AutoOff = 30  # Tijd in seconden voordat hij uitgaat zonder beweging

    if MSensor.value():  # Beweging gedetecteerd
        if not beweging:  # Alleen als dit een nieuwe beweging is
            beweging = True
            display.sleep_mode(False)
            print("Beweging gedetecteerd!")
        StartTime = time.time()  # Starttijd opnieuw instellen
        EndTime = StartTime + AutoOff  # Eindtijd opnieuw berekenen
        Active = True  # Zorg dat Active aan blijft
        was_active = True  # Reset de status
    else:  # Geen beweging
        if time.time() > EndTime:  # Controleer of de timer is verlopen
            if Active:  # Alleen uitvoeren als Active eerder True was
                beweging = False
                Active = False  # Zet Active op False alleen als de timer is verstreken
                display.sleep_mode(True)
                print("Geen beweging meer. Timer verlopen.")
            was_active = False  # Geef aan dat Active nu uit is


            
def Select(Selected, current_row, current_column):
    SelectedPage = PageList[current_column]
    SelectedRow = SelectedPage[current_row]
    print(SelectedPage)
    print(SelectedRow)
    Selected = True
    return Selected, SelectedPage, SelectedRow

def RecentGames():
    Loop = True
    RecentGameData = requests.get(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={APIKey}&steamid={SteamID}&format=json")
    print(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={APIKey}&steamid={SteamID}&format=json")
    try:
        data = RecentGameData.json()
        games = data['response']['games']
        recent_games = []
        for game in games:
            game_name = game['name']
            game_id = game['appid']
            recent_games.append({'name': game_name, 'appid': game_id})
            #print(f"Game: {game_name}, ID: {game_id}")
            x = 45
        #print(recent_games)
            display.text(font,"Recente games:",10,10,fgColor, bgColor)
        for game in recent_games:
            display.text(fontSmall,f"{game['name']}",10,x, fgColor, bgColor)
            x = x + 20
        while Loop == True:
            if encoder_switch.value() == 0:
                Loop = False
                display.fill(bgColor)
        gc.collect()
    
    except Exception as e:
        print(f"Fout bij het ophalen van recent gespeelde games: {e}")
        display.text(fontmall,"Error. Heb je recent",10,10,fgColor, bgColor)
        display.text(font,"spellen gespeeld?",10,40,fgColor, bgColor)
        print("Het kan dat je recent niks heb gespeeld")

def OwnedGames():
    gc.collect()
    Loop = True
    OwnedGamesData = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={APIKey}&steamid={SteamID}&include_appinfo=1&format=json")
    print(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={APIKey}&steamid={SteamID}&include_appinfo=1&format=json")
    print("After data request")
    try:
        data = OwnedGamesData.json()
        games = data['response']['games']
        print("Na .json")
        owned_games = []
        for game in games:
            game_name = game['name']
            playtime_forever = game.get('playtime_forever', 0)
            owned_games.append({'name': game_name, 'playtime_forever': playtime_forever})
            #print(f"Game: {game_name}, Playtime: {playtime_forever} minutes")
        print("Na for loop")
        owned_games_sorted = sorted(owned_games, key=lambda x: x['playtime_forever'], reverse=True)
        top_9_games = owned_games_sorted[:9]
        x = 45
        display.text(font,"Top gespeelde games:",0,10,fgColor, bgColor)
        for i, game in enumerate(top_9_games, start=1):
            #print(f"{i}. Game: {game['name']}, Total Playtime: {game['playtime_forever']} minutes")
            display.text(fontSmall,f"{i}. {game['name']}",10,x, fgColor, bgColor)
            x = x + 20
        print("Deze")
        while Loop == True:
            if encoder_switch.value() == 0:
                Loop = False
                display.fill(bgColor)
        print("Boem")
        gc.collect()
    except Exception as e:
        display.text(font,"Error:",0,10,fgColor, bgColor)
        display.text(fontSmall,f"{e}",0,40,fgColor, bgColor)
        display.text(fontSmall,"Waarschijnlijk te veel games",0,70,fgColor, bgColor)
        print(f"Fout bij het ophalen van owned games: {e}")
        time.sleep(3)
        display.fill(bgColor)

def Achievements():
    Loop = True
    try:
        OwnedGamesData = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={APIKey}&steamid={SteamID}&include_appinfo=1&format=json")
        #print(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={APIKey}&steamid={SteamID}&include_appinfo=1&format=json")
        data = OwnedGamesData.json()
        games = data['response']['games']
        gameNames = []
        owned_games = []
        for game in games:
            id = game['appid']
            game_name = game['name']
            playtime_forever = game.get('playtime_forever', 0)
            owned_games.append({'id': id, 'playtime_forever': playtime_forever})
            gameNames.append({'name': game_name, 'playtime_forever': playtime_forever})
            
        owned_games_sorted = sorted(owned_games, key=lambda x: x['playtime_forever'], reverse=True)
        top_3_games = owned_games_sorted[:3]
        gameNamesSorted = sorted(gameNames, key=lambda x: x['playtime_forever'], reverse=True)
        top3names = gameNamesSorted[:3]
        print(top3names)

        display.text(font,"Recent achievements voor recent games:",0,10,fgColor, bgColor)
        x = 45
        for i, game in enumerate(top_3_games, start=1):
            print(game['id'])
            AchievementData = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={game['id']}&key={APIKey}&steamid={SteamID}")
            print(f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={game['id']}&key={APIKey}&steamid={SteamID}")	
            gc.collect()
            try:
                AData = AchievementData.json()
                success = AData['playerstats']['success']
                print(f"success: {success}")
                id = game['id']
                if success == True:
                    Name = AData['playerstats']['gameName']
                    Achievements = AData['playerstats']['achievements']
                    AchievedAchievements = []
                    for Achievement in Achievements:
                        achieved = Achievement['achieved']
                        if achieved == True:
                            #print("Achieved true")
                            AchievedAchievements.append(Achievement)
                    #print(AchievedAchievements)
                    AchievementsSorted = sorted(AchievedAchievements, key=lambda x: x['unlocktime'], reverse=True)
                    Top3Achievements = AchievementsSorted[:3]
                    print(Top3Achievements)
                    
                    display.text(fontSmall,f"{i}. {Name}",10,x, fgColor, bgColor)
                    display.text(fontSmall,f"   {Top3Achievements[0]['apiname']}, {Top3Achievements[1]['apiname']}",10,x+20, fgColor, bgColor)
                    display.text(fontSmall,f"   {Top3Achievements[2]['apiname']}",10,x+40, fgColor, bgColor)
                    x = x + 65
                    
                elif success == False:
                    print(top3names[i-1])
                    Name = top3names[i-1]['name']
                    print(Name)
                    print(f"{Name} heeft geen achievements")
                    display.text(fontSmall,f"{i}. {Name}",10,x, fgColor, bgColor)
                    display.text(fontSmall,f"     geen achievements!",10,x+20, fgColor, bgColor)
                    x = x + 65
                else:
                    print("Iets is flink fout gegaan")
                
                
            except Exception as achievement_error:
                print(f"Fout bij het verwerken van achievements voor game {game['id']}: {achievement_error}")
            
        while Loop == True:
            if encoder_switch.value() == 0:
                Loop = False
                display.fill(bgColor)
    except Exception as e:
        display.text(font,"Error:",0,10,fgColor, bgColor)
        display.text(fontSmall,f"{e}",0,40,fgColor, bgColor)
        display.text(fontSmall,"Waarschijnlijk te veel games",0,70,fgColor, bgColor)
        print(f"Fout bij het ophalen van owned games: {e}")
        time.sleep(3)
        display.fill(bgColor)

                

def FriendList():
    try:
        Loop = True
        friendData = requests.get(f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={APIKey}&steamid={SteamID}&relationship=friend')
        #print(f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={APIKey}&steamid={SteamID}&relationship=friend')
        friendData = friendData.json()
        Friends = friendData['friendslist']['friends']
        Friends = sorted(Friends, key=lambda x: x['friend_since'], reverse=True)
        display.text(font,"Friend list:",0,10,fgColor, bgColor)
        x = 60
        for i, Friend in enumerate(Friends, start=1):
            steamid = Friend['steamid']
            fSince = Friend['friend_since']
            fSinceUTC = datetime.date.fromtimestamp(fSince)
            friendSumData = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={steamid}")
            #print(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={steamid}")
            friendSumData = friendSumData.json()
            FriendSum = friendSumData['response']['players']
            FriendName = FriendSum[0]['personaname']
            #print(f"{FriendName}, Since: {fSinceUTC}")
            display.text(fontSmall,f"{FriendName}, Since: {fSinceUTC}",10,x, fgColor, bgColor)
            x = x + 20
            
            
        while Loop == True:
                if encoder_switch.value() == 0:
                    Loop = False
                    display.fill(bgColor)
    except Exception as e:
        print(f"Fout bij het ophalen van friend list: {e}")
    
def FriendsOnline():
    try:
        Loop = True
        friendData = requests.get(f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={APIKey}&steamid={SteamID}&relationship=friend')
        #print(f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={APIKey}&steamid={SteamID}&relationship=friend')
        friendData = friendData.json()
        Friends = friendData['friendslist']['friends']
        Friends = sorted(Friends, key=lambda x: x['friend_since'], reverse=True)
        display.text(font,"Friend list:",0,10,fgColor, bgColor)
        x = 60
        for i, Friend in enumerate(Friends, start=1):
            steamid = Friend['steamid']
            fSince = Friend['friend_since']
            fSinceUTC = datetime.date.fromtimestamp(fSince)
            friendSumData = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={steamid}")
            #print(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={steamid}")
            friendSumData = friendSumData.json()
            FriendSum = friendSumData['response']['players']
            status = ''
            FriendName = FriendSum[0]['personaname']
            FriendStatus = FriendSum[0]['personastate']
            if FriendStatus == 0:
                status = 'Offline'
            elif FriendStatus == 1:
                status = 'Online'
            elif FriendStatus == 2:
                status = 'Busy'
            elif FriendStatus == 3:
                status = 'Away'
            elif FriendStatus == 4:
                status = 'Snooze'
            elif FriendStatus == 5:
                status = 'Looking to trade'
            elif FriendStatus == 6:
                status = 'Looking to play'
            #print(f"{FriendName}, Since: {fSinceUTC}")
            display.text(fontSmall,f"{FriendName}, Status: {status}",10,x, fgColor, bgColor)
            x = x + 20
            
            
        while Loop == True:
                if encoder_switch.value() == 0:
                    Loop = False
                    display.fill(bgColor)
                    
    except Exception as e:
        print(f"Fout bij het ophalen van status van vrienden: {e}")

def FriendsPlayed():
    try:
        Loop = True
        friendData = requests.get(f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={APIKey}&steamid={SteamID}&relationship=friend')
        print(f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={APIKey}&steamid={SteamID}&relationship=friend')
        friendData = friendData.json()
        Friends = friendData['friendslist']['friends']
        Friends = sorted(Friends, key=lambda x: x['friend_since'], reverse=True)
        fRecentOn = []
        display.text(font, "Friend played:", 0, 10, fgColor, bgColor)
        for i, Friend in enumerate(Friends, start=1):
            steamid = Friend['steamid']
            fSince = Friend['friend_since']
            fSinceUTC = datetime.date.fromtimestamp(fSince)
            friendSumData = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={steamid}")
            print(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={steamid}")
            friendSumData = friendSumData.json()
            FriendSum = friendSumData['response']['players']
            try:
                FriendName = FriendSum[0]['personaname']
            except:
                FriendName = 'Niet op te halen'
            try:
                fLastOff = FriendSum[0]['lastlogoff']
            except:
                fLastOff = 0
            fRecentOn.append({'id': steamid, 'fLastOff': fLastOff})
            fRecentOn = sorted(fRecentOn, key=lambda x: x['fLastOff'], reverse=True)
            f3Recents = fRecentOn[:3]
        
        print(f3Recents)
        x = 45
        for i, Friend in enumerate(f3Recents, start=0):
            RecentGameData = requests.get(f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={APIKey}&steamid={f3Recents[i]['id']}&format=json")
            try:
                data = RecentGameData.json()
                
                friendSumData = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={f3Recents[i]['id']}")
                friendSumData = friendSumData.json()
                FriendSum = friendSumData['response']['players']
                FriendName = FriendSum[0]['personaname']
                if 'response' in data and 'games' in data['response']:
                    games = data['response']['games']
                    recent_games = []
                    for game in games:
                        game_name = game['name']
                        game_id = game['appid']
                        recent_games.append({'name': game_name, 'appid': game_id})
                    for game in recent_games:
                        display.text(fontSmall, f"{FriendName}", 10, x, fgColor, bgColor)
                        x = x + 20
                        display.text(fontSmall, f"{game['name']}", 10, x, fgColor, bgColor)
                        x = x + 40
                else:
                    
                    #print(FriendName)
                    print(f"Geen recente games gevonden voor vriend {FriendName}")
                    display.text(fontSmall, f"{FriendName}:", 10, x, fgColor, bgColor)
                    x = x + 20
                    display.text(fontSmall, f"Geen recent games/private account", 10, x, fgColor, bgColor)
                    x = x + 40
            except Exception as e:
                print(f"Fout bij het verwerken van recente games voor vriend {f3Recents[i]['id']}: {e}")
                
        while Loop == True:
            if encoder_switch.value() == 0:
                Loop = False
                display.fill(bgColor)

    except Exception as e:
        print(f"Fout bij het ophalen van wat vrienden deden: {e}")
            

def PlayerSummary():
    try:
        Loop = True
        UserData = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={SteamID}")
        print(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIKey}&steamids={SteamID}")
        UserData = UserData.json()
        User = UserData['response']['players']
        
        Username = User[0]['personaname']
        Steamid = User[0]['steamid']
        Visibility = User[0]['communityvisibilitystate']
        Profilestate = User[0]['profilestate']
        LastLogOff = User[0]['lastlogoff']
        PersonaState = User[0]['personastate']
        TimeCreated = User[0]['timecreated']
        PersonaStateFlags = User[0]['personastateflags']
        
        if PersonaState == 0:
            PersonaState = 'Offline'
        elif PersonaState == 1:
            PersonaState = 'Online'
        elif PersonaState == 2:
            PersonaState = 'Busy'
        elif PersonaState == 3:
            PersonaState = 'Away'
        elif PersonaState == 4:
            PersonaState = 'Snooze'
        elif PersonaState == 5:
            PersonaState = 'Looking to trade'
        elif PersonaState == 6:
            PersonaState = 'Looking to play'
                
        if Profilestate == 1:
            Profilestate = 'True'
        elif Profilestate == 0:
            Profilestate = 'False'
        
        LastLogOff = datetime.date.fromtimestamp(LastLogOff)
        TimeCreated = datetime.date.fromtimestamp(TimeCreated)
        
        if PersonaStateFlags == 1:
            PersonaStateFlags = 'True'
        elif PersonaStateFlags == 0:
            PersonaStateFlags = 'False'
        
        display.text(font, "Player Summary:", 0, 10, fgColor, bgColor)
        display.text(fontSmall, f"Username = {Username}", 10, 70, fgColor, bgColor)
        display.text(fontSmall, f"Steam ID = {Steamid}", 10, 90, fgColor, bgColor)
        display.text(fontSmall, f"Has community profile = {Profilestate}", 10, 110, fgColor, bgColor)
        display.text(fontSmall, f"Last logoff = {LastLogOff}", 10, 130, fgColor, bgColor)
        display.text(fontSmall, f"Status = {PersonaState}", 10, 150, fgColor, bgColor)
        display.text(fontSmall, f"Account created = {TimeCreated}", 10, 170, fgColor, bgColor)
        display.text(fontSmall, f"Allow public comments = {PersonaStateFlags}", 10, 190, fgColor, bgColor)
        
        while Loop == True:
            if encoder_switch.value() == 0:
                Loop = False
                display.fill(bgColor)
        
    
    except Exception as e:
        print(f"Fout bij het ophalen van User data: {e}")
        display.text(font, f"Error,", 0, 100, fgColor, bgColor)
        display.text(font, f"Probeer later opnieuw", 0, 150, fgColor, bgColor)
        while Loop == True:
            if encoder_switch.value() == 0:
                Loop = False
                display.fill(bgColor)


def Debug():
    Loop = True  # Zorg ervoor dat Loop lokaal gedefinieerd is
    display.fill(bgColor)
    while Loop:
        try:
            
            display.text(font, "Debug Mode:", 10, 10, fgColor, bgColor)
            
            # Basisinformatie printen
            
            display.text(fontSmall, f"Steam ID: {SteamID}", 10, 60, fgColor, bgColor)
            display.text(fontSmall, f"MQTT Broker: {MQTT_BROKER}", 10, 80, fgColor, bgColor)
            display.text(fontSmall, f"Actief: {'Ja' if Active else 'Nee'}", 10, 100, fgColor, bgColor)
            
            # Encoderstatus
            display.text(fontSmall, f"Encoder Row: {current_row}", 10, 120, fgColor, bgColor)
            display.text(fontSmall, f"Encoder Column: {current_column}", 10, 140, fgColor, bgColor)
            
            # Netwerkstatus
            display.text(fontSmall, f"WiFi ssid: {ssid}", 10, 160, fgColor, bgColor)
            wlan = network.WLAN(network.STA_IF)
            if wlan.isconnected():
                ip = wlan.ifconfig()[0]
                display.text(fontSmall, f"WiFi Verbonden: {ip}", 10, 180, fgColor, bgColor)
            else:
                display.text(fontSmall, "WiFi: Niet verbonden", 10, 180, fgColor, bgColor)
            
            # Controleer of de encoderknop is ingedrukt
            if encoder_switch.value() == 0:
                Loop = False  # Stop de lus
                display.fill(bgColor)
            
            time.sleep(1)  # Kleine pauze in de loop

        except Exception as e:
            print(f"Fout in Debug functie: {e}")
            display.text(fontSmall, "Fout in Debug Mode!", 10, 200, fgColor, bgColor)
            time.sleep(2)  # Laat foutmelding kort zien


    


def ShowPage(Selected, SelectedRow):
    if Selected == True:
        print(f"Page: {SelectedRow}")
        if SelectedRow == "Recent Games":
            RecentGames()
        if SelectedRow == "Owned Games":
            OwnedGames()
        if SelectedRow == "Achievements":
            Achievements()
        if SelectedRow == "Friend List":
            FriendList()
        if SelectedRow == "Friends Online":
            FriendsOnline()
        if SelectedRow == "Friends Played":
            FriendsPlayed()
        if SelectedRow == "Player Summary":
            PlayerSummary()
        if SelectedRow == "Debug":
            Debug()
        if SelectedRow == "Connect":
            MQTTconnect()
        Selected = False
        return Selected
    

# Startup:
connect()
display.fill(bgColor)
time.sleep(0.6)
display.text(font,"Steam MINI",10,10,fgColor, bgColor)
display.fill(bgColor)
strip.show()
time.sleep(0.1)
for color in colors:
        for i in range(numpix):
            strip.set_pixel(i, color)
            time.sleep(0.01)
            strip.show()
strip.fill(black)
strip.show()
time.sleep(0.5)
strip.fill(red)
strip.show()
time.sleep(0.5)
strip.fill(black)
strip.set_pixel(1, yellow)
strip.show()

# Main loop:
while True:
    gc.collect()
    # Modus van de encoder bepalen
    if mode_switch.value() == 0:
        print("mode switch pressed")
        mode = "column"
    else:
        mode = "row"

    # Encoder uitlezen
    val_new = r.value()
    if val_old != val_new and mode == "row":
        val_old = val_new
        print('row =', val_new)
        current_row = val_new
        display.text(font,"                                        ",10,70,fgColor, bgColor)
    if val_old != val_new and mode == "column":
        val_old = val_new
        print('column =', val_new)
        print(PageList[current_column])
        current_column = val_new
        Neopixels(current_column, mode)
        display.text(font,"                                        ",10,70,fgColor, bgColor)
    CRowNormal = current_row + 1
    CColumnNormal = current_column + 1
    
    display.text(font,f"Kolom: {CColumnNormal}",10,70,fgColor, bgColor)
    display.text(font,f"Rij: {CRowNormal}",10,40,fgColor, bgColor)
    display.text(font,f"{PageList[current_column][current_row]}",10,10,fgColor, bgColor)

    # Encoderknop indrukken om een selectie te maken
    if encoder_switch.value() == 0:
        display.fill(bgColor)
        print("Encoder pressed")
        Selected, SelectedPage, SelectedRow = Select(Selected, current_row, current_column)
        Selected = ShowPage(Selected, SelectedRow)
        time.sleep(1)  # Debounce tijd

    # Beweging
    ActiveUser()
    
    # Ruim memory op
    gc.collect()
    
    # Kleine pauze voor de hoofdlus
    time.sleep(0.1)



