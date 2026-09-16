"""Print the PC's LAN IPv4 for the mobile-preview launcher."""
from __future__ import annotations

import ipaddress
import socket


def detect_lan_ipv4() -> str:
    candidates: list[str] = []
    route = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        route.connect(("8.8.8.8", 80))
        candidates.append(route.getsockname()[0])
    except OSError:
        pass
    finally:
        route.close()
    try:
        candidates.extend(info[4][0] for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET))
    except OSError:
        pass
    for value in candidates:
        address = ipaddress.ip_address(value)
        if address.version == 4 and not address.is_loopback and not address.is_link_local:
            return value
    raise RuntimeError("LAN_IPV4_NOT_FOUND")


def main() -> int:
    print(detect_lan_ipv4())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
