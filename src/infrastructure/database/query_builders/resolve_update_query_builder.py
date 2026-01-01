from sqlalchemy.orm import Session
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_activity import FileActivity

class ResolveUpdateQueryBuilder:
    def __init__(self, db: Session):
        self.db = db

    def get_file_by_file_uid(self, file_uid):
        return (
            self.db.query(FileManager)
            .filter(
                FileManager.fileuid == file_uid,
                FileManager.isactive.is_(True)
            )
            .first()
        )
    
    def update_file(self, file: FileManager):
        self.db.add(file)

    def add_file_activities(self, *activities: FileActivity):
        self.db.add_all(activities)

    def move_file_to_ignore(self, file: FileManager, status_comment: str, reason: str):
        file.statuscomment = status_comment
        file.reason = reason
        file.status = "Ignored"
        file.stage = "Ignored"
        self.db.add(file)