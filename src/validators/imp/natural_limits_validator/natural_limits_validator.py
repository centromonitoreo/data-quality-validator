from validators.interface import IValidator
from validators.imp.natural_limits_validator.schemas.schemas import NaturalLimitsInput


class NaturalLimitsValidator(IValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.natural_limits = kwargs.get('natural_limits', None) 
        if not hasattr(self, 'natural_limits'):
            self.natural_limits = None

    def validate(self) -> None:
        #TODO Aqui va la implementacion
        pass

    def validate_inputs(self) -> None:
        if self.natural_limits is None or not isinstance(self.natural_limits, NaturalLimitsInput):
            raise ValueError(f"❌ ")