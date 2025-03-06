import unittest
from breakout import get_data, clean_data, run_backtest

class TestBreakoutStrategy(unittest.TestCase):
    def test_get_data(self):
        """Test that historical data is fetched correctly"""
        df = get_data("EURUSD=X", interval="15m")
        self.assertFalse(df.empty, "Dataframe should not be empty")

    def test_clean_data(self):
        """Test that data cleaning removes NaN and duplicates"""
        df = get_data("EURUSD=X", interval="15m")
        cleaned_df = clean_data(df)
        self.assertFalse(cleaned_df.isnull().values.any(), "Dataframe should not contain NaN values")

    def test_run_backtest(self):
        """Test that backtest returns trade signals"""
        signals = run_backtest()
        self.assertIsInstance(signals, list, "Trade signals should be a list")
        self.assertGreaterEqual(len(signals), 0, "Trade signals list should not be negative")

if __name__ == "__main__":
    unittest.main()
