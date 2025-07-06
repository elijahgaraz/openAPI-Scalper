#!/usr/bin/env python
"""Simple Tkinter GUI for interacting with OpenApiPy."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from ctrader_open_api import Client, TcpProtocol, EndPoints
from strategies import StrategyManager # Import StrategyManager

from twisted.internet import reactor, tksupport

# Define cTrader Open API endpoint details (use demo for testing)
# For live trading, use live.ctraderapi.com
DEMO_HOST = "demo.ctraderapi.com"
# PROD_HOST = "live.ctraderapi.com"
PORT = 5035


class ScalperGUI:
    """Minimal GUI with Trading and Settings tabs."""

    def __init__(self, root):
        self.root = root
        root.title("cTrader Scalper")
        self.client = None
        self.access_token = None # Will be fetched from entry
        self.account_id = None # Will be fetched from entry
        self.strategy_manager = None


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
        ttk.OptionMenu(frame, self.strategy_var, strategies[0], *strategies).grid(row=1, column=1, padx=5, pady=5, sticky="ew")


        # Profit/loss metrics
        metrics_frame = ttk.LabelFrame(frame, text="Metrics")
        metrics_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.balance_var = tk.StringVar(value="Balance: 0")
        self.pnl_var = tk.StringVar(value="PnL: 0")
        ttk.Label(metrics_frame, textvariable=self.balance_var).pack(anchor="w")
        ttk.Label(metrics_frame, textvariable=self.pnl_var).pack(anchor="w")

        # Log area

        self.log = scrolledtext.ScrolledText(frame, width=60, height=10, state="disabled")
        self.log.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Start/stop buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=5)
        self.start_scalp_button = ttk.Button(btn_frame, text="Scalp", command=self.start_scalp, state="disabled")
        self.start_scalp_button.pack(side="left", padx=5)
        self.stop_scalp_button = ttk.Button(btn_frame, text="End Trading", command=self.stop_scalp, state="disabled")
        self.stop_scalp_button.pack(side="left", padx=5)

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
        self.token_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame, text="Account ID:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.account_id_entry = ttk.Entry(frame)
        self.account_id_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Connect button
        self.connect_button = ttk.Button(frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=4, column=0, columnspan=2, pady=10)


        frame.columnconfigure(1, weight=1)
        frame.grid_columnconfigure(1, weight=1) # Ensure entry widgets expand

    # GUI methods

    def log_message(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.configure(state="disabled")
        self.log.see("end")

    def on_connected(self, client):
        self.log_message("Successfully connected to cTrader Open API (TCP layer).")
        self.log_message("Next critical steps: Application and Account Authentication.")
        self.connect_button.config(state="disabled") # Connected, so disable connect button

        # Authentication logic (e.g., sending ProtoOAApplicationAuthReq) would go here.
        # For now, we assume connection implies readiness for demo purposes.
        # self.authenticate_application() # This would be the next logical call

        if self.client and self.account_id: # Ensure client and account_id are set
            try:
                self.strategy_manager = StrategyManager(client=self.client, account_id=self.account_id, log=self.log_message)
                self.log_message("StrategyManager initialized and ready.")
                self.start_scalp_button.config(state="normal")
                self.stop_scalp_button.config(state="disabled")
            except Exception as e:
                self.log_message(f"Error initializing StrategyManager: {e}")
                self.start_scalp_button.config(state="disabled")
                self.stop_scalp_button.config(state="disabled")
        else:
            self.log_message("Client or Account ID not available for StrategyManager. Trading disabled.")
            self.start_scalp_button.config(state="disabled")
            self.stop_scalp_button.config(state="disabled")


    def connect(self):
        if self.client and self.client.isConnected:
            self.log_message("Already connected. Please disconnect first if you want to reconnect.")
            self.connect_button.config(state="disabled")
            return

        self.connect_button.config(state="disabled") # Disable while attempting
        self.log_message("Attempting to connect...")

        client_id_str = self.client_id_entry.get()
        # client_secret_str = self.client_secret_entry.get() # For auth messages
        self.access_token = self.token_entry.get() # For auth messages

        try:
            raw_account_id = self.account_id_entry.get()
            if not raw_account_id:
                raise ValueError("Account ID cannot be empty.")
            self.account_id = int(raw_account_id)
        except ValueError as e:
            self.log_message(f"Error: Invalid Account ID. {e}")
            self.connect_button.config(state="normal") # Re-enable connect button
            return

        if not self.access_token:
            self.log_message("Error: Access Token is required.")
            self.connect_button.config(state="normal")
            return
        if not client_id_str:
            self.log_message("Error: Client ID is required.")
            self.connect_button.config(state="normal")
            return

        host = DEMO_HOST
        port = PORT

        if not self.client:
            try:
                self.log_message(f"Initializing client for {host}:{port}...")
                self.client = Client(host, port, TcpProtocol)
                self.client.setConnectedCallback(self.on_connected)
                self.client.setDisconnectedCallback(self.on_disconnected)
                self.client.setMessageReceivedCallback(self._on_message_received)
                self.log_message("Client initialized.")
            except Exception as e:
                self.log_message(f"Fatal Error initializing client: {e}")
                self.client = None
                self.connect_button.config(state="normal")
                return

        if self.client and not self.client.running:
            try:
                self.log_message("Starting connection service...")
                self.client.startService()
                self.log_message("Connection service started. Waiting for connection callback...")
                # Connect button remains disabled until on_connected or on_disconnected updates it
            except Exception as e:
                self.log_message(f"Fatal Error starting connection service: {e}")
                self.connect_button.config(state="normal")
        elif self.client and self.client.running:
            self.log_message("Connection service already running. Waiting for connection callback or using existing.")
            # If it's running but not connected, ClientService handles retries.
            # Connect button remains disabled.


    def on_disconnected(self, client, reason):
        self.log_message(f"Disconnected from server: {reason}")
        self.log_message("Please check credentials, network, and server status.")
        if self.strategy_manager:
            self.strategy_manager.stop()
            self.log_message("Strategy stopped due to disconnection.")
        self.start_scalp_button.config(state="disabled")
        self.stop_scalp_button.config(state="disabled")
        self.connect_button.config(state="normal") # Allow user to attempt reconnection
        # self.client = None # Or rely on ClientService to retry. If set to None, next connect re-instantiates.
                           # For now, allow ClientService to manage its state for retries.

    def _on_message_received(self, client, message):
        # This is a generic handler. Specific responses are handled by Deferreds.
        self.log_message(f"RECV: {message.payloadType if hasattr(message, 'payloadType') else type(message)}")
        # More detailed logging or processing can be added here if needed.

    def start_scalp(self):
        if not (self.client and self.client.isConnected and self.account_id and self.strategy_manager):
            self.log_message("Cannot start scalp: Not connected, account ID missing, or strategy manager not initialized.")
            return

        selected_pair = self.pair_var.get()
        selected_strategy = self.strategy_var.get()

        self.log_message(f"Starting '{selected_strategy}' strategy for {selected_pair}.")
        try:
            self.strategy_manager.start(name=selected_strategy, pair=selected_pair)
            self.start_scalp_button.config(state="disabled")
            self.stop_scalp_button.config(state="normal")
        except Exception as e:
            self.log_message(f"Error starting strategy: {e}")


    def stop_scalp(self):
        self.log_message("Stopping trading strategy...")
        if self.strategy_manager:
            self.strategy_manager.stop()
        # self.log_message("Trading strategy stopped.") # Already logged by StrategyManager
        self.start_scalp_button.config(state="normal" if self.client and self.client.isConnected else "disabled")
        self.stop_scalp_button.config(state="disabled")
        # Note: self.client.stopService() is not called here, as we might want to stop the strategy
        # but keep the connection open for other purposes or to start another strategy.
        # Disconnection is handled by closing the window or the connect/disconnect logic.


if __name__ == "__main__":
    root = tk.Tk()
    tksupport.install(root)
    app = ScalperGUI(root)
    reactor.run()

