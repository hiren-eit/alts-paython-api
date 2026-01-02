from typing import Optional
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from src.domain.entities.file_activity import FileActivity
from uuid import UUID

class FileActivityLogQueryBuilder:
    def __init__(self, db: Session, file_uid: UUID):
        self.db = db
        self.file_uid = file_uid
        self.query = None

    def build_query(self):
        rn = func.row_number().over(
            partition_by=(
                FileActivity.fileuid,
                FileActivity.status,
                FileActivity.stage,
                FileActivity.fileprocessingstage,
                FileActivity.failurestage,
                FileActivity.statuscomment
            ),
            order_by=desc(FileActivity.created)
        ).label("rn")

        subquery = (
            self.db.query(
                FileActivity,
                rn
            )
            .filter(
                FileActivity.fileuid == self.file_uid,
                FileActivity.isactive.is_(True)
            )
            .subquery()
        )

        self.query = (
            self.db.query(subquery)
            .filter(subquery.c.rn == 1)
            .order_by(desc(subquery.c.created))
        )

    def get_results(self):
        return self.query.all()