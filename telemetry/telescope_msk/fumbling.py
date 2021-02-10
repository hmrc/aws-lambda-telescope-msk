import json

group_ID = 'logstash'
state = 'Stable'
protocol = 'range'
protocol_type = 'consumer'
partition0, partition1, partition2 = 0, 1, 2
partition0_offset, partition1_offset, partition2_offset = 3, 4, 5
partition0_watermark, partition1_watermark, partition2_watermark = 6, 7, 8
partition0_lag, partition1_lag, partition2_lag = 9, 10, 11

logs = {'logs': {'Partition': [partition0, partition1, partition2],
                 'Group Offset': [partition0_offset, partition1_offset, partition2_offset],
                 'High Watermark': [partition0_watermark, partition1_watermark, partition2_watermark],
                 'Lag': [partition0_lag, partition1_lag, partition2_lag],
                 'Metadata': []
                 }
        }

logstash_kaf_dict = {'Group ID': group_ID,
                     'State': state,
                     'Protocol': protocol,
                     'Protocol Type': protocol_type,
                     'Offsets': logs,

                     'Members': {
                         'logstash-0':
                             {
                                 'Host': "/10.16.1.105",
                                 'Assignments':
                                     {
                                         'Topic': 'Partitions',
                                         '-----': '----------',
                                         'logs': '[0]'
                                     }
                             },
                         'logstash-0':
                             {
                                 'Host': "/10.16.0.59",
                                 'Assignments':
                                     {
                                         'Topic': 'Partitions',
                                         '-----': '----------',
                                         'logs': '[1]'
                                     }
                             },
                         'logstash-0':
                             {
                                 'Host': "/10.16.2.6",
                                 'Assignments':
                                     {
                                         'Topic': 'Partitions',
                                         '-----': '----------',
                                         'logs': '[2]'
                                     }
                             }
                     }
                     }

kaf_json = json.dumps(logstash_kaf_dict)
