"""
Module to hold Base Classes used in this project.

The ModelParser BaseClass provides all the core parsing machinery.
"""


class ModelParser:
    """Base Class for ModelParsers.

    This class provides all the basic machinery to transform fields with specified methods.
    The attribute field_transformations maps field names with transformation methods.
    These will be run on the raw data during the process phase.

    """

    def __init__(self):
        if not hasattr(self, "data"):
            raise NotImplementedError(f"Class {self.__class__.__name__} needs to define an attribute 'data'")

        if not hasattr(self, "_model"):
            raise NotImplementedError(f"Class {self.__class__.__name__} needs to define an attribute '_model'")

        if not hasattr(self, "field_transformations"):
            self.field_transformations = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(model='{self._model}')"

    def transform_fields(self):
        """Run all field_transformations"""
        for field_name, transformation in self.field_transformations.items():
            self.data[field_name] = transformation(self.data[field_name])

    def process(self):
        """Run the field transformations and return the data in a processable format"""
        self.transform_fields()
        return {self._model: self.data}

