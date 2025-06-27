"""Orchestrates ChatGPT strategy generation and OKX execution."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from chatgpt._interface import ChatGPTInterface
from okx._client import OKXClient

class TradingBot:
    def __init__(self, chat: ChatGPTInterface, okx: OKXClient, log_file: str = "trades.json"):
        self.chat = chat
        self.okx = okx
        self.log_path = Path(log_file)
        if not self.log_path.exists():
            self.log_path.write_text("[]")

    # === Helpers === #
    def _append_log(self, record: Dict[str, Any]):
        data = json.loads(self.log_path.read_text())
        data.append(record)
        self.log_path.write_text(json.dumps(data, indent=2))

    def _calc_rr(self, side: str, entry: float, sl: float, tp: float) -> float:
        if side.lower() == "long":
            return (tp - entry) / (entry - sl)
        return (entry - tp) / (sl - entry)

    # === Public API === #
    def propose_trade(self, pair: str, desired_rr: float, amount: float, leverage: int) -> Dict[str, Any]:
        sys_prompt = (
            "You are a professional AI trader operating in live market conditions. "
            "Identify one high‑probability trade setup that meets AT LEAST a {rr}:1 risk‑to‑reward ratio. "
            "Return STRICT JSON (no markdown) with keys: side (long/short), entry, stop_loss, take_profit, justification.".format(rr=desired_rr)
        )
        user_prompt = (
            f"Pair: {pair}\nDesired RR: {desired_rr}\nAmount (quote): {amount}\nLeverage: {leverage}"
        )
        raw = self.chat.send_prompt(sys_prompt + "\n---\n" + user_prompt)
        try:
            proposal = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError("ChatGPT did not return valid JSON:\n" + raw)

        rr_actual = self._calc_rr(proposal["side"], float(proposal["entry"]), float(proposal["stop_loss"]), float(proposal["take_profit"]))
        if rr_actual < desired_rr:
            raise ValueError(f"Returned RR {rr_actual:.2f} is below desired {desired_rr}")
        proposal["rr"] = rr_actual
        return proposal

    def execute_trade(self, pair: str, proposal: Dict[str, Any], amount: float, leverage: int):
        # Futures leverage
        if leverage > 1:
            self.okx.set_leverage(pair, leverage)
        side = "buy" if proposal["side"].lower() == "long" else "sell"
        order_resp = self.okx.place_order(
            inst_id=pair,
            td_mode="cross" if leverage > 1 else "cash",
            side=side,
            ord_type="market",
            sz=str(amount),
            tp_px=str(proposal["take_profit"]),
            sl_px=str(proposal["stop_loss"])
        )
        self._append_log({
            "timestamp": datetime.utcnow().isoformat(),
            "pair": pair,
            "proposal": proposal,
            "order_response": order_resp
        })
        return order_resp