From https://developer.oculus.com/documentation/oculus-browser/browser-remote-debugging/ and https://developers.google.com/web/tools/chrome-devtools/remote-debugging/local-server

1. Turn on Developer mode. Get Android Platform Tools. See the above URLs for that.
2. Plug your Quest into your computer and authorize it. If you want to debug wirelessly, run the following two extra steps while the cable is attached:
  1. `adb tcpip 5555`
  2. Get the IP address `x.y.z.w` of your Oculus (e.g. `10.0.0.149`).
  3. `adb connect 10.0.0.149:5555`
3. Open Chrome DevTools and click the three vertical dots and choose "More tools > Remote devices".
4. Under Devices > Settings, set up port forwarding from port 8000 to localhost:8000.
5. Run a webserver on your local machine, e.g. `python3 -m http.server` in the directory you want to serve.
6. Under Devices > Quest, click "Inspect" for the browser tab you want to debug.

---

To test websocket round trip with `paint.html`, also forward port 9000 and run `python3 ping.py`.
