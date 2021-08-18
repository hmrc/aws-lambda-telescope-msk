from telescope_msk.send_graphyte_message import publish_kafka_to_graphite


def publish_metrics(metrics: list, graphite_host: str):
    for metric in metrics:
        keys = ["high", "low", "lag", "offset"]

        for key in keys:
            value = metric[key]
            # EG: logstash.logs.partition_0.high.$high_watermark
            publish_kafka_to_graphite(
                create_metric_key(metric, key), value, graphite_host
            )


def publish_metric_sums(metrics: list, graphite_host: str):
    sums = {}
    for metric in metrics:
        topic_name = metric["topic_name"]

        if topic_name not in sums:
            sums[topic_name] = {"sum_high": 0, "sum_low": 0, "sum_lag": 0}

        topic_sums = sums[topic_name]
        topic_sums["sum_high"] += metric["high"]
        topic_sums["sum_low"] += metric["low"]
        topic_sums["sum_lag"] += metric["lag"]

    for topic_name in sums:
        topic_sum = sums[topic_name]
        sum_range = topic_sum["sum_high"] - topic_sum["sum_low"]
        publish_kafka_to_graphite(
            f"{topic_name}.sum-high", topic_sum["sum_high"], graphite_host
        )
        publish_kafka_to_graphite(
            f"{topic_name}.sum-low", topic_sum["sum_low"], graphite_host
        )
        publish_kafka_to_graphite(
            f"{topic_name}.sum-lag", topic_sum["sum_lag"], graphite_host
        )
        publish_kafka_to_graphite(f"{topic_name}.sum-range", sum_range, graphite_host)


def create_metric_key(metric: list, key: str) -> str:
    return f"{metric['topic_name']}.partition_{metric['partition_id']}.{key}"
