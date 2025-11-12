-- imaging_study table schema
-- Bronze layer: Raw CT imaging study metadata

CREATE EXTERNAL TABLE IF NOT EXISTS imaging_study (
    case_id INTEGER,
    study_instance_uid VARCHAR(128),
    series_instance_uid VARCHAR(128),
    sop_instance_uid VARCHAR(128),
    patient_age INTEGER,
    patient_sex VARCHAR(1),
    study_date VARCHAR(8),
    study_time VARCHAR(6),
    study_description VARCHAR(256),
    modality VARCHAR(16),
    series_description VARCHAR(256),
    series_number INTEGER,
    rows INTEGER,
    columns INTEGER,
    slice_thickness FLOAT,
    contrast_bolus_agent VARCHAR(128),
    contrast_bolus_route VARCHAR(64),
    kvp FLOAT,
    exposure_time FLOAT,
    age INTEGER,
    contrast BOOLEAN,
    contrast_tag VARCHAR(128),
    raw_input_path VARCHAR(512),
    tiff_name VARCHAR(256),
    dicom_name VARCHAR(256),
    file_path VARCHAR(512),
    ingestion_timestamp TIMESTAMP,
    source_dataset VARCHAR(64),
    data_version VARCHAR(16)
)
STORED AS PARQUET
LOCATION 's3://bucket/prefix/bronze/imaging/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');
