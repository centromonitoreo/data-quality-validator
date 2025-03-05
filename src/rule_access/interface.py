from abc import ABC, abstractmethod
from typing import List
from validators.interface import IValidator

class IRulesReader(ABC):

    @abstractmethod
    def get_validators(self, thematic:str) -> List[IValidator]:
        pass

    @abstractmethod
    def get_validate_args(self, validator: IValidator):
        pass