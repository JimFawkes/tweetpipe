"""
Module to hold Base Classes used in this project.

The ModelParser BaseClass provides all the core parsing machinery.
"""
from loguru import logger

import utils


class ModelParser:
    """Base Class for ModelParsers.

    This class provides all the basic machinery to transform fields with specified methods.
    The attribute field_transformations maps field names with transformation methods.
    These will be run on the raw data during the process phase.

    There are two types of transformations:
        1. Field Transformations (FT)- These are linked to a specific field.
            FTs need to be registered for a field in the field_transformations map
            FTs are passed the vield value and should return that singular transformed value
        2. General Transformations (GT) - These may use the entire data dict and update it in place.
            GTs need to be registered in the transformations list
            GTs do not return anything
            GTs may update multiple fields or create new ones

    The execution orderis as follows:
        1. pre_transform_filter - read relevant_fields and parse out fields
        2. FTs - individual fts will be executed in no specific order
        3. GTs - individual gts will be executed in no specific order
        4. filter_model_fields - read fields defined in the model def and filter based on those

    """

    def __init__(self):
        if not hasattr(self, "data"):
            raise NotImplementedError(
                f"Class {self.__class__.__name__} needs to define an attribute 'data'"
            )

        if not hasattr(self, "_model"):
            raise NotImplementedError(
                f"Class {self.__class__.__name__} needs to define an attribute '_model'"
            )

        if not hasattr(self, "relevant_fields"):
            raise NotImplementedError(
                f"Class {self.__class__.__name__} needs to define an attribute 'relevant_fields'"
            )

        if not hasattr(self, "field_transformations"):
            logger.warning(
                f"Class {self.__class__.__name__} does not define 'field_transformations'."
            )
            self.field_transformations = {}

        if not hasattr(self, "general_transformations"):
            logger.warning(
                f"Class {self.__class__.__name__} does not define 'general_transformations'."
            )
            self.general_transformations = []

        self._model_fields = set(
            map(lambda x: x.name, self._model._meta.fields)
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(model='{self._model}')"

    def pre_transformation_filter(self):
        """
        Filter dict based on fields in relevant_fields.

        Entries in relevant_fields may be fields or concatenation of fields:
            "field_name" - taken from highest level
            "field_name.sub_field_name.sub_sub" - traverse the dictionary
            "field_name.* - flatten subdict (mappings only!)

        IMPORTANT: The order in relevant_fields matters. E.g. if relevant_fields = ["lang", "user.lang",],
        then the last definition of lang is used.
        """
        relevant_data = {}

        if not self.relevant_fields:
            # Do not change data if an empty list is provided
            return None

        for field in self.relevant_fields:
            nested_fields = field.split(".")
            subset = self.data
            for nested_field in nested_fields[:-1]:
                # Traverse field.subfield.subsub
                subset = subset[nested_field]

            field_name = nested_fields[-1]
            if field_name == "*" or not field_name:
                # Flatten sub-dict if relevant_field ends in '.*' or just '.'
                # NOTE: This might overwrite fields. E.g., "lang" is a field in the tweet and user sub dict
                # if "lang" is unpacked as part of subset, it will overwrite the higher level field
                relevant_data = {**relevant_data, **subset}
            else:
                relevant_data[field_name] = subset[field_name]

        self.data = relevant_data

    def run_field_transformations(self):
        """
        Run all field_transformations.

        Field transformations should update the instances data attribute.

        These will be run in no specific order, therefore individual transformations should not
        depend on other transformations.
        """
        for field_name, transformation in self.field_transformations.items():
            self.data[field_name] = transformation(self.data[field_name])

    def run_general_transformations(self):
        logger.debug(
            f"RUN_GENERAL_TRANSFORMATIONS for GTs: {self.general_transformations}"
        )

        for transformation in self.general_transformations:
            transformation()

    def filter_model_fields(self):
        """
        Filter out all fields necessary for this model.

        Add new attribute with all fields.

        NOTE: How to cope with nested models?
        """
        return utils.filter_dict(self.data, self._model_fields)

    def process(self):
        """Run the field transformations and return the data in a processable format"""
        self.pre_transformation_filter()
        self.run_field_transformations()
        self.run_general_transformations()
        fields = self.filter_model_fields()
        return {self._model: fields}
