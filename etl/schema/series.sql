-- series table schema
-- Silver layer: Imaging series with quality flags

CREATE EXTERNAL TABLE IF NOT EXISTS imaging_series (
    series_id VARCHAR(128) PRIMARY KEY,
    study_id VARCHAR(128),
    patient_id VARCHAR(64),
    series_number INTEGER,
    series_description VARCHAR(256),
    modality VARCHAR(16),
    num_instances INTEGER,
    series_date VARCHAR(8),
    series_time VARCHAR(6),
    body_part_examined VARCHAR(64),
    protocol_name VARCHAR(128),
    contrast_administered BOOLEAN,
    series_quality_flag VARCHAR(32),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
STORED AS PARQUET
LOCATION 's3://bucket/prefix/silver/imaging/series/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');
