from datetime import datetime, timezone
from typing import List, Dict, Any
from pymongo import MongoClient


class TalkIdeasDB:
    """
    Database wrapper for the app.
    Each topic is its own MongoDB collection.
    Each collection contains a single document with a notes array.
    """

    def __init__(self, uri: str, db_name="talk_ideas_db"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    # -----------------------------
    # Utility
    # -----------------------------
    def now_utc(self):
        return datetime.now(timezone.utc)

    # -----------------------------
    # Topic (collection) management
    # -----------------------------
    def list_topics(self) -> List[str]:
        """Return all topic collection names."""
        return self.db.list_collection_names()

    def create_topic(self, topic_name: str):
        """Create a new topic collection with an initial document."""
        col = self.db[topic_name]
        col.insert_one({
            "notes": [],
            "created_at": self.now_utc(),
            "updated_at": self.now_utc()
        })
    
    def delete_topic(self, topic_name: str):
        """Drop the topic collection."""
        self.db.drop_collection(topic_name)

    # -----------------------------
    # Notes CRUD
    # -----------------------------
    def get_topic_doc(self, topic_name: str) -> Dict[str, Any] | None:
        return self.db[topic_name].find_one()

    def add_note(self, topic_name: str, note: str):
        col = self.db[topic_name]
        col.update_one(
            {},
            {"$push": {"notes": note}, "$set": {"updated_at": self.now_utc()}},
            upsert=True
        )

    def edit_note(self, topic_name: str, index: int, new_text: str):
        col = self.db[topic_name]
        col.update_one(
            {},
            {
                "$set": {
                    f"notes.{index}": new_text,
                    "updated_at": self.now_utc()
                }
            }
        )

    def delete_note(self, topic_name: str, index: int):
        col = self.db[topic_name]

        col.update_one(
            {},
            {
                "$unset": {f"notes.{index}": 1},
                "$set": {"updated_at": self.now_utc()}
            }
        )

        col.update_one(
            {},
            {"$pull": {"notes": None}}
        )

    # -----------------------------
    # Cleanup
    # -----------------------------
    def close(self):
        self.client.close()
