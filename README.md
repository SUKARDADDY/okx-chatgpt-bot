# ChatGPT o3 + OKX Trading Bot

## Overview

This command‑line application lets you generate and execute crypto trades on OKX using ChatGPT (model **o3**) for the strategy logic.
All orders are placed through the OKX REST v5 API; browser automation (Playwright) is used to talk to ChatGPT via the website—**no OpenAI API keys required**.

## Features

- Boots a headless Chromium session, logs in to chat.openai.com, and works inside a **“trading bot”** project (created automatically on first run).
- Interactive CLI built with Typer & prompt‑toolkit, including live **symbol autocompletion** from OKX.
- Lets the user specify **pair**, **desired risk‑to‑reward**, **order size**, and **leverage**; ChatGPT decides entry, stop‑loss, take‑profit, and direction.
- Ensures every setup meets or exceeds the requested R:R before submitting.
- Places market orders plus attached TP/SL on OKX, and stores a JSON log of each ChatGPT prompt/response and order status.
- Graceful error handling for browser restarts, network hiccups, and API errors.

## Quickstart

```bash
git clone https://github.com/yourname/okx-chatgpt-bot.git
cd okx-chatgpt-bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install
cp .env.example .env  # create your local env file
# edit .env with your OpenAI and OKX credentials
python cli.py trade
```
