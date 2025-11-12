-- instance table schema
-- Silver layer: Individual DICOM instances with PHI removed

CREATE EXTERNAL TABLE IF NOT EXISTS imaging_instance (
    instance_id VARCHAR(128) PRIMARY KEY,
    series_id VARCHAR(128),
    sop_instance_uid VARCHAR(128),
    instance_number INTEGER,
    image_position_patient VARCHAR(128),
    image_orientation_patient VARCHAR(256),
    pixel_spacing VARCHAR(64),
    slice_location FLOAT,
    window_center FLOAT,
    window_width FLOAT,
    rows INTEGER,
    columns INTEGER,
    bits_allocated INTEGER,
    bits_stored INTEGER,
    instance_quality_flag VARCHAR(32),
    phi_removed BOOLEAN,
    deidentification_method VARCHAR(128),
    file_size_bytes BIGINT,
    s3_uri VARCHAR(512),
    created_at TIMESTAMP
)
STORED AS PARQUET
LOCATION 's3://bucket/prefix/silver/imaging/instance/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');
