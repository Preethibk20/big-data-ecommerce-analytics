CREATE DATABASE IF NOT EXISTS ${hivevar:DATABASE};
USE ${hivevar:DATABASE};
CREATE EXTERNAL TABLE IF NOT EXISTS daily_text (
    order_date STRING, seller_id STRING, orders INT,
    revenue_brl DOUBLE, mean_order_brl DOUBLE, peak_order_brl DOUBLE
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '${hivevar:INPUT}';

CREATE EXTERNAL TABLE IF NOT EXISTS daily_rcfile (
    order_date STRING, seller_id STRING, orders INT,
    revenue_brl DOUBLE, mean_order_brl DOUBLE, peak_order_brl DOUBLE
)
STORED AS RCFILE
LOCATION '${hivevar:RC_OUTPUT}';

SET hive.exec.compress.output=true;
SET mapred.output.compression.codec=org.apache.hadoop.io.compress.GzipCodec;
SET mapreduce.output.fileoutputformat.compress.codec=org.apache.hadoop.io.compress.GzipCodec;
INSERT OVERWRITE TABLE daily_rcfile
SELECT order_date, seller_id, orders, revenue_brl, mean_order_brl, peak_order_brl FROM daily_text;
ANALYZE TABLE daily_text COMPUTE STATISTICS;
ANALYZE TABLE daily_rcfile COMPUTE STATISTICS;
