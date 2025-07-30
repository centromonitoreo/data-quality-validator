from validators.interface import IValidator
from validators.imp.natural_limits_validator.schemas.schemas import NaturalLimitsInput, VerticalError,VerticalErrors, HorizontalErrors, HorizontalError, NaturalLimitsErros

import pandas as pd
import geopandas as gpd
from typing import Union
from rule_access.imp.database_reader.config import engine

from error_handlers.imp.delete_strategy.delete_strategy import DeleteErrorHandler
from validators.imp.natural_limits_validator.adapters.delete_errors_handler_adapter import DeleteErrorHandlerAdapter


class NaturalLimitsValidator(IValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        errors = None
        if not hasattr(self, 'natural_limits'):
            self.natural_limits = None

    def validate_vertical_parameters(self, data: Union[pd.DataFrame, gpd.GeoDataFrame], vertical_limits) -> VerticalErrors:
        errors = []

        param_col = vertical_limits.column_name_param
        value_col = vertical_limits.column_name_value

        # data[param_col] = data[param_col].astype(float).astype('Int64').astype(str)

        for limit in vertical_limits.limits:
            param = limit.param_name
            limit_max = limit.limit_max
            limit_min = limit.limit_min
            
            param_data = data[data[param_col] == param]
            
            for index, row in param_data.iterrows():
                try:
                    value = float(row[value_col])
                except (ValueError, TypeError):
                    value = pd.NA
                if (limit_max is not None and value > limit_max) or (limit_min is not None and value < limit_min):
                    errors.append(
                        VerticalError(param=param,
                                      index=index,
                                      value=value,
                                      limit_max=limit_max,
                                      limit_min=limit_min
                                      ))

        return [VerticalErrors(column_name=value_col, errors=errors)]

    def validate_horizontal_parameters(self, data: Union[pd.DataFrame, gpd.GeoDataFrame], horizontal_limits) -> HorizontalErrors:
        results = []

        for limit in horizontal_limits.limits:
            param = limit.param_name
            limit_max = limit.limit_max
            limit_min = limit.limit_min

            errors = []

            for index, value in data[param].items():
                if pd.notnull(value) and (
                    (limit_max is not None and value > limit_max) or 
                    (limit_min is not None and value < limit_min)
                ):
                    errors.append(
                        HorizontalError(
                            # param=param,
                            index=index,
                            value=value,
                            limit_max=limit_max,
                            limit_min=limit_min
                        )
                    )

            if errors:
                results.append(
                    HorizontalErrors(
                        column_param=param,
                        errors=errors
                    )
                )

        return results

    def validate(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame], **kwargs
    ) -> NaturalLimitsErros:
        if self.natural_limits.distribution_param_type.value == "Vertical":
            vertical_errors = self.validate_vertical_parameters(data, vertical_limits=self.natural_limits.limits_data)
            errors = NaturalLimitsErros(
                distribution_param_type = self.natural_limits.distribution_param_type,
                errors=vertical_errors
            )
        elif self.natural_limits.distribution_param_type.value == "Horizontal":
            horizontal_errors = self.validate_horizontal_parameters(data, horizontal_limits=self.natural_limits.limits_data)
            errors = NaturalLimitsErros(
                distribution_param_type = self.natural_limits.distribution_param_type,
                errors=horizontal_errors
            )

        self.errors = errors

    def validate_inputs(self) -> None:
        print(type(self.natural_limits))
        if self.natural_limits is None or not isinstance(self.natural_limits, NaturalLimitsInput):
            raise ValueError("❌ ")
    
    def error_handler_adapter(self, error_hadler_strategy, table_name):
        if error_hadler_strategy == DeleteErrorHandler:
            return {"delete_errors_input": DeleteErrorHandlerAdapter(self.errors, table_name).adpter_errors()}