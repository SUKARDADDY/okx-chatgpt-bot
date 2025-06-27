"""Thin wrapper around the OKX REST v5 API."""
import time, hmac, base64, hashlib, json, requests
from typing import Any, Dict, List, Optional

class OKXClient:
    def __init__(self, api_key: str, api_secret: str, passphrase: str, base_url: str = "https://www.okx.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.base_url = base_url.rstrip("/")

    # === Internal helpers === #
    def _timestamp(self) -> str:
        return str(time.time())

    def _sign(self, timestamp: str, method: str, request_path: str, body: str = "") -> str:
        msg = f"{timestamp}{method.upper()}{request_path}{body}"
        mac = hmac.new(self.api_secret.encode(), msg.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()

    def _headers(self, ts: str, sig: str) -> Dict[str, str]:
        return {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": sig,
            "OK-ACCESS-TIMESTAMP": ts,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, body: Optional[Dict[str, Any]] = None, private: bool = False):
        qs = "&".join(f"{k}={v}" for k, v in (params or {}).items())
        request_path = f"/api/v5{path}{'?' + qs if qs else ''}"
        url = self.base_url + request_path
        body_json = json.dumps(body) if body else ""
        headers = {}
        if private:
            ts = self._timestamp()
            sig = self._sign(ts, method, request_path, body_json)
            headers = self._headers(ts, sig)
        resp = requests.request(method, url, headers=headers, params=params, data=body_json, timeout=15)
        resp.raise_for_status()
        return resp.json()

    # === Public === #
    def get_symbols(self) -> List[str]:
        data = self._request("GET", "/public/instruments", params={"instType": "SPOT"})
        return [item["instId"] for item in data.get("data", [])]

    def set_leverage(self, inst_id: str, leverage: int, mgn_mode: str = "cross"):
        body = {"instId": inst_id, "lever": str(leverage), "mgnMode": mgn_mode}
        return self._request("POST", "/account/set-leverage", body=body, private=True)

    def place_order(self, inst_id: str, td_mode: str, side: str, ord_type: str, sz: str,
                    px: Optional[str] = None, tp_px: Optional[str] = None, sl_px: Optional[str] = None,
                    pos_side: Optional[str] = None, cl_ord_id: Optional[str] = None):
        body = {
            "instId": inst_id,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": sz
        }
        if px:
            body["px"] = px
        if tp_px:
            body["tpTriggerPx"] = tp_px
        if sl_px:
            body["slTriggerPx"] = sl_px
        if pos_side:
            body["posSide"] = pos_side
        if cl_ord_id:
            body["clOrdId"] = cl_ord_id
        return self._request("POST", "/trade/order", body=body, private=True)
