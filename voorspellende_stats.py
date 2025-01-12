import json
import matplotlib.pyplot as plt

class LinearRegression:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.weights = None
        self.bias = None
        
    def normalize_data(self, X):
        X_min = min(X)
        X_max = max(X)
        return [(x - X_min)/(X_max - X_min) for x in X], (X_min, X_max)
    
    def fit(self, X, y):
        # Normalize data
        X_norm, (X_min, X_max) = self.normalize_data(X)
        y_norm, (y_min, y_max) = self.normalize_data(y)
        
        n_samples = len(X_norm)
        self.weights = 1.0
        self.bias = 0.0
        
        for _ in range(self.iterations):
            y_pred = [self.weights * x + self.bias for x in X_norm]
            
            dw = (-2/n_samples) * sum((y_norm[j] - y_pred[j]) * X_norm[j] for j in range(n_samples))
            db = (-2/n_samples) * sum(y_norm[j] - y_pred[j] for j in range(n_samples))
            
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
        
        # Denormalize parameters
        self.weights = self.weights * (y_max - y_min)/(X_max - X_min)
        self.bias = y_min + (y_max - y_min) * self.bias - self.weights * X_min
    
    def predict(self, X):
        return [self.weights * x + self.bias for x in X]

def compute_correlation(X, y):
    n = len(X)
    if n == 0:
        return 0
    
    mean_x = sum(X) / n
    mean_y = sum(y) / n
    
    variance_x = sum((x - mean_x) ** 2 for x in X)
    variance_y = sum((y - mean_y) ** 2 for y in y)
    
    covariance = sum((X[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    
    if variance_x * variance_y == 0:
        return 0
        
    return covariance / ((variance_x * variance_y) ** 0.5)

def compute_r_squared(y_true, y_pred):
    mean_y = sum(y_true) / len(y_true)
    ss_tot = sum((y - mean_y) ** 2 for y in y_true)
    ss_res = sum((y_true[i] - y_pred[i]) ** 2 for i in range(len(y_true)))
    
    if ss_tot == 0:
        return 0
    return 1 - (ss_res / ss_tot)

def plot_comparison(X, y):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Full range plot (0-50k)
    model_full = LinearRegression()
    model_full.fit(X, y)
    
    ax1.scatter(X, y, color='blue', alpha=0.5, s=50, label='Actual Data')
    
    X_sorted = sorted(X)
    y_pred = model_full.predict(X_sorted)
    
    ax1.plot(X_sorted, y_pred, color='red', linestyle='--', 
    linewidth=2, label='Regression Line')
    
    correlation_full = compute_correlation(X, y)
    r_squared_full = compute_r_squared(y, model_full.predict(X))
    
    stats_text = f'N: {len(X)}\nCorrelation: {correlation_full:.4f}\nR²: {r_squared_full:.4f}'
    ax1.text(0.05, 0.95, stats_text, transform=ax1.transAxes,
    bbox=dict(facecolor='white', alpha=0.8),
    verticalalignment='top')
    
    ax1.set_xlabel('Peak Players')
    ax1.set_ylabel('Hours Played')
    ax1.set_title('All Games (0-50k peak players)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 0-10k segment plot
    X_segment = []
    y_segment = []
    for i, x in enumerate(X):
        if x < 10000:
            X_segment.append(x)
            y_segment.append(y[i])
    
    model_segment = LinearRegression()
    model_segment.fit(X_segment, y_segment)
    
    ax2.scatter(X_segment, y_segment, color='blue', alpha=0.5, s=50, label='Actual Data')
    
    X_sorted_segment = sorted(X_segment)
    y_pred_segment = model_segment.predict(X_sorted_segment)
    
    ax2.plot(X_sorted_segment, y_pred_segment, color='red', linestyle='--', 
    linewidth=2, label='Regression Line')
    
    correlation_segment = compute_correlation(X_segment, y_segment)
    r_squared_segment = compute_r_squared(y_segment, model_segment.predict(X_segment))
    
    stats_text = f'N: {len(X_segment)}\nCorrelation: {correlation_segment:.4f}\nR²: {r_squared_segment:.4f}'
    ax2.text(0.05, 0.95, stats_text, transform=ax2.transAxes,
    bbox=dict(facecolor='white', alpha=0.8),
    verticalalignment='top')
    
    ax2.set_xlabel('Peak Players')
    ax2.set_ylabel('Hours Played')
    ax2.set_title('Games with 0-10k peak players')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.suptitle('Steam Games: Peak Players vs Hours Played - Full Range vs Best Segment', fontsize=14)
    plt.tight_layout()
    plt.show()
def main():
    try:
        # Load data
        with open('-S-team-4/steam_games.json', 'r') as f:
            data = json.load(f)
        
        X = []  # peak_players
        y = []  # hours_played
        
        for game in data:
            peak_players = game['peak_players']
            if peak_players < 50000:  # Filter for games with <50k peak players
                X.append(peak_players)
                y.append(game['hours_played'])
        
        print(f"Loaded {len(X)} games")
        plot_comparison(X, y)
        
    except Exception as e:
        print(f"An error occurred: {e}")
if __name__ == "__main__":
    main()
