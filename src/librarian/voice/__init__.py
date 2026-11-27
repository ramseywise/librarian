"""The conversational voice process (Wave 6b, D9 and D10). Started only by `make voice`.

Pipecat and the speech models live behind the optional `voice` extra and are imported only by
`pipeline.py`, so everything else here can be imported and tested without them. The API never
imports this package: `app/backend/voice_broker.py` talks to this process over HTTP.
"""
