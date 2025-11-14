CREATE TABLE IF NOT EXISTS validation_results (
    id SERIAL PRIMARY KEY,
    validation_type VARCHAR(10) NOT NULL,
    input_file_name TEXT,
    is_valid BOOLEAN NOT NULL,
    execution_time_ms FLOAT NOT NULL,
    error_count INTEGER DEFAULT 0,
    errors TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_validation_type ON validation_results(validation_type);
CREATE INDEX IF NOT EXISTS idx_created_at ON validation_results(created_at);
CREATE INDEX IF NOT EXISTS idx_is_valid ON validation_results(is_valid);
