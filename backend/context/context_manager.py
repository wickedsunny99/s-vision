import base64
import json
import time

import redis


class ContextManager:
    def __init__(self):
        self.redis = redis.Redis(host="localhost", port=6379, db=0)

    def _key(self, user_id):
        return f"user:{user_id}"

    def _load(self, user_id):
        raw = self.redis.get(self._key(user_id))
        return json.loads(raw) if raw else {}

    def _save(self, user_id, context):
        self.redis.set(self._key(user_id), json.dumps(context))

    def initialize_user(self, user_id):
        """Create an empty context entry when a user connects."""
        self._save(
            user_id,
            {
                "last_frame": None,
                "last_text": "",
                "last_command": None,
                "timestamp": time.time(),
            },
        )

    def update_context(self, user_id, frame_data, text):
        context = self._load(user_id)
        # frame_data is raw JPEG bytes, which json.dumps cannot serialize;
        # base64-encode it so the context stays JSON-safe.
        context.update(
            {
                "last_frame": (
                    base64.b64encode(frame_data).decode("ascii")
                    if frame_data is not None
                    else None
                ),
                "last_text": text,
                "timestamp": time.time(),
            }
        )
        self._save(user_id, context)

    def update_from_voice(self, user_id, command):
        """Record the most recent voice command in the user's context."""
        context = self._load(user_id)
        context["last_command"] = command
        context["timestamp"] = time.time()
        self._save(user_id, context)

    def get_changes(self, user_id, new_text):
        context = self._load(user_id)
        old_text = context.get("last_text", "")
        return self._text_diff(old_text, new_text)

    def _text_diff(self, old, new):
        # Simple text comparison - consider using difflib
        return list(set(new.split()) - set(old.split()))
