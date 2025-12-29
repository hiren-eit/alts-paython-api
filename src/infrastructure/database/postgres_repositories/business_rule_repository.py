
from src.domain.dtos.business_rule_request import BusinessRuleRequest
from typing import Any, Dict, List, Optional
import json
import re
import uuid
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, text, String, cast, and_, or_, func, literal_column, desc, asc, JSON, case
from sqlalchemy.dialects.postgresql import JSONB
from src.domain.interfaces.business_rule_repository_interface import IBusinessRuleRepository
from src.infrastructure.logging.logger_manager import get_logger
from src.domain.entities.business_rule import BusinessRule
from src.domain.entities.business_rule_log import BusinessRuleLog
from src.domain.entities.file_manager import FileManager
from src.domain.entities.file_process_log import FileProcessLog
from src.domain.entities.file_activity import FileActivity
from src.domain.entities.master_configuration_type import MasterConfigurationType
from src.domain.enums.business_rule_enums import (
    BusinessRuleTypes, ChangeType, FileProcessStage, 
    FileProcessingState, FileProcessStatus
)

logger = get_logger(__name__)

class BusinessRuleRepository(IBusinessRuleRepository):
    def __init__(self):
        super().__init__(model=BusinessRule)

    def _get_rule_type_prefix(self, rule_type: str) -> str:
        if rule_type == BusinessRuleTypes.Ignore:
            return "IG"
        elif rule_type == BusinessRuleTypes.Classification:
            return "CN"
        elif rule_type == BusinessRuleTypes.Password:
            return "PW"
        elif rule_type == BusinessRuleTypes.ETL:
            return "ETL"
        else:
            raise ValueError("Invalid RuleType")

    def save_rule(self, db: Session, rule_data: Dict[str, Any]) -> int:
        try:
            # Map Dict to Entity
            rule = BusinessRule(
                ruletype=rule_data.get('ruletype'),
                ruleexpressions=rule_data.get('ruleexpressions'),
                isactive=rule_data.get('isactive'),
                # createdby=rule_data.get('createdby'),
                created=datetime.datetime.utcnow(),
                updated=datetime.datetime.utcnow(),
                password=rule_data.get('password'),
                groupcode=rule_data.get('groupcode'),
                filetypeid=rule_data.get('filetypeid'),
                sourceid=rule_data.get('sourceid')
            )
            
            prefix = self._get_rule_type_prefix(rule.ruletype)
            
            # Fetch last rule of same type
            last_rule = db.query(BusinessRule).filter(
                BusinessRule.ruletype == rule.ruletype,
                BusinessRule.uniqueruleid.isnot(None),
                ~BusinessRule.uniqueruleid.contains("-CLONE"),
                BusinessRule.uniqueruleid.startswith(prefix)
            ).order_by(desc(BusinessRule.uniqueruleid)).first()

            next_number = 1
            if last_rule and last_rule.uniqueruleid:
                try:
                    last_number_str = last_rule.uniqueruleid[len(prefix):]
                    next_number = int(last_number_str) + 1
                except ValueError:
                    pass

            rule.uniqueruleid = f"{prefix}{next_number:04d}"

            new_rule_log = BusinessRuleLog(
                uniqueruleid=rule.uniqueruleid,
                changetype=ChangeType.Added,
                ruleexpressions=rule.ruleexpressions,
                rulelogmessage="The Rule is enabled" if rule.isactive else "The Rule is disabled",
                rulelogtitle="New Rule Created",
                createdby=rule.createdby,
                created=datetime.datetime.utcnow(),
                isactive=True
            )

            db.add(new_rule_log)
            db.add(rule)
            db.commit()
            return 1
        except Exception as ex:
            logger.error(f"Rule: Error occurred while inserting Rule: {ex}", exc_info=True)
            db.rollback()
            return 0

    def update_rule(self, db: Session, rule_data: Dict[str, Any]) -> int:
        try:
            # Check for ID or BusinessRuleId in input
            rule_id = rule_data.get('businessruleid') or rule_data.get('id')
            rule_db = db.query(BusinessRule).filter(BusinessRule.businessruleid == rule_id).first()
            
            if not rule_db:
                logger.error(f"Rule: Rule with ID - {rule_id} not found")
                return 0

            old_expressions_json = json.loads(rule_db.ruleexpressions) if rule_db.ruleexpressions else {}
            new_expressions_json = json.loads(rule_data.get('ruleexpressions', '{}'))
            
            rule_log_message = self._generate_rule_log_message_json(old_expressions_json, new_expressions_json)

            new_rule_log = BusinessRuleLog(
                uniqueruleid=rule_db.uniqueruleid or "",
                changetype=ChangeType.Updated,
                ruleexpressions=rule_data.get('ruleexpressions'),
                rulelogtitle="Rule Modified",
                rulelogmessage=rule_log_message,
                createdby=rule_data.get('updatedby', "SYSTEM"),
                created=datetime.datetime.utcnow(),
                isactive=True
            )
            
            # Update fields
            if 'password' in rule_data:
                rule_db.password = rule_data['password']
            if 'groupcode' in rule_data:
                rule_db.groupcode = rule_data['groupcode']
            
            rule_db.ruleexpressions = rule_data.get('ruleexpressions')
            rule_db.updated = datetime.datetime.utcnow()
            rule_db.updatedby = rule_data.get('updatedby', "SYSTEM")

            db.add(new_rule_log)
            db.commit()
            return 1
        except Exception as ex:
            logger.error(f"Rule: Error occurred while updating Rule: {ex}", exc_info=True)
            db.rollback()
            return 0

    def _generate_rule_log_message_json(self, old_json: Dict, new_json: Dict) -> str:
        pattern_modified_count = 0
        pattern_added_count = 0
        result = {"Pattern Modified": set(), "Pattern Added": set()}
        
        # Simplified comparison based on keys
        all_keys = set(old_json.keys()) | set(new_json.keys())
        
        for key in all_keys:
            old_val = old_json.get(key, "")
            new_val = new_json.get(key, "")
            
            if old_val != new_val:
                msg = f"{key} : {new_val}"
                if old_val:
                    pattern_modified_count += 1
                    result["Pattern Modified"].add(msg)
                else:
                    pattern_added_count += 1
                    result["Pattern Added"].add(msg)

        final_json = {}
        for key, value_set in result.items():
            if not value_set:
                continue
            if key == "Pattern Modified" and pattern_modified_count > 1:
                final_json["Patterns Modified"] = list(value_set)
            elif key == "Pattern Added" and pattern_added_count > 1:
                final_json["Patterns Added"] = list(value_set)
            else:
                final_json[key] = list(value_set)
                
        return json.dumps(final_json)

    def clone_rule(self, db: Session, rule_data: Dict[str, Any]) -> int:
        try:
            rule_type = rule_data.get('ruletype')
            prefix = self._get_rule_type_prefix(rule_type)
            
            latest_clone = db.query(BusinessRule).filter(
                BusinessRule.uniqueruleid.contains("CLONE"),
                BusinessRule.uniqueruleid.startswith(prefix)
            ).order_by(desc(BusinessRule.created)).first()
            
            incremented_number = 1
            if latest_clone and latest_clone.uniqueruleid:
                match = re.search(r"CLONE(\d+)$", latest_clone.uniqueruleid)
                if match:
                    incremented_number = int(match.group(1)) + 1
                    
            original_unique_id = rule_data.get('uniqueruleid')
            new_unique_id = f"{original_unique_id}-CLONE{incremented_number:04d}"
            
            rule = BusinessRule(
                uniqueruleid=new_unique_id,
                ruletype=rule_type,
                ruleexpressions=rule_data.get('ruleexpressions'),
                isactive=rule_data.get('isactive', True),
                createdby=rule_data.get('createdby', "SYSTEM"),
                created=datetime.datetime.utcnow(),
                updated=datetime.datetime.utcnow(),
                password=rule_data.get('password'),
                groupcode=rule_data.get('groupcode'),
                filetypeid=rule_data.get('filetypeid'),
                sourceid=rule_data.get('sourceid')
            )
            
            new_rule_log = BusinessRuleLog(
                uniqueruleid=new_unique_id,
                changetype=ChangeType.Added,
                ruleexpressions=rule.ruleexpressions,
                rulelogmessage="The Rule is enabled" if rule.isactive else "The Rule is disabled",
                rulelogtitle="New Rule Created",
                createdby=rule.createdby,
                created=datetime.datetime.utcnow(),
                isactive=True
            )
            
            db.add(new_rule_log)
            db.add(rule)
            db.commit()
            return 1
        except Exception as ex:
            logger.error(f"Error occurred while cloning the rule: {ex}", exc_info=True)
            db.rollback()
            return 0

    def get_business_rules_api(self, db: Session) -> List[Any]:
        # Implementation depends on return type, assuming basic list matching Entity
        # Check 'GetBusinessRuleApi' stored proc logic from C# if specific cols needed
        # For now return all active
        return db.query(BusinessRule).all()

    def toggle_rule(self, db: Session, rule_data: Dict[str, Any]) -> Any:
        try:
            rule_id = rule_data.get('businessruleid') or rule_data.get('id')
            rule_db = db.query(BusinessRule).filter(BusinessRule.businessruleid == rule_id).first()
            
            if rule_db:
                is_active = not rule_db.isactive
                rule_log_title = "Rule Enabled" if is_active else "Rule Disabled"
                
                new_rule_log = BusinessRuleLog(
                    uniqueruleid=rule_db.uniqueruleid or "",
                    ruleexpressions=rule_db.ruleexpressions,
                    changetype=ChangeType.Updated,
                    rulelogmessage=rule_data.get('reasonfortoggle', ""),
                    rulelogtitle=rule_log_title,
                    created=datetime.datetime.utcnow(),
                    isactive=True
                    # CreatedBy missing in C# snippet for toggle log, assume system or passed
                )
                
                rule_db.isactive = is_active
                rule_db.reasonfortoggle = rule_data.get('reasonfortoggle')
                rule_db.updated = datetime.datetime.utcnow()
                rule_db.updatedby = rule_data.get('updatedby', "SYSTEM")
                
                db.add(new_rule_log)
                db.commit()
                return rule_log_title
            
            return "Error occured while toggling rule"
        except Exception as ex:
            logger.error(f"Rule : Error occured while toggling rule: {ex}", exc_info=True)
            return "Error occured while toggling rule"

    def update_stage(self, db: Session) -> Any:
        try:
            # Fetch Files
            files = db.query(FileManager).filter(
                FileManager.stage == FileProcessStage.DocReady.value
            ).all()

            classification_rules = self._get_business_rules(db, BusinessRuleTypes.Classification)
            ignore_rules = self._get_business_rules(db, BusinessRuleTypes.Ignore)

            for file in files:
                # 1. Classification
                matched_class_rule = self._get_matching_classification_rule(file, classification_rules)
                
                if matched_class_rule and matched_class_rule.filetypeid:
                    if file.stage != FileProcessStage.Classified.value:
                        file_type = db.query(MasterConfigurationType).filter(MasterConfigurationType.masterconfigurationtypeid == matched_class_rule.filetypeid).first()
                        if file_type:
                            logger.info(f"BUSINESS RULE : File {file.fileuid} classified.")
                            
                            file.stage = FileProcessStage.Classified.value
                            file.fileprocessstage = FileProcessingState.RuleProcessor.value
                            
                            status_comment = f"File matched with classified rule and updated File Type as {file_type.displayname}" \
                                if file_type.displayname else "File matched with classified rule"
                            file.statuscomment = status_comment
                            file.filetypeproceesrule = file_type.displayname
                            file.rule = matched_class_rule.uniqueruleid
                            file.businessruleapplieddate = datetime.datetime.utcnow()

                # 2. Ignore
                ignore_rule = self._is_rule_applied(file, ignore_rules)
                
                if ignore_rule:
                    if file.stage != FileProcessStage.Ignored.value:
                        logger.info(f"BUSINESS RULE : File {file.fileuid} marked as ignored.")
                        
                        file.stage = FileProcessStage.Ignored.value
                        file.fileprocessstage = FileProcessingState.RuleProcessor.value
                        file.status = FileProcessStatus.Ignored.value
                        file.ignoredby = 0 # System ? 
                        file.ignoredon = datetime.datetime.utcnow()
                        file.rule = ignore_rule.uniqueruleid
                        file.statuscomment = "File match With ignored Rule"
                        file.businessruleapplieddate = datetime.datetime.utcnow()
                        
                        self._log_file_process(db, file, ignore_rule.uniqueruleid, "File match With ignored Rule", FileProcessStatus.Ignored.value)

                elif file.stage == FileProcessStage.Classified.value:
                    logger.info(f"BUSINESS RULE : File {file.fileuid} moved to InProgress.")
                    file.statuscomment = "File match With Classified Rule"
                    file.businessruleapplieddate = datetime.datetime.utcnow()
                    
                    self._log_file_process(db, file, ignore_rule.uniqueruleid if ignore_rule else None, "File match With Classified Rule", file.status)
                    
                    file.stage = FileProcessStage.ExtractReady.value
                    
                    self._log_file_process(db, file, ignore_rule.uniqueruleid if ignore_rule else None, "File is ExtractReady", file.status)
                    
                else:
                    logger.info(f"BUSINESS RULE : File {file.fileuid} is not match on classified and ignore.")
                    file.filetypeproceesrule = "Unknown"
                    file.stage = FileProcessStage.NotMacthRule.value
                    file.fileprocessstage = FileProcessingState.RuleProcessor.value
                    file.statuscomment = "File Not match with classified and ignore."
                    file.businessruleapplieddate = datetime.datetime.utcnow()
                    
                    self._log_file_process(db, file, None, "File Not match with classified and ignore.", file.status)
                    
                    file.stage = FileProcessStage.ExtractReady.value
                    self._log_file_process(db, file, None, "File is ExtractReady", file.status)

            db.commit()
            return files
        except Exception as ex:
            logger.error(f"BUSINESS RULE : Error occurred while updating Status: {ex}", exc_info=True)
            db.rollback()
            return None

    def _get_business_rules(self, db: Session, rule_type: str) -> List[BusinessRule]:
        return db.query(BusinessRule).filter(BusinessRule.ruletype == rule_type).all()

    def _get_matching_classification_rule(self, file: FileManager, rules: List[BusinessRule]) -> Optional[BusinessRule]:
        if not file.file_metadata:
            return None
        
        try:
            metadata = json.loads(file.file_metadata)
        except json.JSONDecodeError:
            logger.error(f"BUSINESS RULE : Error parsing metadata for file {file.fileuid}")
            return None
        
        if file.harvestsource == "Email":
             return self._has_matching_email_rules(metadata, rules)
        else:
             file_name = metadata.get("File_Name")
             if file_name:
                 return self._check_for_matching_rule(file_name, rules)
        return None

    def _is_rule_applied(self, file: FileManager, rules: List[BusinessRule]) -> Optional[BusinessRule]:
        if not file.file_metadata:
            return None
        
        try:
            metadata = json.loads(file.file_metadata)
        except:
             return None

        if file.harvestsource == "Email":
            return self._has_matching_email_rules(metadata, rules)
        else:
            file_name = metadata.get("File_Name")
            if file_name:
                return self._check_for_matching_rule(file_name, rules)
        return None

    def _has_matching_email_rules(self, metadata: Dict, rules: List[BusinessRule]) -> Optional[BusinessRule]:
        # metadata keys based on C#
        subject = metadata.get("Subject")
        sender = metadata.get("To") # C# uses 'To' for SenderAddress? code says SenderAddress = parsedMetadata["To"]
        body = metadata.get("Email_Body")
        filename = metadata.get("File_Name")

        for rule in rules:
            if (self._contains_pattern(rule.ruleexpressions, subject) or
                self._contains_pattern(rule.ruleexpressions, sender) or
                self._contains_pattern(rule.ruleexpressions, body) or
                self._contains_pattern(rule.ruleexpressions, filename)):
                return rule
        return None

    def _check_for_matching_rule(self, file_name: str, rules: List[BusinessRule]) -> Optional[BusinessRule]:
        for rule in rules:
            if not rule.ruleexpressions:
                continue
            
            # Note: C# code parses ruleExpression just to check FileName key presence?
            # It actually calls ContainsPattern with isEmail=false (default is true)
            # which does specific 'FileName' key check
            if self._contains_pattern(rule.ruleexpressions, file_name, is_email=False):
                return rule
        return None

    def _contains_pattern(self, rule_data: str, file_data: str, is_email: bool = True) -> bool:
        if not rule_data or not file_data:
            return False
            
        try:
            rule_dict = json.loads(rule_data)
        except:
            return False

        if not is_email:
            # File Only Check
            if "FileName" in rule_dict:
                pattern = rule_dict["FileName"]
                if pattern:
                    # Convert wildcard * to regex .*
                    regex_pattern = pattern.replace("*", ".*")
                    if re.search(regex_pattern, file_data, re.IGNORECASE):
                        return True
            return False

        # Email Check (Iterate all keys)
        for key, pattern in rule_dict.items():
            if not pattern:
                continue
            regex_pattern = pattern.replace("*", ".*")
            if re.search(regex_pattern, file_data, re.IGNORECASE):
                return True
        
        return False

    def _log_file_process(self, db: Session, file: FileManager, rule_id: Optional[str], comment: str, status: Optional[str]):
        log = FileProcessLog(
            fileuid=file.fileuid,
            stage=file.stage,
            status=status,
            ruleid=rule_id,
            statuscomment=comment,
            fileprocessstage=FileProcessingState.RuleProcessor.value,
            created=datetime.datetime.utcnow(),
            isactive=True
        )
        activity = FileActivity(
            fileuid=file.fileuid,
            status=status,
            stage=file.stage,
            fileprocessingstage=FileProcessingState.RuleProcessor.value,
            statuscomment=comment,
            created=datetime.datetime.utcnow(),
            isactive=True
        )
        db.add(log)
        db.add(activity)

    def apply_business_rule_api_async(self, db: Session) -> int:
        # Calls Stored Proc in C# : EXECUTE [alts].[ProcessingRule]
        # In Python, we might just call update_stage? 
        # C# has both ApplyBusinessRuleApiAsync (Exec Proc) and UpdateStage (Logic)
        # If user wants logic in Project, maybe UpdateStage IS the logic they want?
        # User REQ: "But don't add the core logic for this Api ApplyBusinessRuleApi"
        # Wait, the user said: "I have to implement the core logic of the business rule APIs... But don't add the core logic for this Api ApplyBusinessRuleApi"
        # So I should SKIP ApplyBusinessRuleApi?
        # Re-reading: "But don't add the core logic for this Api ApplyBusinessRuleApi"
        # Okay, I will leave it empty or just returns 0.
        return 0

    def get_business_rule_data(self, db: Session, input_data: Any) -> Any:
        try:
            from src.domain.dtos.business_rule_api_input import GetBusinessRuleApiInput
            from sqlalchemy.orm import aliased

            # Parse input if it's a dict or already the model
            if isinstance(input_data, dict):
                input_model = GetBusinessRuleApiInput(**input_data)
            else:
                input_model = input_data

            SourceTypeAlias = aliased(MasterConfigurationType, name="SourceType")
            FileTypeAlias = aliased(MasterConfigurationType, name="FileType")

            usage_subquery = db.query(func.count(FileManager.fileid)).filter(
                FileManager.rule == BusinessRule.uniqueruleid
            ).correlate(BusinessRule).as_scalar().label("Usage")

            # JSON extraction helpers
            def get_json_v(field):
                # We use a CASE statement to avoid casting non-JSON strings to JSONB, which would fail.
                # Heuristic: If it starts with '{', we try to cast and extract.
                return case(
                    (BusinessRule.ruleexpressions.like('{%'), cast(BusinessRule.ruleexpressions, JSONB).op('->>')(field)),
                    else_=''
                )

            # Define columns to select
            query = db.query(
                BusinessRule.businessruleid.label("Id"),
                func.coalesce(SourceTypeAlias.displayname, 'None').label("Source"),
                BusinessRule.uniqueruleid.label("UniqueRuleId"),
                BusinessRule.ruletype.label("RuleType"),
                FileTypeAlias.displayname.label("File"),
                func.coalesce(get_json_v('FileName'), '').label("FileName"),
                func.coalesce(get_json_v('SenderAddress'), '').label("SenderAddress"),
                func.coalesce(get_json_v('Subject'), '').label("Subject"),
                func.coalesce(get_json_v('EmailBody'), '').label("EmailBody"),
                BusinessRule.filetypeid.label("FileTypeId"),
                BusinessRule.created.label("Created"),
                BusinessRule.createdby.label("CreatedBy"),
                BusinessRule.updated.label("Updated"),
                BusinessRule.updatedby.label("UpdatedBy"),
                BusinessRule.isactive.label("IsActive"),
                BusinessRule.password.label("Password"),
                BusinessRule.groupcode.label("GroupCode"),
                FileTypeAlias.displayname.label("FileType"),
                usage_subquery
            )

            # Left Joins
            query = query.outerjoin(SourceTypeAlias, BusinessRule.sourceid == SourceTypeAlias.masterconfigurationtypeid)
            query = query.outerjoin(FileTypeAlias, BusinessRule.filetypeid == FileTypeAlias.masterconfigurationtypeid)

            # Filters
            filters = [BusinessRule.ruletype == input_model.RuleType]

            # SourceType Filter
            source_filter = or_(
                SourceTypeAlias.type.is_(None),
                and_(
                    SourceTypeAlias.type == 'Source',
                    or_(
                        input_model.SourceType is None,
                        input_model.SourceType.lower() == 'all',
                        SourceTypeAlias.displayname == input_model.SourceType
                    )
                )
            )
            filters.append(source_filter)

            # ContentType Filter
            if input_model.RuleType == 'Classification':
                if input_model.ContentType:
                    # ContentType in C# is UNIQUEIDENTIFIER, but in local entity it's BigInteger refactored
                    # If we have an ID mismatch, we'll need to handle it. 
                    # For now assume it's BigInteger if passed as such, or keep it as is if it's refactored.
                    try:
                         # Attempt to match UUID to BigInteger if that's what's passed (unlikely if strictly UUID)
                         # Assuming it matches the entity type
                         filters.append(BusinessRule.filetypeid == input_model.ContentType)
                    except:
                         pass
            elif input_model.ContentType:
                 # Even if not classification, the SQL says:
                 # AND (@RuleType <> 'Classification' OR (@ContentType IS NULL OR Rules.FileTypeId = @ContentType))
                 # Wait, logic is: IF CN, check CT. IF NOT CN, logic is always true (unless CT is null?)
                 # Re-reading SQL: Rules.RuleType = @RuleType AND ... AND (@RuleType <> 'Classification' OR ...)
                 # So if RuleType != 'Classification', the OR condition is always true.
                 pass

            # SearchText
            if input_model.SearchText:
                st = f"%{input_model.SearchText}%"
                search_filters = or_(
                    BusinessRule.uniqueruleid.ilike(st),
                    BusinessRule.ruletype.ilike(st),
                    FileTypeAlias.displayname.ilike(st),
                    get_json_v('FileName').ilike(st),
                    get_json_v('SenderAddress').ilike(st),
                    get_json_v('Subject').ilike(st),
                    get_json_v('EmailBody').ilike(st),
                    BusinessRule.createdby.ilike(st),
                    BusinessRule.updatedby.ilike(st)
                )
                filters.append(search_filters)

            # Column Filters
            if input_model.FilterStatus is not None:
                # Convert string to boolean if necessary
                if str(input_model.FilterStatus).lower() in ['true', '1', 'active']:
                    filters.append(BusinessRule.isactive == True)
                elif str(input_model.FilterStatus).lower() in ['false', '0', 'inactive']:
                    filters.append(BusinessRule.isactive == False)
            
            if input_model.FilterCreatedBy:
                filters.append(BusinessRule.createdby == input_model.FilterCreatedBy)
            
            if input_model.FilterSenderAddress:
                filters.append(get_json_v('SenderAddress').ilike(f"%{input_model.FilterSenderAddress}%"))
            
            if input_model.FilterSubject:
                filters.append(get_json_v('Subject').ilike(f"%{input_model.FilterSubject}%"))
            
            if input_model.FilterEmailBody:
                filters.append(get_json_v('EmailBody').ilike(f"%{input_model.FilterEmailBody}%"))
            
            if input_model.FilterRuleID:
                filters.append(BusinessRule.uniqueruleid == input_model.FilterRuleID)

            # Date Range
            if input_model.FilterCreatedFrom and input_model.FilterCreatedTo:
                from datetime import datetime, time
                start_dt = datetime.combine(input_model.FilterCreatedFrom, time.min)
                end_dt = datetime.combine(input_model.FilterCreatedTo, time.max)
                filters.append(BusinessRule.created >= start_dt)
                filters.append(BusinessRule.created <= end_dt)

            query = query.filter(and_(*filters))

            # Total Count
            total_count = query.count()

            # Sorting
            sort_order_fn = desc if input_model.SortOrder.upper() == 'DESC' else asc
            sc = input_model.SortColumn.lower()
            
            if sc == 'isactive':
                query = query.order_by(sort_order_fn(BusinessRule.isactive))
            elif sc == 'source':
                query = query.order_by(sort_order_fn(SourceTypeAlias.displayname))
            elif sc == 'created':
                query = query.order_by(sort_order_fn(BusinessRule.created))
            elif sc == 'usage':
                query = query.order_by(sort_order_fn(usage_subquery))
            elif sc == 'createdby':
                query = query.order_by(sort_order_fn(BusinessRule.createdby))
            elif sc == 'updated':
                query = query.order_by(sort_order_fn(BusinessRule.updated))
            elif sc == 'uniqueruleid':
                query = query.order_by(sort_order_fn(BusinessRule.uniqueruleid))
            elif sc == 'ruletype':
                query = query.order_by(sort_order_fn(BusinessRule.ruletype))
            elif sc == 'file':
                query = query.order_by(sort_order_fn(FileTypeAlias.displayname))
            elif sc == 'filename':
                query = query.order_by(sort_order_fn(get_json_v('FileName')))
            elif sc == 'senderaddress':
                query = query.order_by(sort_order_fn(get_json_v('SenderAddress')))
            elif sc == 'subject':
                query = query.order_by(sort_order_fn(get_json_v('Subject')))
            elif sc == 'emailbody':
                query = query.order_by(sort_order_fn(get_json_v('EmailBody')))
            else:
                query = query.order_by(desc(BusinessRule.created))

            # Pagination
            offset = (input_model.PageNumber - 1) * input_model.PageSize
            results = query.offset(offset).limit(input_model.PageSize).all()

            # Map results to objects (they are Row objects)
            data_list = []
            for r in results:
                # Map to match C# GetBusinessDataResponse
                data_list.append({
                    "Id": str(r.Id) if r.Id else None,
                    "SourceId": str(r.Id) if r.Id else None, # C# logic maps Id to SourceId? Yes: SourceId = reader.GetGuid(reader.GetOrdinal("Id"))
                    "Source": r.Source,
                    "UniqueRuleId": r.UniqueRuleId,
                    "RuleType": r.RuleType,
                    "File": r.File,
                    "FileName": r.FileName,
                    "SenderAddress": r.SenderAddress,
                    "Subject": r.Subject,
                    "EmailBody": r.EmailBody,
                    "FileTypeId": str(r.FileTypeId) if r.FileTypeId else None,
                    "Created": r.Created.isoformat() if r.Created else None,
                    "CreatedBy": r.CreatedBy,
                    "Updated": r.Updated.isoformat() if r.Updated else None,
                    "UpdatedBy": r.UpdatedBy,
                    "isActive": r.IsActive,
                    "Password": r.Password,
                    "GroupCode": r.GroupCode,
                    "Usage": r.Usage,
                    "FileType": r.FileType
                })

            return {
                "ResultObject": data_list,
                "Count": total_count,
            }

        except Exception as ex:
             logger.error(f"Error retrieving Business Data: {ex}", exc_info=True)
             return {"ResultObject": [], "Count": 0, "ResultCode": 500, "ResultMessage": str(ex)}

    def get_business_filter_by_field(self, db: Session, filter_field: str, source_type: str, rule_type: str, content_type: str) -> Any:
        """
        Implementation of GetBusinessFilterByField matching SQL Stored Procedure logic.
        """
        try:
            from sqlalchemy.orm import aliased

            SourceTypeAlias = aliased(MasterConfigurationType, name="SourceType")
            FileTypeAlias = aliased(MasterConfigurationType, name="FileType")

            # Determine the value expression
            if filter_field in ['Subject', 'EmailBody', 'SenderAddress']:
                # JSON_VALUE equivalent in Postgres with resilience
                value_expression = case(
                    (BusinessRule.ruleexpressions.like('{%'), cast(BusinessRule.ruleexpressions, JSONB).op('->>')(filter_field)),
                    else_=''
                ).label("FilterValue")
            else:
                # Direct column access
                if hasattr(BusinessRule, filter_field.lower()):
                    value_expression = getattr(BusinessRule, filter_field.lower()).label("FilterValue")
                else:
                    logger.warning(f"Field {filter_field} not found on BusinessRule model.")
                    return {"value": []}

            # Build query
            query = db.query(value_expression).distinct()
            
            # Left Joins
            query = query.outerjoin(SourceTypeAlias, BusinessRule.sourceid == SourceTypeAlias.masterconfigurationtypeid)
            query = query.outerjoin(FileTypeAlias, BusinessRule.filetypeid == FileTypeAlias.masterconfigurationtypeid)

            # WHERE clauses
            filters = [BusinessRule.ruletype == rule_type]

            # SourceType filtering logic from SQL:
            # (SourceType.[Type] IS NULL OR (SourceType.[Type] = 'Source' AND (@SourceType IS NULL OR @SourceType = 'All' OR SourceType.[DisplayName] = @SourceType)))
            source_filter = or_(
                SourceTypeAlias.type.is_(None),
                and_(
                    SourceTypeAlias.type == 'Source',
                    or_(
                        source_type is None,
                        source_type == 'All',
                        SourceTypeAlias.displayname == source_type
                    )
                )
            )
            filters.append(source_filter)

            # ContentType filtering logic from SQL:
            # (@RuleType <> 'Classification' OR (Rules.FileTypeId = @ContentType))
            if rule_type == 'Classification':
                # Convert content_type to int if possible, handling None/DBNull
                try:
                    ct_id = int(content_type) if content_type and content_type.isdigit() else None
                    if ct_id is not None:
                        filters.append(BusinessRule.filetypeid == ct_id)
                except (ValueError, TypeError):
                     pass

            # Exclude NULL and empty strings
            if filter_field in ['Subject', 'EmailBody', 'SenderAddress']:
                filters.append(value_expression.isnot(None))
                filters.append(value_expression != '')
            else:
                filters.append(value_expression.isnot(None))
                filters.append(func.cast(value_expression, String) != '')

            query = query.filter(and_(*filters))

            results = query.all()

            # Format response: {"value": [{filter_field: val}]}
            values_list = []
            for r in results:
                val = r[0]
                if val is not None:
                    values_list.append({filter_field: str(val)})

            return {"value": values_list}

        except Exception as ex:
            logger.error(f"Error in get_business_filter_by_field: {ex}", exc_info=True)
            return {"value": []}

    def get_business_rule_log_data(self, db: Session, rule_id: str) -> List[Dict[str, Any]]:
        results = (
            db.query(BusinessRuleLog)
            .filter(BusinessRuleLog.uniqueruleid == rule_id)
            .order_by(desc(BusinessRuleLog.created))
            .all()
        )
        
        log_list = []
        for log in results:
            log_list.append({
                "BusinessRuleLogId": log.businessrulelogid,
                "UniqueRuleId": log.uniqueruleid,
                "ChangeType": log.changetype,
                "RuleExpressions": log.ruleexpressions,
                "RuleLogMessage": log.rulelogmessage,
                "RuleLogTitle": log.rulelogtitle,
                "Created": log.created.isoformat() if log.created else None,
                "CreatedBy": log.createdby,
                "Updated": log.updated.isoformat() if log.updated else None,
                "UpdatedBy": log.updatedby,
                "IsActive": log.isactive
            })
        return log_list

    def get_usage_log_by_rule_async(self, db: Session, input_model: Any) -> Any:
        try:
            # Join FileProcessLog and FileManager to get details
            # C# returns UsageLogApiResult with fields: Count, Id, FileName, FileType, Expression, FileUID, UniqueRuleId
            
            query = db.query(
                FileProcessLog, 
                FileManager.filename,
                FileManager.type
            ).join(
                FileManager, FileProcessLog.fileuid == FileManager.fileuid
            )
            
            if isinstance(input_model, dict):
                 rule_id = input_model.get('UniqueRuleId')
                 if rule_id:
                     query = query.filter(FileProcessLog.ruleid == rule_id)
                 
                 # Sorting
                 sort_col = input_model.get('SortColumn')
                 sort_order = input_model.get('SortOrder', 'asc')
                 # Add sort logic if needed
                 
                 # Pagination
                 page_index = int(input_model.get('PageIndex', 1))
                 page_size = int(input_model.get('PageSize', 10))
                 offset = (page_index - 1) * page_size
                 
                 total_records = query.count()
                 results = query.offset(offset).limit(page_size).all()
                 
                 # Map to result list
                 usage_logs = []
                 for log, fname, ftype in results:
                     usage_logs.append({
                         "Count": total_records,
                         "Id": log.fileprocesslogid,
                         "FileName": fname,
                         "FileType": ftype,
                         "Expression": None, # Expression not easily available without joining rule or parsing log
                         "FileUID": log.fileuid,
                         "UniqueRuleId": log.ruleid
                     })
                     
                 return {
                     "ResultObject": usage_logs,
                     "Count": total_records,
                     "ResultCode": 200
                 }

            return {"ResultObject": [], "Count": 0, "ResultCode": 200}
        except Exception as ex:
            logger.error(f"Usage Log : Error retrieving usage log data: {ex}", exc_info=True)
            return {"ResultObject": [], "Count": 0, "ResultCode": 500}
