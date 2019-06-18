"""
Load the transformed data into the database.

The loader expects data in the following form:
    {
        model_class_a: model_fields,
        ...,
    }

It processes this dict in a pre-defined order (model_order).
The dependents are pulled out of the instances dict and added to the current model.

In order to determine which fields should be used to check update or create, you can specify a
model class attribute 'req_fields' (on the model class) which is then used in the get_instance method.
"""
from django.db import IntegrityError
from loguru import logger

import utils
from models import User, Tweet


_log_file_name = __file__.split("/")[-1].split(".")[0]
logger.add(f"logs/tweetpipe_{_log_file_name}.log", rotation="1 day")


class Loader:
    def __init__(self, data):
        self.data = data
        # TODO: While the data model changes, check  if there is a better ways of
        # dealing with dependencies and creation order
        self.model_order = (User, Tweet)
        self.instances = {}

    def process(self):
        """Process the transformed data and store it in all relevant models"""
        for model in self.model_order:
            fields = self.data[model]
            for dependent_name, dependent_inst in self.instances.items():
                if dependent_name in fields:
                    fields[dependent_name] = dependent_inst
            model_inst = self.get_instance(model, fields)
            self.instances[self.get_model_name(model)] = model_inst

    def get_model_name(self, model):
        return model.__name__.lower()

    def get_instance(self, model, fields):
        """
        Update or Create a new instance of model

        At this time, the id is used as only unique identifier. This results in updated user rows
        for every data lookup.

        It might be interesting to rewrite entries for the same user with different fetched_at times,
        to track the change in follower count etc..

        """

        required_fields = {}
        try:
            try:
                for req_field in model.req_fields:
                    required_fields[req_field] = fields.pop(req_field)
            except AttributeError:
                required_fields["id"] = fields.pop("id")
        except KeyError:
            logger.error(
                f"Could not retrieve required_field for {model} in {fields}"
            )
            return None

        logger.debug(f"required_fields: {required_fields}")

        inst, created = model.objects.update_or_create(
            **required_fields, defaults=fields
        )
        if created:
            logger.debug(f"Created new {inst}.")
        else:
            logger.debug(f"Updated {inst}.")

        return inst


def load_data(transformed_data):
    """Entry function to instanciate and process the Loader"""
    for data in transformed_data:
        loader = Loader(data)
        try:
            loader.process()
        except IntegrityError as e:
            # Do not break if a tweet does not fit the schema.
            # track in logs.
            logger.error(e)
            continue
