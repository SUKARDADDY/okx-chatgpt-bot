"""CLI entry‑point using Typer + prompt‑toolkit."""
import os, json, typer
from prompt_toolkit.completion import WordCompleter
from dotenv import load_dotenv

from chatgpt._interface import ChatGPTInterface
from okx._client import OKXClient
from bot import TradingBot

app = typer.Typer(help="ChatGPT‑driven OKX trading bot")

REQUIRED_VARS = [
    "OPENAI_API_KEY",
    "OKX_API_KEY",
    "OKX_API_SECRET",
    "OKX_API_PASSPHRASE",
]

def _check_env():
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        typer.echo(f"Missing env vars: {', '.join(missing)}")
        raise typer.Exit(code=1)

@app.command()
def trade():
    """Interactive trade flow."""
    load_dotenv()
    _check_env()

    okx = OKXClient(os.getenv("OKX_API_KEY"), os.getenv("OKX_API_SECRET"), os.getenv("OKX_API_PASSPHRASE"))
    symbols = okx.get_symbols()
    completer = WordCompleter(symbols, ignore_case=True)

    pair = typer.prompt("Coin pair", completer=completer)
    rr = float(typer.prompt("Desired risk:reward", default="3"))
    amount = float(typer.prompt("Order size (quote currency)"))
    leverage = int(typer.prompt("Leverage", default="1"))

    with ChatGPTInterface() as chat:   # API key is picked up from env
        bot = TradingBot(chat, okx)
        typer.echo("Generating strategy via ChatGPT…")
        proposal = bot.propose_trade(pair, rr, amount, leverage)
        typer.echo(json.dumps(proposal, indent=2))
        if typer.confirm("Place this order?"):
            resp = bot.execute_trade(pair, proposal, amount, leverage)
            typer.echo("Order response:\n" + json.dumps(resp, indent=2))
        else:
            typer.echo("Aborted.")

if __name__ == "__main__":
    app()
