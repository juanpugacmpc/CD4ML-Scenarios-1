from cd4ml.problems.houses.readers.stream_data import stream_data
from cd4ml.problems.houses.readers.zip_lookup import get_zip_lookup
from cd4ml.splitter import splitter
from cd4ml.problem import Problem
from cd4ml.utils import average_by
from cd4ml.get_problem import get_pipeline_params
from cd4ml.feature_set import get_feature_set_class


class HousesProblem(Problem):
    def __init__(self,
                 feature_set_name='default',
                 problem_params_name='default',
                 ml_params_name='default',
                 algorithm_name='default'):

        super(HousesProblem, self).__init__(feature_set_name=feature_set_name,
                                            problem_params_name=problem_params_name,
                                            ml_params_name=ml_params_name,
                                            algorithm_name=algorithm_name)

        self.problem_name = 'houses'
        self.pipeline_params = get_pipeline_params(self.problem_name,
                                                   problem_params_name,
                                                   ml_params_name,
                                                   algorithm_name,
                                                   __file__)

        self._stream_data = stream_data
        self.training_filter, self.validation_filter = splitter(self.pipeline_params)

        # feature set
        if self.feature_set_name == 'default':
            self.feature_set_name = 'feature_set_1'

        feature_set_class = get_feature_set_class(self.feature_set_name, __file__)
        self.feature_set = feature_set_class({})

        # this will call whatever generic steps should be done after derived class init
        self._post_init()

    def prepare_feature_data(self):
        # do the work required to look up derived features
        if self.feature_set is not None:
            self.feature_set.zip_lookup = get_zip_lookup(self.pipeline_params)

        train_data = self.training_stream()

        avg_price_prior = 350000.0
        prior_num = 5

        averages = average_by(train_data, 'price', 'zipcode',
                              prior_num=prior_num, prior_value=avg_price_prior)

        for k, v in self.feature_set.zip_lookup.items():
            # modify the zip_lookup values in place
            average_count = averages.get(k)
            if average_count is None:
                v['avg_price_in_zip'] = avg_price_prior
                v['num_in_zip'] = 0
            else:
                average, count = average_count
                v['avg_price_in_zip'] = average
                v['num_in_zip'] = count
