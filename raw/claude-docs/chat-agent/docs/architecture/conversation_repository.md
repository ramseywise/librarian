# Conversation Database Schema

The conversation store uses two PostgreSQL tables:

## `conversations`

Stores one row per chat session.

- `id` `TEXT PRIMARY KEY`: conversation or session identifier.
- `title` `TEXT NOT NULL DEFAULT 'New conversation'`: display title.
- `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`: creation timestamp.
- `updated_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`: last activity timestamp.

## `messages`

Stores all user and assistant messages for a conversation.

- `id` `BIGSERIAL PRIMARY KEY`: message identifier.
- `conversation_id` `TEXT NOT NULL`: references `conversations(id)` with `ON DELETE CASCADE`.
- `role` `TEXT NOT NULL`: constrained to `user` or `assistant`.
- `content` `TEXT NOT NULL`: message text.
- `trace` `JSONB NOT NULL DEFAULT '[]'`: execution trace for assistant responses.
- `sources` `JSONB NOT NULL DEFAULT '[]'`: retrieved sources attached to a message.
- `confidence` `TEXT`: optional confidence label.
- `created_at` `TIMESTAMPTZ NOT NULL DEFAULT NOW()`: message timestamp.

## Relationships and indexing

- One conversation has many messages.
- Deleting a conversation removes its messages automatically.
- Index `messages_conv_idx` supports chronological reads by `conversation_id, created_at`.
