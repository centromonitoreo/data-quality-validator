
from validators.interface import IValidator
from validators.imp.relationship_validator.schemas.shemas import RelationshipData
from typing import List

class RelationshipDataValidator(IValidator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'relationship_data'):
            self.relationship_data = None


    def validate(self, data):
        #TODO hacer toda la logica de validacion
        for relationshipdata in self.relationship_data:
            left_table_data = data[relationshipdata.left_table]
            right_table_data = data[relationshipdata.right_table]
        pass


    def validate_inputs(self):
        if self.relationship_data is None or not isinstance(self.relationship_data, list):
            raise ValueError(f"❌ ")
        for relation_data in self.relationship_data:
            if not isinstance(relation_data, RelationshipData):
                raise
    