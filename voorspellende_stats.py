import psycopg2
import matplotlib.pyplot as plt

class Game:
    def __init__(self, price, positive_ratings):
        self.price = float(price)
        self.positive_ratings = float(positive_ratings)

class DatabaseConnection:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Successfully connected to database!")
            return self.connection
        except Exception as error:
            print(f"Could not connect to database: {error}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()

class DataProcessor:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.games = []

    def fetch_data(self, limit=100):
        connection = self.db_connection.connect()
        if connection:
            cursor = connection.cursor()
            query = """
                WITH filtered_games AS (
                    SELECT 
                        CAST(price AS NUMERIC) as price, 
                        CAST(positive_ratings AS INTEGER) as positive_ratings
                    FROM games
                    WHERE 
                        price IS NOT NULL 
                        AND positive_ratings IS NOT NULL 
                        AND CAST(price AS NUMERIC) BETWEEN 5 AND 40
                        AND CAST(positive_ratings AS INTEGER) BETWEEN 100 AND 5000
                        AND CAST(average_playtime AS INTEGER) > 0
                )
                SELECT price, positive_ratings
                FROM filtered_games
                WHERE price > (SELECT AVG(price) - 2 * STDDEV(price) FROM filtered_games)
                AND price < (SELECT AVG(price) + 2 * STDDEV(price) FROM filtered_games)
                ORDER BY positive_ratings ASC
                LIMIT %s;
            """
            cursor.execute(query, (limit,))
            data = cursor.fetchall()
            self.games = [Game(price, ratings) for price, ratings in data]
            connection.close()
            return self.games
        return []

    def normalize_data(self):
        if not self.games:
            return [], [], []

        prices = [game.price for game in self.games]
        ratings = [game.positive_ratings for game in self.games]
        
        price_min, price_max = min(prices), max(prices)
        normalized_prices = [
            (price - price_min) / (price_max - price_min) 
            for price in prices
        ]
        
        return normalized_prices, ratings, prices

class LinearRegression:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.theta0 = 0
        self.theta1 = 0

    def train(self, X, y):
        m = len(y)
        
        for _ in range(self.iterations):
            h = [self.theta0 + self.theta1 * x for x in X]
            gradient0 = sum(h_i - y_i for h_i, y_i in zip(h, y)) / m
            gradient1 = sum((h_i - y_i) * x for h_i, y_i, x in zip(h, y, X)) / m
            self.theta0 -= self.learning_rate * gradient0
            self.theta1 -= self.learning_rate * gradient1

    def predict(self, X):
        return [self.theta0 + self.theta1 * x for x in X]

    def compute_r_squared(self, y, y_pred):
        y_mean = sum(y) / len(y)
        ss_total = sum((y_i - y_mean) * (y_i - y_mean) for y_i in y)
        ss_residual = sum((y_i - y_pred_i) * (y_i - y_pred_i) 
                         for y_i, y_pred_i in zip(y, y_pred))
        return 1 - (ss_residual / ss_total)

class Visualizer:
    @staticmethod
    def plot_regression(original_prices, y, y_pred, r_squared):
        plt.figure(figsize=(10, 6), facecolor='white')
        ax = plt.gca()
        ax.set_facecolor('white')
        
        # Plot scatter points
        plt.scatter(original_prices, y, 
                   color='#3498db',
                   alpha=0.6, 
                   s=70,
                   label='Games')
        
        # Sort data for line plot
        sorted_indices = sorted(range(len(original_prices)), 
                              key=lambda k: original_prices[k])
        sorted_prices = [original_prices[i] for i in sorted_indices]
        sorted_predictions = [y_pred[i] for i in sorted_indices]
        
        # Plot regression line
        plt.plot(sorted_prices, sorted_predictions, 
                color='#e74c3c',
                linewidth=2.5,
                label=f'Regression Line (R² = {r_squared:.4f})')
        
        plt.grid(True, linestyle='--', alpha=0.3, color='gray')
        
        plt.xlabel('Game Price ($)', fontsize=12, fontweight='bold')
        plt.ylabel('Positive Ratings', fontsize=12, fontweight='bold')
        plt.title('Steam Games: Price vs Positive Ratings', 
                 fontsize=14, 
                 fontweight='bold', 
                 pad=20)
        
        plt.legend(loc='upper right', 
                  frameon=True, 
                  facecolor='white', 
                  edgecolor='none',
                  fontsize=10)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.margins(x=0.1)
        plt.tight_layout()
        plt.show()

class SteamAnalyzer:
    def __init__(self, db_config):
        self.db_connection = DatabaseConnection(**db_config)
        self.data_processor = DataProcessor(self.db_connection)
        self.model = LinearRegression()
        self.visualizer = Visualizer()

    def analyze(self, limit=100):
        print("Fetching data from database...")
        games = self.data_processor.fetch_data(limit)
        
        if not games:
            print("No data fetched from database!")
            return
            
        print(f"Fetched {len(games)} records")
        
        X, y, original_prices = self.data_processor.normalize_data()
        
        print("\nTraining model...")
        self.model.train(X, y)
        
        y_pred = self.model.predict(X)
        r_squared = self.model.compute_r_squared(y, y_pred)
        
        print("\nGenerating visualization...")
        self.visualizer.plot_regression(original_prices, y, y_pred, r_squared)



if __name__ == "__main__":
    main()