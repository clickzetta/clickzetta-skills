# Logstash Data Import Guide

Logstash is an open-source data processing pipeline that can simultaneously collect data from multiple sources, process the data, and send it to a destination of your choice. Logstash is part of the Elastic Stack (formerly known as the ELK Stack), which also includes Elasticsearch and Kibana. These three tools are often used together to provide powerful search, analysis, and visualization capabilities. Lakehouse provides a Logstash Connector that can directly connect to Lakehouse.


# Deployment

Uninstall plugin:

```JSON
./bin/logstash-plugin uninstall logstash-output-clickzetta && rm -rf ./vendor/local_gems/

```

Install plugin:

```JSON
./bin/logstash-plugin install --no-verify --local logstash-output-clickzetta-0.0.1.gem 

```

View plugin:

```JSON
./bin/logstash-plugin list --verbose
```

> When installing the plugin, although `--no-verify --local` is specified, it still seems to download or verify certain packages from the remote server. So if you encounter a long time stuck at the `installing ...` stage, you can directly press `Ctrl+C` to force terminate. At this point, the plugin may have already been successfully installed, and you can verify by viewing the plugin list.

# Test

```JSON
cd /logstash-data
/usr/share/logstash/bin/logstash -f data/logstash.conf.5 --log.level error
```

The default number of workers is the number of machine cores (-w), and the default batch size is 125 (-b). You can adjust the corresponding parameters with -w 16 -b 200:

**File input**

Refer to [file input plugin](https://www.elastic.co/guide/en/logstash/7.17/plugins-inputs-file.html#plugins-inputs-file-sincedb_clean_after)
```JSON
input {
  file {
                path => "/logstash-data/data/igs_worker_full_log.log"
                codec => json
                start_position => "beginning"
                mode => "read"
                file_completed_action => log
                file_completed_log_path => "/logstash-data/data/temp_log/"
                exit_after_read => true
                sincedb_clean_after => "1 second"
        }
  file {
                path => "/logstash-data/data/igs_worker_full_log_1.log"
                codec => json
                start_position => "beginning"
                mode => "read"
                file_completed_action => log
                file_completed_log_path => "/logstash-data/data/temp_log/"
                exit_after_read => true
                sincedb_clean_after => "1 second"
        }
  file {
                path => "/logstash-data/data/igs_worker_full_log_2.log"
                codec => json
                start_position => "beginning"
                mode => "read"
                file_completed_action => log
                file_completed_log_path => "/logstash-data/data/temp_log/"
                exit_after_read => true
                sincedb_clean_after => "1 second"
        }
  file {
                path => "/logstash-data/data/igs_worker_full_log_3.log"
                codec => json
                start_position => "beginning"
                mode => "read"
                file_completed_action => log
                file_completed_log_path => "/logstash-data/data/temp_log/"
                exit_after_read => true
                sincedb_clean_after => "1 second"
        }
  file {
                path => "/logstash-data/data/igs_worker_full_log_4.log"
                codec => json
                start_position => "beginning"
                mode => "read"
                file_completed_action => log
                file_completed_log_path => "/logstash-data/data/temp_log/"
                exit_after_read => true
                sincedb_clean_after => "1 second"
        }
}

output {
    clickzetta {
            jdbcUrl => "jdbc:clickzetta://9a310b9b.api.clickzetta.com/quick_start?schema=public&username=index_test&password=password&virtualCluster=YETING_TEST_AP"
            username => "index_test"
            password => "password"
            schema => "public"
            table => "test_simple_data-%{+YYYY.MM.dd}"
            internalMode => false
            directMode => false
        }
}
```
**Kafka input**

Kafka input configuration reference \[[kafka as input access](https://help.aliyun.com/zh/apsaramq-for-kafka/connect-an-apsaramq-for-kafka-instance-to-logstash-as-an-input-over-the-internet)]

> Since this test case uses Alibaba Cloud's Kafka component, it is necessary to configure the relevant SSL certificates. Other cloud environments may differ, and you need to follow the official documentation of other cloud service providers.
>
> The ssl\_truststore\_location configuration requires the certificate downloaded from \[[here](https://github.com/AliwareMQ/aliware-kafka-demos/blob/master/kafka-java-demo/vpc-ssl/src/main/resources/only.4096.client.truststore.jks)]
```JSON
input {
    kafka {
                bootstrap_servers => "alikafka-pre-cn-co92y9d22001-1.alikafka.aliyuncs.com:9093,alikafka-pre-cn-co92y9d22001-2.alikafka.aliyuncs.com:9093,alikafka-pre-cn-co92y9d22001-3.alikafka.aliyuncs.com:9093"
                group_id => "logstash-test-group"
                decorate_events => true
                topics => ["igs-worker-log-for-sla"]
                security_protocol => "SASL_SSL"
                sasl_mechanism => "PLAIN"
                sasl_jaas_config => "org.apache.kafka.common.security.plain.PlainLoginModule required username='username' password='password';"
                ssl_truststore_password => "KafkaOnsClient"
                ssl_truststore_location => "/logstash-data/only.4096.client.truststore.jks"
                ssl_endpoint_identification_algorithm => ""
                consumer_threads => 3
                codec => json {
                    charset => "UTF-8"
                }
        }
}

filter {
mutate {
    add_field => {
        "kafka_topic_name" => "%{[fields][log_topic]}"
    }
}
grok {
    match => { "message" => "\[%{TIMESTAMP_ISO8601:@timestamp}\] \[%{NUMBER:thread_id}\] \[%{LOGLEVEL:log_level}\] \[%{DATA:source_file}\] \[%{DATA:function_name}\]%{GREEDYDATA:log_content}" }
}
ruby {
        code => "
            if event.get('thread_id').to_i % 2 == 0
                event.tag('even')
            else
                event.tag('odd')
            end
        "
    }
}
output {
    if "odd" in [tags] {
        clickzetta {
            jdbcUrl => "jdbc:clickzetta://9a310b9b.api.clickzetta.com/quick_start?schema=public&username=index_test&password=password&virtualCluster=YETING_TEST_AP"
            username => "index_test"
            password => "password"
            schema => "public"
            table => "liuwei_log_data-odd-%{kafka_topic_name}-%{+YYYY.MM.dd}"
            tablet => 16
            debug => true
            internalMode => false
            directMode => false
        }
    } else {
        clickzetta {
            jdbcUrl => "jdbc:clickzetta://9a310b9b.api.clickzetta.com/quick_start?schema=public&username=index_test&password=password&virtualCluster=YETING_TEST_AP"
            username => "index_test"
            password => "password"
            schema => "public"
            table => "liuwei_log_data-even-%{kafka_topic_name}-%{+YYYY.MM.dd}"
            tablet => 16
            debug => true
            internalMode => false
            directMode => false
        }
    }
}
```