import os
import json
from cd4ml.filenames import get_filenames
from cd4ml.validation_plots import make_validation_plot
from cd4ml.fluentd_logging import FluentdLogger

fluentd_logger = FluentdLogger()


def write_metrics(evaluation_metrics, problem_name):
    file_names = get_filenames(problem_name)
    filename = file_names['metrics']
    print("Writing to {}".format(filename))
    if not os.path.exists('results'):
        os.makedirs('results')
    with open(filename, 'w+') as score_file:
        json.dump(evaluation_metrics, score_file)


def write_validation_info(validation_metrics,
                          track,
                          true_validation_target,
                          validation_predictions,
                          problem_name):

    if track is not None:
        track.log_metrics(validation_metrics)

    fluentd_logger.log('validation_metrics', validation_metrics)

    write_metrics(validation_metrics, problem_name)

    print("Evaluation done with metrics {}.".format(
        json.dumps(validation_metrics)))

    make_validation_plot(true_validation_target, validation_predictions, track, problem_name)
