## Installation

    pip3 install numpy scipy websockets
    git submodule init
    git submodule update

## Running

### General Case

    python3 beautify_server.py

Open `beautify_gui.html` in a web browser.

### Close curves

    python3 close_curve_server.py

or

    websocketd --address 127.0.0.1 --port 9000 python3 close_curve_server_websocketsd.py

Open `close_curve_gui.html` in a web browser.

### Fit lines

    julia fit_line_server.jl

Open `close_curve_gui.html` in a web browser.
