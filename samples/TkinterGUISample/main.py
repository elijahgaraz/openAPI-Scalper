#!/usr/bin/env python
"""Simple Tkinter GUI for interacting with OpenApiPy."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from ctrader_open_api import Client, TcpProtocol, EndPoints
from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOAApplicationAuthReq
from twisted.internet import reactor, tksupport


class ScalperGUI:
    """Minimal GUI with Trading and Settings tabs."""

    def __init__(self, root):
        self.root = root
        root.title("cTrader Scalper")
        self.client = None
        self.access_token = None
        self.account_id = None

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self._create_trading_tab(notebook)
        self._create_settings_tab(notebook)

    def _create_trading_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Trading")

        # Dropdown for forex pairs
        pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF"]
        ttk.Label(frame, text="Pair:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pair_var = tk.StringVar(value=pairs[0])
        ttk.OptionMenu(frame, self.pair_var, pairs[0], *pairs).grid(row=0, column=1, padx=5, pady=5)

        # Dropdown for strategy
        strategies = ["safe", "moderate", "aggressive", "trends", "scalping"]
        ttk.Label(frame, text="Strategy:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.strategy_var = tk.StringVar(value=strategies[0])
        ttk.OptionMenu(frame, self.strategy_var, strategies[0], *strategies).grid(row=1, column=1, padx=5, pady=5)

        # Profit/loss metrics
        metrics_frame = ttk.LabelFrame(frame, text="Metrics")
        metrics_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.balance_var = tk.StringVar(value="Balance: 0")
        self.pnl_var = tk.StringVar(value="PnL: 0")
        ttk.Label(metrics_frame, textvariable=self.balance_var).pack(anchor="w")
        ttk.Label(metrics_frame, textvariable=self.pnl_var).pack(anchor="w")

        # Log area
        ttk.Label(frame, text="Activity Log:").grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
        self.log = scrolledtext.ScrolledText(frame, width=60, height=10, state="disabled")
        self.log.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Start/stop buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=5)
        ttk.Button(btn_frame, text="Scalp", command=self.start_scalp).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="End Trading", command=self.stop_scalp).pack(side="left", padx=5)

        frame.columnconfigure(1, weight=1)

    def _create_settings_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Settings")

        ttk.Label(frame, text="Client ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.client_id_entry = ttk.Entry(frame)
        self.client_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Client Secret:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.client_secret_entry = ttk.Entry(frame, show="*")
        self.client_secret_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Access Token:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.token_entry = ttk.Entry(frame)
        self.token_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Connect", command=self.connect).grid(row=3, column=0, columnspan=2, pady=5)

        frame.columnconfigure(1, weight=1)

    # GUI methods

    def log_message(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.configure(state="disabled")
        self.log.see("end")

    def connect(self):
        client_id = self.client_id_entry.get()
        client_secret = self.client_secret_entry.get()
        self.access_token = self.token_entry.get()

        self.client = Client(EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)

        def on_connected(_):
            self.log_message("Connected")
            req = ProtoOAApplicationAuthReq()
            req.clientId = client_id
            req.clientSecret = client_secret
            self.client.send(req).addErrback(lambda f: self.log_message(str(f)))

        def on_disconnected(_, reason):
            self.log_message(f"Disconnected: {reason}")

        self.client.setConnectedCallback(on_connected)
        self.client.setDisconnectedCallback(on_disconnected)
        self.client.setMessageReceivedCallback(lambda _, msg: self.log_message(str(msg)))
        self.client.startService()

    def start_scalp(self):
        self.log_message(f"Starting scalping {self.pair_var.get()} using {self.strategy_var.get()} strategy")
        # Placeholder for real scalping logic

    def stop_scalp(self):
        self.log_message("Stopping trading")
        if self.client:
            self.client.stopService()


if __name__ == "__main__":
    root = tk.Tk()
    tksupport.install(root)
    app = ScalperGUI(root)
    reactor.run()

