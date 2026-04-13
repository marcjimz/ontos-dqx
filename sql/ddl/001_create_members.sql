-- Pharmacy PBM: Member enrollment master data
CREATE TABLE IF NOT EXISTS ${CATALOG}.pbm.members (
    member_id       STRING    NOT NULL  COMMENT 'Unique member identifier (MBR-NNNNNN)',
    plan_id         STRING    NOT NULL  COMMENT 'Benefit plan identifier',
    group_id        STRING    NOT NULL  COMMENT 'Employer group identifier',
    first_name      STRING    NOT NULL  COMMENT 'Member first name',
    last_name       STRING    NOT NULL  COMMENT 'Member last name',
    date_of_birth   DATE      NOT NULL  COMMENT 'Member date of birth',
    gender          STRING    NOT NULL  COMMENT 'Gender code: M, F, X, U',
    eligibility_start DATE    NOT NULL  COMMENT 'Benefit eligibility start date',
    eligibility_end   DATE              COMMENT 'Benefit eligibility end date (NULL if active)',
    created_at      TIMESTAMP NOT NULL  COMMENT 'Record creation timestamp (UTC)',
    updated_at      TIMESTAMP NOT NULL  COMMENT 'Record last update timestamp (UTC)'
) USING DELTA
COMMENT 'Pharmacy PBM member enrollment records';
