import uuid
from sqlalchemy import TIMESTAMP, BigInteger, Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID

from .base_entity import BaseEntity


# class FileManager(BaseEntity):
#     __tablename__ = "file"

#     doc_uid = Column(UUID(as_uuid=True), nullable=False)
#     counter = Column(Integer)
#     type = Column(String)
#     filename = Column(String)
#     firm = Column(Integer)

#     entity_uid = Column(UUID(as_uuid=True))
#     account_sid = Column(String)
#     account_uid = Column(UUID(as_uuid=True))
#     position_uid = Column(UUID(as_uuid=True))

#     report_date = Column(String)
#     create_date = Column(DateTime)
#     create_time = Column(DateTime)

#     module = Column(String)
#     work_sid = Column(String)
#     work_uid = Column(UUID(as_uuid=True))

#     comments = Column(String)
#     tag = Column(String)
#     create_by = Column(String)

#     client_entity_uid = Column(UUID(as_uuid=True))
#     filename_alt = Column(String)
#     external_id = Column(String)
#     batch_id = Column(String)
#     pub_uid = Column(UUID(as_uuid=True))

#     metadata_json = Column(String)
#     checksum = Column(String)
#     status = Column(String)
#     status_date = Column(DateTime)

#     method = Column(String)
#     doc_sid = Column(String)
#     link_uid = Column(UUID(as_uuid=True))

#     available_date = Column(DateTime)
#     notice_date = Column(DateTime)

#     reason_id = Column(String)
#     reason = Column(String)

#     harvest_system = Column(String)
#     harvest_method = Column(String)
#     harvest_source = Column(String)

#     index_system = Column(String)
#     index_method = Column(String)

#     extract_system = Column(String)
#     extract_method = Column(String)

#     age = Column(Integer)

#     email_sender = Column(String)
#     email_subject = Column(String)

#     category = Column(String)
#     failure_stage = Column(String)

#     document_type_procees_rule = Column(String)
#     document_type_gen_ai = Column(String)

#     ignored_on = Column(DateTime)
#     ignored_by = Column(String)

#     rule = Column(String)

#     business_date = Column(DateTime)

#     firm_name = Column(String)
#     entity_name = Column(String)
#     account_name = Column(String)

#     capture_method = Column(String)
#     capture_system = Column(String)

#     linking_method = Column(String)
#     linking_system = Column(String)

#     source_attributes = Column(String)
#     investor = Column(String)

#     stage = Column(String(100))
#     file_path = Column(String(450))

#     duplicate_document_id = Column(UUID(as_uuid=True))
#     update_document_id = Column(UUID(as_uuid=True))

#     status_comment = Column(String)
#     document_process_stage = Column(String)

#     business_rule_applied_date = Column(DateTime)

#     file_extension = Column(String(255))
#     password = Column(String)

#     group_code = Column(String)

#     last_attempted_time = Column(DateTime)
#     retry_count = Column(Integer)

#     replay = Column(Boolean)
#     ingestion_failed_image_url = Column(String(250))

class FileManager(BaseEntity):
    __tablename__ = 'tbl_file_manager'
    __table_args__ = {'schema': 'frame'}

    fileid = Column(BigInteger, primary_key=True, autoincrement=True)
    fileuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    type = Column(String(450))
    filename = Column(String(450))
    firm = Column(Integer)
    entityuid = Column(UUID(as_uuid=True))
    accountsid = Column(String(450))
    accountuid = Column(UUID(as_uuid=True))
    filepath = Column(String(450))
    createdate = Column(TIMESTAMP(7))
    createtime = Column(TIMESTAMP(7))
    comments = Column(Text)
    createby = Column(Integer)
    filenameframe = Column(String(450))
    batchid = Column(String(450))
    file_metadata = Column("metadata", Text)
    checksum = Column(String(450))
    status = Column(String(100))
    statusdate = Column(TIMESTAMP(7))
    method = Column(String(450))
    reasonid = Column(String(450))
    reason = Column(Text)
    harvestsystem = Column(String(450))
    harvestmethod = Column(String(450))
    harvestsource = Column(String(450))
    indexsystem = Column(String(450))
    indexmethod = Column(String(450))
    extractsystem = Column(String(450))
    extractmethod = Column(String(450))
    age = Column(Integer)
    emailsender = Column(String(450))
    emailsubject = Column(String(450))
    category = Column(String(450))
    failurestage = Column(String(450))
    filetypeproceesrule = Column(String(450))
    filetypegenai = Column(String(450))
    ignoredon = Column(TIMESTAMP(7))
    ignoredby = Column(Integer)
    rule = Column(String(450))
    businessdate = Column(TIMESTAMP(7))
    firmname = Column(String(450))
    entityname = Column(String(450))
    capturemethod = Column(String(450))
    # capturesystem = Column(String(450)) # Not in User SQL for FileManager, but was in previous entity. I will remove it per User SQL.
    linkingmethod = Column(String(450))
    # linkingsystem = Column(String(450)) # Not in User SQL for FileManager
    stage = Column(String(100))
    # isactive, created, createdby, updated, updatedby are inherited from BaseEntity
    updatefileid = Column(UUID(as_uuid=True))
    statuscomment = Column(Text)
    duplicatefileid = Column(UUID(as_uuid=True))
    fileprocessstage = Column(Text)
    businessruleapplieddate = Column(TIMESTAMP(7))
    fileextension = Column(String(255))
    password = Column(Text)
    groupcode = Column(Text)
    replay = Column(Boolean, default=False)
    lastattemptedtime = Column(TIMESTAMP)
    retrycount = Column(Integer)
    ingestionfailedimageurl = Column(String(250))
