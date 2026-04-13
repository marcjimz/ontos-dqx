-- Scripius PBM: Seed formulary data (10 rows, all clean)
INSERT INTO ${CATALOG}.pbm.formulary VALUES
('00071015523', 'Lipitor', 'Atorvastatin', 'Statins', 1, false, 90, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('00002322330', 'Humalog', 'Insulin Lispro', 'Insulins', 2, false, NULL, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('59762384001', 'Eliquis', 'Apixaban', 'Anticoagulants', 2, false, 60, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('00006027531', 'Januvia', 'Sitagliptin', 'DPP-4 Inhibitors', 2, true, 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('00173071320', 'Advair Diskus', 'Fluticasone/Salmeterol', 'Respiratory', 3, true, 1, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('50242006201', 'Humira', 'Adalimumab', 'Biologics', 4, true, 2, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('00378180510', 'Metformin', 'Metformin HCl', 'Biguanides', 1, false, 180, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('00093505898', 'Omeprazole', 'Omeprazole', 'Proton Pump Inhibitors', 1, false, 90, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('68180072003', 'Lisinopril', 'Lisinopril', 'ACE Inhibitors', 1, false, 90, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('00591024001', 'Amoxicillin', 'Amoxicillin', 'Antibiotics', 1, false, 30, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
