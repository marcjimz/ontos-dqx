-- Pharmacy PBM: Pharmacy claims
CREATE TABLE IF NOT EXISTS ${CATALOG}.pbm.claims (
    claim_id        STRING        NOT NULL  COMMENT 'Unique claim identifier (CLM-NNNNNN)',
    member_id       STRING        NOT NULL  COMMENT 'Reference to members.member_id',
    ndc_code        STRING        NOT NULL  COMMENT 'National Drug Code dispensed',
    pharmacy_npi    STRING        NOT NULL  COMMENT 'Dispensing pharmacy NPI (10-digit)',
    fill_date       DATE          NOT NULL  COMMENT 'Date prescription was filled',
    days_supply     INT           NOT NULL  COMMENT 'Days supply dispensed',
    quantity        DECIMAL(10,2) NOT NULL  COMMENT 'Quantity dispensed',
    ingredient_cost DECIMAL(10,2) NOT NULL  COMMENT 'Drug ingredient cost',
    dispensing_fee  DECIMAL(10,2) NOT NULL  COMMENT 'Pharmacy dispensing fee',
    copay           DECIMAL(10,2) NOT NULL  COMMENT 'Member copay amount',
    claim_status    STRING        NOT NULL  COMMENT 'Status: paid, reversed, rejected, pending',
    created_at      TIMESTAMP     NOT NULL  COMMENT 'Record creation timestamp (UTC)',
    updated_at      TIMESTAMP     NOT NULL  COMMENT 'Record last update timestamp (UTC)'
) USING DELTA
COMMENT 'Pharmacy PBM pharmacy claims';
