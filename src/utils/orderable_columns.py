from src.domain.entities.publishing_control import PublishingControl 
ORDERABLE_COLUMNS = {
    "Created": PublishingControl.created,
    "BusinessDate": PublishingControl.business_date,
    "ExpectedDate": PublishingControl.expected_date,
    "ReceivedDate": PublishingControl.received_date,
    "DocumentType": PublishingControl.file_type,
    "FileType": PublishingControl.file_type,
    "PubStatus": PublishingControl.pub_status,
}