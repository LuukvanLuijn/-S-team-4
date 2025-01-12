import json
import matplotlib.pyplot as plt

class LineaireRegressie:
    """Een eenvoudige lineaire regressie implementatie met data normalisatie."""
    
    def __init__(self, leersnelheid=0.01, iteraties=1000):
        """Initialiseer het model met leersnelheid en aantal iteraties."""
        self.leersnelheid = leersnelheid
        self.iteraties = iteraties
        self.gewichten = None
        self.bias = None
        
    def normaliseer_data(self, X):
        """Normaliseer features naar bereik [0,1]."""
        X_min = min(X)
        X_max = max(X)
        return [(x - X_min)/(X_max - X_min) for x in X], (X_min, X_max)
    
    def train(self, X, y):
        """Train het model met gebruik van gradiënt afdaling."""
        # Normaliseer data
        X_norm, (X_min, X_max) = self.normaliseer_data(X)
        y_norm, (y_min, y_max) = self.normaliseer_data(y)
        
        n_samples = len(X_norm)
        self.gewichten = 1.0
        self.bias = 0.0
        
        for _ in range(self.iteraties):
            y_voorspeld = [self.gewichten * x + self.bias for x in X_norm]
            
            dw = (-2/n_samples) * sum((y_norm[j] - y_voorspeld[j]) * X_norm[j] for j in range(n_samples))
            db = (-2/n_samples) * sum(y_norm[j] - y_voorspeld[j] for j in range(n_samples))
            
            self.gewichten -= self.leersnelheid * dw
            self.bias -= self.leersnelheid * db
        
        # Denormaliseer parameters
        self.gewichten = self.gewichten * (y_max - y_min)/(X_max - X_min)
        self.bias = y_min + (y_max - y_min) * self.bias - self.gewichten * X_min
    
    def voorspel(self, X):
        """Maak voorspellingen voor gegeven input features."""
        return [self.gewichten * x + self.bias for x in X]

def bereken_correlatie(X, y):
    """Bereken Pearson correlatie coëfficiënt tussen twee variabelen."""
    n = len(X)
    if n == 0:
        return 0
    
    gemiddelde_x = sum(X) / n
    gemiddelde_y = sum(y) / n
    
    variantie_x = sum((x - gemiddelde_x) ** 2 for x in X)
    variantie_y = sum((y - gemiddelde_y) ** 2 for y in y)
    
    covariantie = sum((X[i] - gemiddelde_x) * (y[i] - gemiddelde_y) for i in range(n))
    
    if variantie_x * variantie_y == 0:
        return 0
        
    return covariantie / ((variantie_x * variantie_y) ** 0.5)

def bereken_r_kwadraat(y_waar, y_voorspeld):
    """Bereken R-kwadraat (determinatiecoëfficiënt) score."""
    gemiddelde_y = sum(y_waar) / len(y_waar)
    ss_tot = sum((y - gemiddelde_y) ** 2 for y in y_waar)
    ss_res = sum((y_waar[i] - y_voorspeld[i]) ** 2 for i in range(len(y_waar)))
    
    if ss_tot == 0:
        return 0
    return 1 - (ss_res / ss_tot)

def plot_vergelijking(X, y):
    """Maak vergelijkingsplots voor volledige bereik en 0-10k segment van de data."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Volledige bereik plot (0-50k)
    model_volledig = LineaireRegressie()
    model_volledig.train(X, y)
    
    ax1.scatter(X, y, color='blue', alpha=0.5, s=50, label='Werkelijke Data')
    
    X_gesorteerd = sorted(X)
    y_voorspeld = model_volledig.voorspel(X_gesorteerd)
    
    ax1.plot(X_gesorteerd, y_voorspeld, color='red', linestyle='--', 
    linewidth=2, label='Regressielijn')
    
    correlatie_volledig = bereken_correlatie(X, y)
    r_kwadraat_volledig = bereken_r_kwadraat(y, model_volledig.voorspel(X))
    
    stats_tekst = f'N: {len(X)}\nCorrelatie: {correlatie_volledig:.4f}\nR²: {r_kwadraat_volledig:.4f}'
    ax1.text(0.05, 0.95, stats_tekst, transform=ax1.transAxes,
    bbox=dict(facecolor='white', alpha=0.8),
    verticalalignment='top')
    
    ax1.set_xlabel('Piek Spelers')
    ax1.set_ylabel('Gespeelde Uren')
    ax1.set_title('Alle Games (0-50k piek spelers)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 0-10k segment plot
    X_segment = []
    y_segment = []
    for i, x in enumerate(X):
        if x < 10000:
            X_segment.append(x)
            y_segment.append(y[i])
    
    model_segment = LineaireRegressie()
    model_segment.train(X_segment, y_segment)
    
    ax2.scatter(X_segment, y_segment, color='blue', alpha=0.5, s=50, label='Werkelijke Data')
    
    X_gesorteerd_segment = sorted(X_segment)
    y_voorspeld_segment = model_segment.voorspel(X_gesorteerd_segment)
    
    ax2.plot(X_gesorteerd_segment, y_voorspeld_segment, color='red', linestyle='--', 
    linewidth=2, label='Regressielijn')
    
    correlatie_segment = bereken_correlatie(X_segment, y_segment)
    r_kwadraat_segment = bereken_r_kwadraat(y_segment, model_segment.voorspel(X_segment))
    
    stats_tekst = f'N: {len(X_segment)}\nCorrelatie: {correlatie_segment:.4f}\nR²: {r_kwadraat_segment:.4f}'
    ax2.text(0.05, 0.95, stats_tekst, transform=ax2.transAxes,
    bbox=dict(facecolor='white', alpha=0.8), verticalalignment='top')
    
    ax2.set_xlabel('Piek Spelers')
    ax2.set_ylabel('Gespeelde Uren')
    ax2.set_title('Games met 0-10k piek spelers')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.suptitle('Steam Games: Piek Spelers vs Gespeelde Uren - Volledig Bereik vs Best Segment', fontsize=14)
    plt.tight_layout()
    plt.show()

def main():
    """Laad Steam games data en maak visualisatie van spelersstatistieken."""
    try:
        # Load data
        try:
            with open('steam_games.json', 'r') as f:
                data = json.load(f)
        except:
            with open('-S-team-4/steam_games.json', 'r') as f:
                data = json.load(f)
        
        X = []  # piek_spelers
        y = []  # gespeelde_uren
        
        for spel in data:
            piek_spelers = spel['peak_players']
            if piek_spelers < 50000:  # Filter voor spellen met <50k piek spelers
                X.append(piek_spelers)
                y.append(spel['hours_played'])
        
        print(f"Geladen: {len(X)} spellen")
        plot_vergelijking(X, y)
        
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")

if __name__ == "__main__":
    main()
