import os
from src.AlgoTrader import AlgoTrader

if __name__ == "__main__":
    print("\n")
    print("Hello, Gemini!")
    print("algoTrader, started!")

    algoTrader = AlgoTrader()

    choice = 0  # 0: single trader, 1: multiple trader, 2: optimization single trader
    if choice == 0:
        algoTrader.run_with_single_trader()
    elif choice == 1:
        algoTrader.run_with_multiple_trader(4)
    elif choice == 2:
        algoTrader.run_optimization_with_single_trader()
    else:
        pass

    print("\n")
    print("algoTrader, finished!")