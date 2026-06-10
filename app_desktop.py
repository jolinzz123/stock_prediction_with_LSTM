# app_desktop.py
# Tkinter desktop GUI for the Stock Price Prediction System.
# Tkinter docs: https://docs.python.org/3/library/tkinter.html
# Threading approach for long-running tasks adapted from:
# https://docs.python.org/3/library/threading.html

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # pillow

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class StockPredictorApp:
    """Main Tkinter application window for stock price prediction."""

    # ── Colour palette ──────────────────────────────────────
    BG       = "#1e1e2e"
    PANEL    = "#2a2a3e"
    ACCENT   = "#7c6af7"
    ACCENT2  = "#ff8a65"
    TEXT     = "#e0e0e0"
    SUBTEXT  = "#9e9e9e"
    SUCCESS  = "#81c784"
    ERROR    = "#ef5350"
    ENTRY_BG = "#13131f"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📈 Stock Price Prediction System")
        self.root.geometry("820x680")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        self._build_ui()

    # ── UI construction ──────────────────────────────────────

    def _build_ui(self):
        """Construct all UI widgets."""

        # ── Header ──
        header = tk.Frame(self.root, bg=self.ACCENT, height=60)
        header.pack(fill="x")
        tk.Label(header,
                 text="📈  Stock Price Prediction System",
                 font=("Segoe UI", 16, "bold"),
                 bg=self.ACCENT, fg="white").pack(pady=12)

        # ── Input panel ──
        input_frame = tk.Frame(self.root, bg=self.PANEL, pady=20, padx=30)
        input_frame.pack(fill="x", padx=20, pady=(20, 0))

        # Ticker input
        tk.Label(input_frame, text="Stock Ticker Symbol",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.PANEL, fg=self.SUBTEXT).grid(row=0, column=0, sticky="w")

        self.ticker_var = tk.StringVar()
        ticker_entry = tk.Entry(input_frame, textvariable=self.ticker_var,
                                font=("Segoe UI", 13, "bold"),
                                bg=self.ENTRY_BG, fg=self.ACCENT,
                                insertbackground=self.ACCENT,
                                relief="flat", width=12)
        ticker_entry.grid(row=1, column=0, pady=(4, 0), ipady=8, padx=(0, 30))

        # Placeholder hint
        tk.Label(input_frame, text="e.g. AAPL  TSLA  GOOG  MSFT",
                 font=("Segoe UI", 8), bg=self.PANEL,
                 fg=self.SUBTEXT).grid(row=2, column=0, sticky="w")

        # Days slider
        tk.Label(input_frame, text="Forecast Days",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.PANEL, fg=self.SUBTEXT).grid(row=0, column=1, sticky="w")

        self.days_var = tk.IntVar(value=10)
        days_slider = ttk.Scale(input_frame, from_=1, to=30,
                                variable=self.days_var, orient="horizontal",
                                length=200,
                                command=lambda v: self.days_label.config(
                                    text=f"{int(float(v))} days"))
        days_slider.grid(row=1, column=1, pady=(4, 0), sticky="w")

        self.days_label = tk.Label(input_frame,
                                   text=f"{self.days_var.get()} days",
                                   font=("Segoe UI", 12, "bold"),
                                   bg=self.PANEL, fg=self.ACCENT2)
        self.days_label.grid(row=1, column=2, padx=12)

        # Retrain checkbox
        self.retrain_var = tk.BooleanVar(value=True)
        tk.Checkbutton(input_frame, text="Train new model",
                       variable=self.retrain_var,
                       font=("Segoe UI", 9),
                       bg=self.PANEL, fg=self.TEXT,
                       selectcolor=self.ENTRY_BG,
                       activebackground=self.PANEL).grid(row=2, column=1, sticky="w")

        # Predict button
        self.predict_btn = tk.Button(input_frame,
                                     text="  🔮  Predict  ",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=self.ACCENT, fg="white",
                                     activebackground="#6a5acd",
                                     relief="flat", cursor="hand2",
                                     command=self._start_prediction)
        self.predict_btn.grid(row=1, column=3, padx=(30, 0), ipady=6, ipadx=10)

        # ── Progress bar ──
        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=780)
        self.progress.pack(padx=20, pady=(12, 0))

        # ── Status label ──
        self.status_var = tk.StringVar(value="Enter a ticker and press Predict to begin.")
        tk.Label(self.root, textvariable=self.status_var,
                 font=("Segoe UI", 9), bg=self.BG,
                 fg=self.SUBTEXT).pack(pady=(4, 0))

        # ── Results panel ──
        results_frame = tk.Frame(self.root, bg=self.PANEL, pady=16, padx=24)
        results_frame.pack(fill="both", expand=True, padx=20, pady=12)

        # Metrics row
        metrics_row = tk.Frame(results_frame, bg=self.PANEL)
        metrics_row.pack(fill="x")

        self.metric_labels = {}
        for i, (key, title) in enumerate([
            ("price",  "Current Price"),
            ("target", "Day-N Target"),
            ("trend",  "Trend Signal"),
            ("mape",   "MAPE Error"),
        ]):
            col = tk.Frame(metrics_row, bg=self.ENTRY_BG,
                           padx=16, pady=10)
            col.grid(row=0, column=i, padx=6, sticky="nsew")
            metrics_row.columnconfigure(i, weight=1)

            tk.Label(col, text=title, font=("Segoe UI", 8),
                     bg=self.ENTRY_BG, fg=self.SUBTEXT).pack()
            lbl = tk.Label(col, text="—",
                           font=("Segoe UI", 13, "bold"),
                           bg=self.ENTRY_BG, fg=self.ACCENT)
            lbl.pack()
            self.metric_labels[key] = lbl

        # Forecast table
        tk.Label(results_frame, text="Price Forecast",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.PANEL, fg=self.SUBTEXT).pack(anchor="w", pady=(16, 4))

        table_frame = tk.Frame(results_frame, bg=self.PANEL)
        table_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=self.ENTRY_BG,
                        foreground=self.TEXT,
                        fieldbackground=self.ENTRY_BG,
                        rowheight=24,
                        font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading",
                        background=self.ACCENT,
                        foreground="white",
                        font=("Segoe UI", 9, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", self.ACCENT)])

        self.tree = ttk.Treeview(table_frame,
                                 columns=("day", "date", "price", "change"),
                                 show="headings",
                                 style="Custom.Treeview",
                                 height=8)
        for col, heading, width in [
            ("day",    "Day",         60),
            ("date",   "Date",       120),
            ("price",  "Price (USD)", 130),
            ("change", "Change",      100),
        ]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ── Chart button ──
        self.chart_btn = tk.Button(self.root,
                                   text="📊  Open Charts",
                                   font=("Segoe UI", 10),
                                   bg=self.PANEL, fg=self.TEXT,
                                   activebackground=self.ACCENT,
                                   relief="flat", cursor="hand2",
                                   state="disabled",
                                   command=self._open_charts)
        self.chart_btn.pack(pady=(0, 16))

        # ── Disclaimer ──
        tk.Label(self.root,
                 text="⚠  Educational use only. Not financial advice.",
                 font=("Segoe UI", 8), bg=self.BG,
                 fg=self.SUBTEXT).pack(pady=(0, 8))

    # ── Prediction logic ─────────────────────────────────────

    def _start_prediction(self):
        """Validate inputs then run prediction in a background thread."""
        ticker = self.ticker_var.get().strip().upper()
        days   = int(self.days_var.get())

        if not ticker or not ticker.isalpha() or len(ticker) > 5:
            messagebox.showerror("Invalid Input",
                                 "Please enter a valid ticker (1–5 letters, e.g. AAPL).")
            return

        self.predict_btn.config(state="disabled")
        self.chart_btn.config(state="disabled")
        self.progress.start(10)
        self._set_status(f"Fetching data for {ticker}...")
        self._clear_results()

        thread = threading.Thread(
            target=self._run_pipeline,
            args=(ticker, days, self.retrain_var.get()),
            daemon=True
        )
        thread.start()

    def _run_pipeline(self, ticker: str, days: int, retrain: bool):
        """Full ML pipeline executed in a background thread."""
        try:
            import numpy as np
            import pandas as pd
            from data_fetcher import fetch_stock_data, preprocess_data, train_test_split_timeseries
            from model import build_model, train_model, load_saved_model, MODEL_SAVE_PATH
            from predictor import predict_on_test_set, predict_future, calculate_metrics, get_trend_signal
            from visualizer import plot_prediction_results, plot_training_loss, plot_future_only

            LOOK_BACK   = 60
            SPLIT_RATIO = 0.8

            # 1. Fetch
            self._set_status(f"[1/5] Downloading {ticker} historical data...")
            df = fetch_stock_data(ticker)
            last_price = float(df['Close'].iloc[-1])

            # 2. Preprocess
            self._set_status("[2/5] Preprocessing data...")
            X, y, scaler = preprocess_data(df, look_back=LOOK_BACK)
            X_train, X_test, y_train, y_test = train_test_split_timeseries(
                X, y, SPLIT_RATIO)

            # 3. Train / load
            if retrain or not os.path.exists(MODEL_SAVE_PATH):
                self._set_status("[3/5] Training LSTM model (this takes 1–3 min)...")
                model = build_model(look_back=LOOK_BACK)
                model, history = train_model(model, X_train, y_train, epochs=30)
                plot_training_loss(history, ticker)
            else:
                self._set_status("[3/5] Loading saved model...")
                model = load_saved_model()

            # 4. Evaluate
            self._set_status("[4/5] Evaluating model on test set...")
            test_predicted = predict_on_test_set(model, X_test, scaler)
            test_actual    = scaler.inverse_transform(
                y_test.reshape(-1, 1)).flatten()
            metrics = calculate_metrics(test_actual, test_predicted)

            # 5. Forecast
            self._set_status(f"[5/5] Forecasting next {days} days...")
            future_prices = predict_future(model, df, scaler, days, LOOK_BACK)
            trend         = get_trend_signal(future_prices)

            # Charts
            plot_prediction_results(df, test_actual, test_predicted,
                                    future_prices, ticker, LOOK_BACK, SPLIT_RATIO)
            plot_future_only(df, future_prices, ticker)

            # Build forecast table data
            last_date    = pd.to_datetime(df.index[-1])
            future_dates = pd.bdate_range(
                start=last_date + pd.Timedelta(days=1), periods=days)

            table_rows = []
            prev = last_price
            for i, (price, date) in enumerate(
                    zip(future_prices, future_dates), 1):
                change = price - prev
                table_rows.append((
                    i,
                    date.strftime("%d %b %Y"),
                    f"${price:.2f}",
                    f"+${change:.2f}" if change >= 0 else f"-${abs(change):.2f}"
                ))
                prev = price

            # Update UI on main thread
            self.root.after(0, self._update_results,
                            last_price, future_prices[-1],
                            trend, metrics['MAPE'], table_rows, ticker)

        except Exception as exc:
            self.root.after(0, self._show_error, str(exc))

    def _update_results(self, current: float, target: float,
                        trend: str, mape: float, rows: list, ticker: str):
        """Push results to the UI (called on the main thread)."""
        self.progress.stop()
        self.predict_btn.config(state="normal")
        self.chart_btn.config(state="normal")
        self._set_status(f"✓ Prediction complete for {ticker}.")

        self.metric_labels["price"].config( text=f"${current:.2f}", fg=self.TEXT)
        self.metric_labels["target"].config(text=f"${target:.2f}",  fg=self.ACCENT2)
        self.metric_labels["trend"].config( text=trend,              fg=self.SUCCESS)
        self.metric_labels["mape"].config(  text=f"{mape:.2f}%",    fg=self.SUBTEXT)

        for row in rows:
            tag = "up" if row[3].startswith("+") else "down"
            self.tree.insert("", "end", values=row, tags=(tag,))

        self.tree.tag_configure("up",   foreground=self.SUCCESS)
        self.tree.tag_configure("down", foreground=self.ERROR)

        self._current_ticker = ticker

    def _show_error(self, message: str):
        self.progress.stop()
        self.predict_btn.config(state="normal")
        self._set_status(f"✗ Error: {message}")
        messagebox.showerror("Error", message)

    def _clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for lbl in self.metric_labels.values():
            lbl.config(text="—")

    def _set_status(self, msg: str):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def _open_charts(self):
        """Open saved chart images using the default system viewer."""
        import subprocess
        import platform
        ticker = getattr(self, '_current_ticker', '')
        assets = os.path.join(os.path.dirname(__file__), "assets")
        charts = [
            os.path.join(assets, f"{ticker}_forecast.png"),
            os.path.join(assets, f"{ticker}_prediction.png"),
        ]
        for path in charts:
            if os.path.exists(path):
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", path])
                else:
                    subprocess.call(["xdg-open", path])


def run_desktop():
    """Launch the Tkinter desktop application."""
    root = tk.Tk()
    app  = StockPredictorApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_desktop()
