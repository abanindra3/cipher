# Database Schema

JARVIS uses SQLite so memories and conversations remain local.

## Tables

- `conversations`: one row per chat session.
- `messages`: user, assistant, system, and tool messages.
- `memories`: durable facts about the user, such as `location`, `exam_goal`, `career_goal`, and `job_search`.
- `tool_logs`: every tool call, argument payload, result, and status.
- `reminders`: scheduled reminders.
- `notification_settings`: configurable notification channels.
- `notifications`: notification center records.

See `jarvis/backend/db/schema.sql` for the executable schema.

