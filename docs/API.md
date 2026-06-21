# API Documentation

Base URL: `http://127.0.0.1:8765`

## Health

`GET /health`

Returns app status.

## Chat

`POST /chat`

```json
{
  "message": "Open Chrome",
  "conversation_id": null
}
```

Returns the assistant response, conversation id, remembered facts, and tool results.

## Memory

- `GET /memory`
- `POST /memory`
- `DELETE /memory/{key}`

Example:

```json
{
  "key": "location",
  "value": "Kolkata",
  "source": "user",
  "confidence": 1.0
}
```

## Tools

- `GET /tools`
- `POST /tools/run`
- `GET /tools/logs`

Tool call:

```json
{
  "name": "google_search",
  "arguments": {
    "query": "UPSC current affairs"
  },
  "confirmed": false
}
```

## Daily Briefing

`GET /briefing/good-morning`

Returns date, time, weather, calendar placeholders, latest news, UPSC current affairs, and job updates.

## Notifications and Reminders

- `GET /notifications`
- `POST /notifications`
- `POST /reminders`

## Android Future Endpoint

`POST /android/command`

Accepts the same payload as `/chat`. Add authentication before exposing it outside localhost.

