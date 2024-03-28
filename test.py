import json
import threading
import time
from kiteconnect import KiteConnect

class StockWishlistApp:
    def __init__(self, api_key, api_secret, access_token):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token

        # Initialize KiteConnect instances for buying and selling
        self.buy_kite = KiteConnect(api_key=self.api_key)
        self.sell_kite = KiteConnect(api_key=self.api_key)

        # Set access tokens
        self.buy_kite.set_access_token(self.access_token)
        self.sell_kite.set_access_token(self.access_token)

        # Initialize stock prices
        self.stock_prices = {}
        self.subscribed_instruments = [[] for _ in range(10)]  # List of lists for 10 wishlists

        # Create a separate thread for real-time updates
        self.update_thread = threading.Thread(target=self.update_stock_prices_thread, daemon=True)
        self.update_thread.start()

        # Fetch all instruments from Kite API
        self.all_instruments = self.get_all_instruments()

        # Load subscribed instruments from JSON files
        self.load_subscribed_instruments()

    def update_stock_prices_thread(self):
        self.load_subscribed_instruments()
        while True:
            self.update_stock_prices()
            time.sleep(1)

    def update_stock_prices(self):
        for stock_list in self.subscribed_instruments:
            for stock in stock_list:
                try:
                    ticker_data = self.buy_kite.ltp(["NSE:" + stock, "NFO:" + stock])
                    last_price = ticker_data["NSE:" + stock]["last_price"] if "NSE:" + stock in ticker_data else ticker_data["NFO:" + stock]["last_price"]
                    self.stock_prices[stock] = last_price
                except Exception as e:
                    print(f"Failed to fetch price for {stock}: {str(e)}")

    def get_all_instruments(self):
        try:
            nse_equity_instruments = self.buy_kite.instruments("NSE")
            nse_nfo_instruments = self.buy_kite.instruments("NFO")
            nse_equity_symbols = [instrument['tradingsymbol'] for instrument in nse_equity_instruments]
            nse_nfo_symbols = [instrument['tradingsymbol'] for instrument in nse_nfo_instruments]

            all_instruments = nse_equity_symbols + nse_nfo_symbols
            return all_instruments

        except Exception as e:
            print(f"Failed to fetch all instruments: {str(e)}")
            return []

    def load_subscribed_instruments_from_file(self, wishlist_index):
        tab_filename = f"wishlist_tab_{wishlist_index + 1}.json"
        try:
            with open(tab_filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def load_subscribed_instruments(self):
        for i in range(10):
            self.subscribed_instruments[i] = self.load_subscribed_instruments_from_file(i)

    def place_order(self, stock_symbol, quantity, transaction_type, kite_instance):
        try:
            order_id = kite_instance.place_order(
                tradingsymbol=stock_symbol,
                exchange=kite_instance.EXCHANGE_NSE,
                transaction_type=transaction_type,
                quantity=quantity,
                price=self.stock_prices[stock_symbol],
                variety=kite_instance.VARIETY_REGULAR,
                order_type=kite_instance.ORDER_TYPE_LIMIT,
                product=kite_instance.PRODUCT_CNC
            )

            print(f"Order placed successfully for {stock_symbol}. Order ID is: {order_id}")
            return order_id
        except Exception as e:
            print(f"Order placement failed for {stock_symbol}: {str(e)}")
            return None

if __name__ == "__main__":
    # Replace these with your actual credentials
    api_key = "ce17fet4bjf7fg4c"
    api_secret = "4xsvbdlafnt2pk5slaw31qaeyz55joc9"
    access_token = "uPANj0LdDVJlpokY92E6kv8x9gbTIK56"

    app = StockWishlistApp(api_key, api_secret, access_token)

    # Example usage:
    # Place a buy order for a stock
    stock_symbol = "RELIANCE"
    quantity = 1
    app.place_order(stock_symbol, quantity, "BUY", app.buy_kite)

    # # Place a sell order for a stock
    # stock_symbol = "TATAMOTORS"
    # quantity = 2
    # app.place_order(stock_symbol, quantity, "SELL", app.sell_kite)
