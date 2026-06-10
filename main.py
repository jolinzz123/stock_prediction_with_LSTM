# main.py
# Entry point for the Stock Price Prediction Application.
# Run this file to choose between Desktop (Tkinter) or Web (Flask) interface.

import sys
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def main():
    print("=" * 50)
    print("   📈  STOCK PRICE PREDICTION SYSTEM  📈")
    print("=" * 50)
    print("\nChoose interface:")
    print("  1 — Desktop App  (Tkinter window)")
    print("  2 — Web App      (Flask browser)")
    print()

    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            from app_desktop import run_desktop
            run_desktop()
            break
        elif choice == "2":
            from app_web import run_web
            run_web()
            break
        else:
            print("  Please enter 1 or 2.")


if __name__ == "__main__":
    main()
