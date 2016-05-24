import logging
import socket

from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class Statsd(MetricsCollector):
    """
    A metrics collector that uses :mod:`statsd` to connect to a graphite
    instance and send incr() and timing() events.
    """

    def __init__(self, statsd_client):
        self.statsd_client = statsd_client

    def precache_request(self, context_name, model_names, duration):
        with self.statsd_client.pipeline() as pipe:
            for model_name in model_names:
                pipe.timing("precache_request.{0}.{1}"
                            .format(context_name, model_name),
                            duration * 1000)
            pipe.timing("precache_request.{0}".format(context_name),
                        duration * 1000)
            pipe.timing("precache_request",
                        duration * 1000)

    def scores_request(self, context_name, model_names, rev_id_count, duration):
        with self.statsd_client.pipeline() as pipe:
            for model_name in model_names:
                pipe.timing(
                    "scores_request.{0}.{1}.{2}"
                    .format(context_name, model_name, rev_id_count),
                    duration * 1000)
                pipe.timing("scores_request.{0}.{1}"
                            .format(context_name, model_name),
                            duration * 1000)
                pipe.incr("revision_scored.{0}.{1}"
                          .format(context_name, model_name),
                          count=rev_id_count)

            pipe.timing("scores_request.{0}".format(context_name),
                        duration * 1000)
            pipe.timing("scores_request", duration * 1000)
            pipe.incr("revision_scored.{0}".format(context_name),
                      count=rev_id_count)
            pipe.incr("revision_scored", count=rev_id_count)

    def datasources_extracted(self, context_name, model_names, rev_id_count,
                              duration):
        with self.statsd_client.pipeline() as pipe:
            for model_name in model_names:
                pipe.timing(
                    "datasources_extracted.{0}.{1}.{2}"
                    .format(context_name, model_name, rev_id_count),
                    duration * 1000)
                pipe.timing("datasources_extracted.{0}.{1}"
                            .format(context_name, model_name),
                            duration * 1000)
            pipe.timing("datasources_extracted.{0}".format(context_name),
                        duration * 1000)
            pipe.timing("datasources_extracted",
                        duration * 1000)

    def score_processed(self, context_name, model_names, duration):
        with self.statsd_client.pipeline() as pipe:
            for model_name in model_names:
                pipe.timing("score_processed.{0}.{1}"
                            .format(context_name, model_name),
                            duration * 1000)

            pipe.timing("score_processed.{0}".format(context_name),
                        duration * 1000)
            pipe.timing("score_processed", duration * 1000)

    def score_processor_overloaded(self, context_name, model_names, count=1):
        with self.statsd_client.pipeline() as pipe:
            for model_name in model_names:
                pipe.incr("score_processor_overloaded.{0}.{1}"
                          .format(context_name, model_name),
                          count=count)
            pipe.incr("score_processor_overloaded.{0}".format(context_name),
                      count=count)
            pipe.incr("score_processor_overloaded",
                      count=count)

    def score_cache_hit(self, context_name, model_names, count=1):
        with self.statsd_client.pipeline() as pipe:
            for model_name in model_names:
                pipe.incr("score_cache_hit.{0}.{1}"
                          .format(context_name, model_name),
                          count=count)
            pipe.incr("score_cache_hit.{0}".format(context_name),
                      count=count)
            pipe.incr("score_cache_hit".format(context_name),
                      count=count)

    def score_errored(self, context_name, model_names, count=1):
        with self.statsd_client.pipeline() as pipe:
            for model_name in model_names:
                pipe.incr("score_errored.{0}.{1}"
                          .format(context_name, model_name),
                          count=count)
            pipe.incr("score_errored.{0}".format(context_name), count=count)
            pipe.incr("score_errored".format(context_name), count=count)

    @classmethod
    def from_parameters(cls, *args, **kwargs):
        import statsd
        statsd_client = statsd.StatsClient(*args, **kwargs)
        return cls(statsd_client)

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
            wmflabs_statsd:
                class: ores.metrics_collectors.Statsd
                host: labmon1001.eqiad.wmnet
                prefix: ores.{hostname}
                maxudpsize: 512
        """
        logger.info("Loading Statsd '{0}' from config.".format(name))
        section = config[section_key][name]

        kwargs = {k: v for k, v in section.items() if k != "class"}
        if 'prefix' in kwargs:
            kwargs['prefix'] = kwargs['prefix'] \
                               .format(hostname=socket.gethostname())
        return cls.from_parameters(**kwargs)
