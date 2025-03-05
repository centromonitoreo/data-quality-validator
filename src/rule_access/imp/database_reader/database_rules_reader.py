from rule_access.interface import IRulesReader
from validators.imp.relationship_validator.relationship_validator import RelationshipDataValidator
from validators.imp.relationship_validator.schemas.shemas import RelationshipData
from validators.interface import IValidator
from typing import List

class RuleAccessDataBase(IRulesReader):

    def get_validators(self, thematic:str) -> List[IValidator]:
        pass


    def get_validate_args(self, validator: IValidator):
        if isinstance(validator, RelationshipDataValidator):
            return self.get_relationship_args()
        raise("Validator Method is not suscribed")


    def get_relationship_args(validator: RelationshipDataValidator) -> RelationshipData:
        pass 