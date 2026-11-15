-- Validate daily seller sales records; reject malformed rows.
raw = LOAD '$INPUT' USING PigStorage('\t') AS (
    order_date:chararray, seller_id:chararray, orders:int,
    revenue_brl:double, mean_order_brl:double, peak_order_brl:double
);
clean = FILTER raw BY order_date IS NOT NULL AND order_date MATCHES '\\d{4}-\\d{2}-\\d{2}'
    AND seller_id IS NOT NULL AND TRIM(seller_id) != ''
    AND orders IS NOT NULL AND orders >= 1
    AND revenue_brl IS NOT NULL AND revenue_brl >= 0.0
    AND mean_order_brl IS NOT NULL AND mean_order_brl >= 0.0
    AND peak_order_brl IS NOT NULL AND peak_order_brl >= 0.0;
STORE clean INTO '$OUTPUT' USING PigStorage('\t');
