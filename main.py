from src.AlgoTrader import AlgoTrader

if __name__ == "__main__":
    print("Hello, Gemini!")

    print("algoTrader, started!")

    algoTrader = AlgoTrader()

    choice = 0
    if choice == 0:
        algoTrader.run_with_single_trader()
    elif choice == 1:
        algoTrader.run_with_multiple_trader()
    elif choice == 2:
        algoTrader.run_optimization_with_single_trader()
    else:
        pass

    print("algoTrader, finished!")
