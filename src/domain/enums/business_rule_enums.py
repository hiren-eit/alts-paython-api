from enum import Enum

class BusinessRuleTypes(str, Enum):
    Ignore = "Ignore"
    Classification = "Classification"
    Password = "Password"
    ETL = "ETL"

class ChangeType(str, Enum):
    Added = "Added"
    Updated = "Updated"

class DocumentProcessStage(str, Enum):
    DocReady = "DocReady"
    Classified = "Classified"
    Ignored = "Ignored"
    ExtractReady = "ExtractReady"
    NotMacthRule = "NotMacthRule" # Matches C# typo/naming

class DocumentProcessingState(str, Enum):
    RuleProcessor = "RuleProcessor"

class DocumentProcessStatus(str, Enum):
    Ignored = "Ignored"
    # Add other statuses as needed based on codebase usage
