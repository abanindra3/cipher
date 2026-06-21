from jarvis.backend.ai.memory_extractor import MemoryExtractor
from jarvis.backend.db.database import Database
from jarvis.backend.db.repositories import MemoryRepository


def test_memory_extractor_stores_user_facts(tmp_path):
    database = Database(tmp_path / "test.db")
    repo = MemoryRepository(database)
    extractor = MemoryExtractor(repo)

    stored = extractor.extract("I am based in Kolkata and I am preparing for UPSC 2027.")

    memories = {item["key"]: item["value"] for item in repo.all()}
    assert memories["location"] == "Kolkata"
    assert memories["exam_goal"] == "UPSC 2027"
