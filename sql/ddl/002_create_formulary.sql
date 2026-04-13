-- Scripius PBM: Drug formulary tier list
CREATE TABLE IF NOT EXISTS ${CATALOG}.pbm.formulary (
    ndc_code            STRING    NOT NULL  COMMENT 'National Drug Code (11-digit)',
    drug_name           STRING    NOT NULL  COMMENT 'Brand drug name',
    generic_name        STRING    NOT NULL  COMMENT 'Generic drug name',
    therapeutic_class   STRING    NOT NULL  COMMENT 'Therapeutic classification',
    tier                INT       NOT NULL  COMMENT 'Formulary tier (1=generic, 2=preferred brand, 3=non-preferred, 4=specialty)',
    requires_prior_auth BOOLEAN   NOT NULL  COMMENT 'Whether prior authorization is required',
    quantity_limit      INT                 COMMENT 'Maximum quantity per fill (NULL if no limit)',
    created_at          TIMESTAMP NOT NULL  COMMENT 'Record creation timestamp (UTC)',
    updated_at          TIMESTAMP NOT NULL  COMMENT 'Record last update timestamp (UTC)'
) USING DELTA
COMMENT 'Scripius PBM drug formulary and tier assignments';
