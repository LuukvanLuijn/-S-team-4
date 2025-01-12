import json
import matplotlib.pyplot as plt

class SteamData:
    def __init__(self, data="-S-team-4/steam_games.json"):
        self.data = data
        self.games_data = self.laad_json_data()
        self.peak_players = [game.get("peak_players", 0) for game in self.games_data]
        self.hours_played = [game.get("hours_played", 0) for game in self.games_data]

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
            "Peak Players": {
                "Gemiddelde": self.gemiddelde(self.peak_players),
                "Mediaan": self.mediaan(self.peak_players),
                "Standaarddeviatie": self.standaard_deviatie(self.peak_players),
            },
            "Hours Played": {
                "Gemiddelde": self.gemiddelde(self.hours_played),
                "Mediaan": self.mediaan(self.hours_played),
                "Standaarddeviatie": self.standaard_deviatie(self.hours_played),
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

