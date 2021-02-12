The high watermark offset is the offset of the last message that was successfully copied to all of the log’s replicas.

Note

A consumer can only read up to the high watermark offset to prevent reading unreplicated messages.

Low
Gets the offset of the earliest message in the topic/partition. If no messages have been written to the topic, the low watermark offset is set to 0. The low watermark will also be 0 if one message has been written to the partition (with offset 0).


















Resources
https://docs.confluent.io/5.5.0/clients/confluent-kafka-dotnet/api/Confluent.Kafka.WatermarkOffsets.html#Confluent_Kafka_WatermarkOffsets__ctor_Confluent_Kafka_Offset_Confluent_Kafka_Offset_
https://jaceklaskowski.gitbooks.io/apache-kafka/content/kafka-topics.html






