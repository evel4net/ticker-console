# Ticker Console 📟

This project aims to build a small wireless productivity device to display the clock, calendar, 
weather and daily tasks, in a retro style similar to Ticker Tape displays. 

Device uses a **Raspberry Pi Pico** with a custom **MicroPython** firmware: control the hardware,
save and handle data, and expose a lightweight HTTP server for future integration with a phone 
or web application, allowing data synchronization and management.

The firmware is currently in development and is close to being finalized.

## Project Structure
```
ticker-console/
├── docs/            # Documentation & Learning notes
├── firmware/        # Raspberry Pi Pico code
│   ├── dependencies/
│   ├── fonts/
│   ├── icons-png/
│   ├── icons/
│   ├── src/
│   ├── main.py
│   ├── requirements-dev.txt
│   └── README.md
│
├── app/             # Mobile app code
│   ├── android/
│   ├── ios/
│   └── README.md
└── README.md        # Main project overview
```
