"""极简 CONNECT 代理：把 github.com 的解析结果固定到可用 IP。

背景：本机 DNS 把 github.com 解析到 20.205.243.166（不可达），
而 140.82.112.3 可达。git 走 libcurl，不认 --resolve，故用一个本地代理做中转。

用法：
    python scripts/github_proxy.py --port 8899 [--ip 140.82.112.3]
    git -c http.proxy=http://127.0.0.1:8899 push
"""

from __future__ import annotations

import argparse
import selectors
import socket
import sys
import threading

FIXED = {"github.com": None, "api.github.com": None}
LOCK = threading.Lock()


def pipe(a: socket.socket, b: socket.socket) -> None:
    sel = selectors.DefaultSelector()
    sel.register(a, selectors.EVENT_READ, b)
    sel.register(b, selectors.EVENT_READ, a)
    try:
        while True:
            for key, _ in sel.select(timeout=60):
                data = key.fileobj.recv(65536)
                other = key.data
                if not data:
                    return
                other.sendall(data)
    except OSError:
        return
    finally:
        sel.close()
        for s in (a, b):
            try:
                s.close()
            except OSError:
                pass


def handle(conn: socket.socket, fixed_ip: str | None) -> None:
    try:
        conn.settimeout(30)
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = conn.recv(4096)
            if not chunk:
                return
            buf += chunk
        head = buf.split(b"\r\n\r\n", 1)[0].decode("latin-1")
        line = head.splitlines()[0]
        parts = line.split()
        if len(parts) < 2 or parts[0].upper() != "CONNECT":
            conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            return
        host, _, port = parts[1].partition(":")
        port = int(port or "443")
        target = fixed_ip if (fixed_ip and host in FIXED) else None
        with LOCK:
            up = socket.create_connection((target or host, port), timeout=20)
        conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        pipe(conn, up)
    except Exception as e:  # noqa: BLE001
        try:
            conn.sendall(f"HTTP/1.1 502 Bad Gateway ({e})\r\n\r\n".encode())
        except OSError:
            pass
    finally:
        try:
            conn.close()
        except OSError:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--ip", default="140.82.112.3")
    args = ap.parse_args()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", args.port))
    srv.listen(64)
    print(f"proxy listening 127.0.0.1:{args.port} → github.com 固定 {args.ip}", flush=True)
    try:
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=handle, args=(conn, args.ip), daemon=True).start()
    except KeyboardInterrupt:
        print("bye")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
