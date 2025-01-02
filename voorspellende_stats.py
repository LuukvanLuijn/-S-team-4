import matplotlib.pyplot as plt
import psycopg2  # Bibliotheek voor PostgreSQL database verbinding

# Functie om verbinding te maken met onze database
def maak_database_verbinding():
    """Probeer verbinding te maken met de Steam games database"""
    try:
        # Maak verbinding met onze database gegevens
        verbinding = psycopg2.connect(
            dbname="steam",
            user="postgres",
            password="123Welkom123!",
            host="20.58.44.220",
            port="5432"
        )
        print("Succesvol verbonden met database!")
        return verbinding
    except Exception as fout:
        print(f"Kon geen verbinding maken met database: {fout}")
        return None

class LineaireRegressie:
    """Een eenvoudig lineaire regressie model met gebruik van gradiënt afdaling"""
    
    def __init__(self, leer_snelheid=0.01, aantal_iteraties=1000):
        # Initialiseer model parameters
        self.leer_snelheid = leer_snelheid  # Hoe snel het model leert
        self.aantal_iteraties = aantal_iteraties  # Hoe vaak we trainen
        self.gewichten = []  # Model gewichten (geïnitialiseerd tijdens training)
        self.fouten_geschiedenis = []  # Bijhouden van fouten tijdens training
    
    def bereken_fout(self, werkelijke_y, voorspelde_y):
        """Bereken de gemiddelde kwadratische fout tussen werkelijke en voorspelde waarden"""
        aantal_voorbeelden = len(werkelijke_y)
        totale_fout = 0
        
        # Loop door elk voorbeeld om de fout te berekenen
        for i in range(aantal_voorbeelden):
            fout = (werkelijke_y[i] - voorspelde_y[i]) ** 2
            totale_fout = totale_fout + fout
        
        return totale_fout / (2 * aantal_voorbeelden)
    
    def voorspel(self, X):
        """Maak voorspellingen met huidige gewichten"""
        voorspellingen = []
        
        # Voor elk datapunt
        for x in X:
            # Bereken voorspelling voor dit punt
            voorspelling = 0
            for i in range(len(self.gewichten)):
                voorspelling = voorspelling + (self.gewichten[i] * x[i])
            voorspellingen.append(voorspelling)
            
        return voorspellingen
    
    def train(self, X, y):
        """Train het model met gradiënt afdaling"""
        # Initialiseer gewichten met nullen
        aantal_kenmerken = len(X[0])
        self.gewichten = []
        for i in range(aantal_kenmerken):
            self.gewichten.append(0)
        
        # Training loop
        for iteratie in range(self.aantal_iteraties):
            # Maak voorspellingen met huidige gewichten
            voorspellingen = self.voorspel(X)
            
            # Bereken fouten
            fouten = []
            for i in range(len(y)):
                fout = voorspellingen[i] - y[i]
                fouten.append(fout)
            
            # Update elk gewicht
            for j in range(aantal_kenmerken):
                # Bereken gradiënt
                gradient = 0
                for i in range(len(X)):
                    gradient = gradient + (fouten[i] * X[i][j])
                gradient = gradient / len(X)
                
                # Update gewicht met gradiënt afdaling
                self.gewichten[j] = self.gewichten[j] - (self.leer_snelheid * gradient)
            
            # Bereken en bewaar fout voor deze iteratie
            huidige_fout = self.bereken_fout(y, voorspellingen)
            self.fouten_geschiedenis.append(huidige_fout)
            
            # Print voortgang elke 100 iteraties
            if iteratie % 100 == 0:
                print(f"Training iteratie {iteratie}, Fout: {huidige_fout:.4f}")

def schaal_kenmerken(data):
    """Schaal data naar bereik [0,1] met min-max schaling"""
    min_waarde = min(data)
    max_waarde = max(data)
    geschaalde_data = []
    
    if max_waarde > min_waarde:
        for x in data:
            geschaalde_waarde = (x - min_waarde) / (max_waarde - min_waarde)
            geschaalde_data.append(geschaalde_waarde)
        return geschaalde_data
    else:
        # Als alle waarden hetzelfde zijn, return lijst met nullen
        for x in data:
            geschaalde_data.append(0)
        return geschaalde_data

def voeg_bias_toe(X):
    """Voeg een kolom met enen toe aan onze data voor de bias term"""
    X_met_bias = []
    for rij in X:
        nieuwe_rij = [1]  # Voeg de bias term (1) toe aan het begin
        for waarde in rij:
            nieuwe_rij.append(waarde)
        X_met_bias.append(nieuwe_rij)
    return X_met_bias

