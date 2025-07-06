# Tkinter GUI Sample

This sample demonstrates a minimal Tkinter GUI that connects to the OpenApiPy `Client`.

The application shows two tabs:

* **Trading** - Start/stop a sample scalping loop, view trade history and account metrics.
* **Settings** - Enter API credentials used for authentication. Specify your account ID and choose Live or Demo host.

Run the example with `python main.py`.

Fill in your application credentials, access token, and cTrader account ID on the
**Settings** tab. Select whether to connect to the Demo or Live host and click
**Connect** to authorize the account. Successful authorization messages appear in
the activity log.

The **Trading** tab lets you choose a forex pair and one of five built-in
strategies: `safe`, `moderate`, `aggressive`, `trends`, and `scalping`. After
connecting, click **Scalp** to start the selected strategy. The strategy logic
places sample market orders using the Open API. Click **End Trading** to stop
the strategy and disconnect.
