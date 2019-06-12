"""
Load the transformed data into the database.

At the moment the hierarchy is hard-coded to two levels.
TODO: This needs to become more dynamic.

"""
from loguru import logger

import utils
from models import User, Tweet


_log_file_name = __file__.split("/")[-1].split(".")[0]
logger.add(f"logs/tweetpipe_{_log_file_name}.log", rotation="1 day")


class Loader:
    def __init__(self, data):
        self.data = data
        self.models = [User, Tweet]

    def process(self):
        """Process the transformed data and store it in all relevant models"""
        # TODO: Hardcoded at this point
        for model in self.models:
            try:
                model_data = self.data.pop(model)
                sub_model_insts = {}
                for sub_model in self.models:
                    try:
                        sub_model_data = model_data.pop(sub_model)
                        sub_model_inst = self.get_instance(sub_model, sub_model_data)
                        sub_model_insts = {self.get_model_name(sub_model): sub_model_inst}

                    except KeyError:
                        logger.debug(f"Could not find sub_model {sub_model} in data of model {model}.")
                        continue
                model_inst = self.get_instance(model, {**model_data, **sub_model_insts})
            except KeyError:
                logger.debug(f"Could not find {model} in data.")
                continue

    def get_model_name(self, model):
        return model.__name__.lower()

    def get_instance(self, model, data):
        """
        Update or Create a new instance of model

        At this time, the id is used as only unique identifier. This results in updated user rows
        for every data lookup. 

        It might be interesting to rewrite entries for the same user with different fetched_at times,
        to track the change in follower count etc..

        """

        fields = utils.filter_dict(data, self.get_model_field_set(model))

        try:
            inst_id = fields.pop("id")
        except KeyError:
            logger.error(f"Could not retrieve an id for {model} in {data}")
            return None

        inst, created = model.objects.update_or_create(id=inst_id, defaults=fields)
        if created:
            logger.debug(f"Created new {inst}.")
        else:
            logger.debug(f"Updated {inst}.")

        return inst

    def get_model_field_set(self, model):
        """Return a set of all the defined field_names in the model"""
        return set(map(lambda x: x.name, model._meta.fields))


def load_data(transformed_data):
    """Entry function to instanciate and process the Loader"""
    for data in transformed_data:
        loader = Loader(data)
        loader.process()
