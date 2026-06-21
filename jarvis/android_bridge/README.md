# Android Bridge Contract

JARVIS already exposes local REST endpoints that a future Android app can call over the same network, VPN, or a secure tunnel.

Planned mobile capabilities map to backend endpoints:

| Mobile feature | Endpoint shape | Status |
| --- | --- | --- |
| Remote command | `POST /android/command` | Implemented |
| Send SMS | `POST /android/sms/send` | Reserved |
| Make call | `POST /android/calls/start` | Reserved |
| Read notifications | `POST /android/notifications/sync` | Reserved |
| WhatsApp message | `POST /android/whatsapp/send` | Reserved |

Android clients should authenticate before these endpoints are enabled on a non-local network. Keep the API bound to `127.0.0.1` until a proper auth layer and TLS tunnel are configured.

