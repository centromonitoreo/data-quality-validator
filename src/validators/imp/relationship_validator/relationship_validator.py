
from validators.interface import IValidator
from validators.imp.relationship_validator.schemas.shemas import RelationshipData
from typing import List

class RelationshipDataValidator(IValidator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'relationship_data'):
            self.relationship_data = None


    def validate(self, data):
        pass


    def validate_inputs(self):
        if self.relationship_data is None or isinstance(self.relationship_data, List[RelationshipData]):
            raise ValueError(f"❌ ")