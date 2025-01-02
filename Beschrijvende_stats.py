import psycopg2
import json
import matplotlib.pyplot as plt


class SteamData:
    def __init__(self, data="-S-team-4/steam.json"):
        self.data = data
        self.games_data = self.laad_json_data()
        self.positieve_beoordelingen = [game.get("positive_ratings", 0) for game in self.games_data]
        self.negatieve_beoordelingen = [game.get("negative_ratings", 0) for game in self.games_data]
        self.prestaties = [game.get("achievements", 0) for game in self.games_data]
        self.prijzen = [game.get("price", 0) for game in self.games_data]
        self.speeltijden = [game.get("median_playtime", 0) for game in self.games_data]

    def connect_to_database(self):
        try:
            conn = psycopg2.connect(
                dbname="steam",
                user="postgres",
                password="123Welkom123!",
                host="20.58.44.220",
                port="5432"
            )
            print("Verbonden met de database.")
            return conn
        except Exception as e:
            print(f"Kan geen verbinding maken met de database: {e}")
            return None

    def laad_json_data(self):
        try:
            with open(self.data, "r") as bestand:
                return json.load(bestand)
        except FileNotFoundError:
            print(f"Bestand {self.data} niet gevonden.")
            return []
        except json.JSONDecodeError:
            print(f"Fout bij het decoderen van JSON uit bestand {self.data}.")
            return []

    def gemiddelde(self, waarden):
        return round(sum(waarden) / len(waarden), 2) if waarden else 0

    def mediaan(self, waarden):
        if not waarden:
            return None
        gesorteerd = sorted(waarden)
        n = len(gesorteerd)
        if n % 2 == 0:
            return round((gesorteerd[n // 2 - 1] + gesorteerd[n // 2]) / 2, 2)
        else:
            return round(gesorteerd[n // 2], 2)

    def standaard_deviatie(self, waarden):
        gem = self.gemiddelde(waarden)
        kwadratische_afwijkingen = sum((x - gem) ** 2 for x in waarden)
        standaarddev = (kwadratische_afwijkingen / len(waarden)) ** 0.5 if waarden else 0
        return round(standaarddev, 2)

    def bereken_statistieken(self):
        return {
            "Positieve beoordelingen": {
                "Gemiddelde": self.gemiddelde(self.positieve_beoordelingen),
                "Mediaan": self.mediaan(self.positieve_beoordelingen),
                "Standaarddeviatie": self.standaard_deviatie(self.positieve_beoordelingen),
            },
            "Negatieve beoordelingen": {
                "Gemiddelde": self.gemiddelde(self.negatieve_beoordelingen),
                "Mediaan": self.mediaan(self.negatieve_beoordelingen),
                "Standaarddeviatie": self.standaard_deviatie(self.negatieve_beoordelingen),
            },
            "Prestaties": {
                "Gemiddelde": self.gemiddelde(self.prestaties),
                "Mediaan": self.mediaan(self.prestaties),
                "Standaarddeviatie": self.standaard_deviatie(self.prestaties),
            },
            "Prijzen": {
                "Gemiddelde": self.gemiddelde(self.prijzen),
                "Mediaan": self.mediaan(self.prijzen),
                "Standaarddeviatie": self.standaard_deviatie(self.prijzen),
            },
            "Speeltijden": {
                "Gemiddelde": self.gemiddelde(self.speeltijden),
            },
        }
        
    def print_statistieken(self):
        statistieken = self.bereken_statistieken()
        for categorie, statistiek in statistieken.items():
            print(f"Statistieken voor {categorie}:")
            for sleutel, waarde in statistiek.items():
                print(f"{sleutel.capitalize()}: {waarde}")
            print()

steam_data = SteamData()
steam_data.print_statistieken()
