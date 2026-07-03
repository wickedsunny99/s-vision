import json
import time

import redis


class ContextManager:
    def __init__(self):
        self.redis = redis.Redis(host="localhost", port=6379, db=0)

    def update_context(self, user_id, frame_data, text):
        context = {
            "last_frame": frame_data,
            "last_text": text,
            "timestamp": time.time(),
        }
        self.redis.set(f"user:{user_id}", json.dumps(context))

    def get_changes(self, user_id, new_text):
        context = json.loads(self.redis.get(f"user:{user_id}") or "{}")
        old_text = context.get("last_text", "")
        return self._text_diff(old_text, new_text)

    def _text_diff(self, old, new):
        # Simple text comparison - consider using difflib
        return list(set(new.split()) - set(old.split()))
