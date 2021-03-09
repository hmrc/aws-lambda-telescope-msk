#!/usr/bin/env python3

import logging
from pprint import pprint

from telemetry.telescope_msk.cli import cli
from telemetry.telescope_msk.logger import create_app_logger
from telemetry.telescope_msk.consumer import list_offsets, get_consumer, list_offsets_for_topic
from telemetry.telescope_msk.msk import get_plaintext_bootstrap_servers

# what do we hope to achieve?
# Overall grab consumer lag for all consumer groups in a grafana dashboard
# / Return a list of consumer groups excluding aws msk
# / filter out __consumer_offsets and __aws_msk_etc
# / Get the metrics for each partition in group
# / Transform into a string  something like ${partition}-${topic_name}-${metric_name}, Check with Vitor
# / Push to graphite
# / Build a grafana dashboard to display it.
# / Make available to consumer.py
#   Make it run continuously in a ecs task


def main(log_level: str = logging.DEBUG, graphite_host="graphite") -> None:
    create_app_logger(log_level)
    bootstrap_servers = get_plaintext_bootstrap_servers()

    consumer_groups_topic_names = {
        'logstash': 'logs',
        'metrics': 'metrics'
    }

    for group_id in consumer_groups_topic_names:
        topic_name = consumer_groups_topic_names[group_id]
        msk_consumer = get_consumer(bootstrap_servers, group_id)

        metrics = list_offsets_for_topic(msk_consumer, topic_name)
        msk_consumer.close()

        pprint(metrics)

    # publish_metric_sums(metrics, graphite_host)
    # publish_metric_sums(metrics, graphite_host)

    # for metric in metrics:
    #     keys = ['high', 'low', 'lag', 'offset']
    #
    #     for key in keys:
    #         value = metric[key]
    #         # EG: logstash.logs.partition_0.high.$high_watermark
    #         # print(create_metric_key(metric, group.id, key)+f"={value}")
    #         print(f"{key}.{metric}")
    #
    # topics = list_topics(consumer)
    # for topic in topics:
    #     for partition in get_committed_partitions_for_topic(consumer, topic):
    #         print("\n \n \n partitions")
    #         print(partition)


if __name__ == '__main__':
    cli(main)
