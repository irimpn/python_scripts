__author__ = 'Navin'


 from pyspark.streaming.kafka import KafkaUtils


 directKafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})