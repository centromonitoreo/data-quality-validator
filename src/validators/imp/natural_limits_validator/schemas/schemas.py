from pydantic import BaseModel
from enum import Enum
from typing import Union, List


#ENTRADAS
class DistributionParamType(Enum):
    columns = "columns" #Ejemplo aire o suelo
    rows = "rows" #Ejemplo agua superficial

class LimitPara(BaseModel):
    param_name:Union[str, int] #Para el caso de columns se coloca aca el nombre de la columna y para caso de rows el nombre del parametro
    limit_max:float
    limit_min:float

class ColumnsLimit(BaseModel):
    limits: List[LimitPara]

class RowsLimits(BaseModel):
    column_name: str
    limits: List[LimitPara]

class NaturalLimitsInput(BaseModel):
    distribution_param_type: DistributionParamType
    limits_data: Union[ColumnsLimit, RowsLimits]

#SALIDAS

#Manejo de errores cuando son columnas
class ColumnError(BaseModel):
    index: int
    value: float
class ColumnsErrors(BaseModel):
    column_name: str
    limit_max:float
    limit_min:float
    errors: List[ColumnError]

#Manejo de erroes cuando son por filas

class RowError(BaseModel):
    index: int
    value: float


class ParamRowsErrors(BaseModel):
    param_name:str
    limit_max:float
    limit_min:float
    errors: List[RowError]

class RowsErrors(BaseModel):
    column_name:str
    errors: List[ParamRowsErrors]

#ESTA DE NaturalLimitsErros ES LA QUE DEBE GENERAR LA SALIDA 
class NaturalLimitsErros(BaseModel):
    distribution_param_type: DistributionParamType
    errors: Union[ParamRowsErrors, ColumnsErrors]
    