# Hoofdprogramma
def hoofdprogramma():
    # Maak verbinding met database
    verbinding = maak_database_verbinding()
    
    if verbinding:
        # Haal data op uit database
        cursor = verbinding.cursor()
        cursor.execute("SELECT price, positive_ratings, genres, categories, average_playtime, name FROM games LIMIT 1000;")
        spellen_data = cursor.fetchall()
        verbinding.close()
        
        # Bereid data voor voor het model
        spellen = []
        weergave_info = []
        
        # Verwerk elk spel
        for spel in spellen_data:
            # Haal kenmerken op
            prijs = float(spel[0])
            positieve_beoordelingen = int(spel[1])
            
            # Tel aantal genres
            genres = spel[2].split(";")
            aantal_genres = len(genres)
            
            # Tel aantal categorieën
            categorieen = spel[3].split(";")
            aantal_categorieen = len(categorieen)
            
            speeltijd = int(spel[4])
            naam = spel[5]
            
            # Bewaar kenmerken en doel
            kenmerken = [prijs, positieve_beoordelingen, aantal_genres, aantal_categorieen]
            spellen.append((kenmerken, speeltijd))
            weergave_info.append((naam, speeltijd, positieve_beoordelingen))
        
        # Split kenmerken (X) en doel (y)
        X = []
        y = []
        for spel in spellen:
            X.append(spel[0])
            y.append(spel[1])
        
        # Schaal kenmerken
        kenmerken_per_kolom = []
        for i in range(len(X[0])):
            kolom = []
            for rij in X:
                kolom.append(rij[i])
            kenmerken_per_kolom.append(kolom)
        
        # Schaal elke kolom
        geschaalde_kolommen = []
        for kolom in kenmerken_per_kolom:
            geschaalde_kolom = schaal_kenmerken(kolom)
            geschaalde_kolommen.append(geschaalde_kolom)
        
        # Reorganiseer terug naar rijen
        X_geschaald = []
        for i in range(len(X)):
            rij = []
            for kol in geschaalde_kolommen:
                rij.append(kol[i])
            X_geschaald.append(rij)
        
        # Voeg bias term toe
        X_geschaald = voeg_bias_toe(X_geschaald)
        
        # Split in training en test sets (80% training, 20% test)
        training_grootte = int(0.8 * len(X_geschaald))
        
        X_train = []
        X_test = []
        y_train = []
        y_test = []
        
        # Split X data
        for i in range(len(X_geschaald)):
            if i < training_grootte:
                X_train.append(X_geschaald[i])
            else:
                X_test.append(X_geschaald[i])
        
        # Split y data
        for i in range(len(y)):
            if i < training_grootte:
                y_train.append(y[i])
            else:
                y_test.append(y[i])
        
        # Maak en train model
        model = LineaireRegressie(leer_snelheid=0.1, aantal_iteraties=500)
        model.train(X_train, y_train)
        
        # Test model
        test_voorspellingen = model.voorspel(X_test)
        test_fout = model.bereken_fout(y_test, test_voorspellingen)
        print(f"Test Fout: {test_fout:.4f}")
        
        # Maak voorspellingen voor alle spellen
        alle_voorspellingen = model.voorspel(X_geschaald)
        
        # Combineer voorspellingen met spel info
        spel_voorspellingen = []
        for i in range(len(alle_voorspellingen)):
            spel_voorspelling = (weergave_info[i][0], alle_voorspellingen[i], weergave_info[i][2])
            spel_voorspellingen.append(spel_voorspelling)
        
        # Sorteer spellen op voorspelde speeltijd
        spel_voorspellingen.sort(key=lambda x: x[1], reverse=True)
        
        # Pak top 10 spellen
        top_spellen = []
        for i in range(10):
            top_spellen.append(spel_voorspellingen[i])
        
        # Bereid data voor voor plot
        namen = []
        voorspelde_tijden = []
        beoordelingen = []
        for spel in top_spellen:
            namen.append(spel[0])
            voorspelde_tijden.append(spel[1])
            beoordelingen.append(spel[2])
        
        # Maak staafdiagram
        plt.figure(figsize=(10, 6))
        plt.barh(namen, voorspelde_tijden, color="skyblue")
        plt.xlabel("Voorspelde Speeltijd")
        plt.ylabel("Spelnamen")
        plt.title("Top 10 Spellen op Basis van Voorspelde Speeltijd")
        plt.gca().invert_yaxis()  # Toon hoogste waarde bovenaan
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.show()
    else:
        print("Kon geen gegevens ophalen uit de database.")

# Start het programma
if __name__ == "__main__":
    hoofdprogramma()