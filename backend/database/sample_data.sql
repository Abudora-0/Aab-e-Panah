DELETE FROM supply_batches;
DELETE FROM aid_requests;
DELETE FROM camps;

INSERT INTO camps (name, district, capacity) VALUES
('Dadu Relief Camp', 'Dadu', 500);

INSERT INTO camps (name, district, capacity) VALUES
('Jacobabad Safe Shelter', 'Jacobabad', 350);

INSERT INTO camps (name, district, capacity) VALUES
('Nowshera Community Camp', 'Nowshera', 700);

INSERT INTO camps (name, district, capacity) VALUES
('Rajanpur Flood Relief Camp', 'Rajanpur', 250);

INSERT INTO camps (name, district, capacity) VALUES
('Charsadda Relief Centre', 'Charsadda', 600);

INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Water bottles', 1000, 30 FROM camps
WHERE name = 'Dadu Relief Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Rice bags', 300, 180 FROM camps
WHERE name = 'Dadu Relief Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Medicine kits', 80, 14 FROM camps
WHERE name = 'Dadu Relief Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Tents', 120, 90 FROM camps
WHERE name = 'Jacobabad Safe Shelter';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Blankets', 250, 365 FROM camps
WHERE name = 'Jacobabad Safe Shelter';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Water bottles', 700, 45 FROM camps
WHERE name = 'Jacobabad Safe Shelter';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Rice bags', 500, 150 FROM camps
WHERE name = 'Nowshera Community Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Tents', 160, 60 FROM camps
WHERE name = 'Nowshera Community Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Medicine kits', 100, 10 FROM camps
WHERE name = 'Nowshera Community Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Blankets', 180, 240 FROM camps
WHERE name = 'Rajanpur Flood Relief Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Water bottles', 400, 20 FROM camps
WHERE name = 'Rajanpur Flood Relief Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Tents', 70, 75 FROM camps
WHERE name = 'Rajanpur Flood Relief Camp';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Rice bags', 450, 120 FROM camps
WHERE name = 'Charsadda Relief Centre';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Medicine kits', 90, 12 FROM camps
WHERE name = 'Charsadda Relief Centre';
INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days)
SELECT camp_id, 'Blankets', 220, 300 FROM camps
WHERE name = 'Charsadda Relief Centre';

INSERT INTO aid_requests (area_name, needs, severity) VALUES
('Mehar', 'water', 5);

INSERT INTO aid_requests (area_name, needs, severity) VALUES
('Thul', 'food', 4);

INSERT INTO aid_requests (area_name, needs, severity) VALUES
('Nowshera Village', 'tents', 3);

INSERT INTO aid_requests (area_name, needs, severity) VALUES
('Rajanpur East', 'medicine', 5);

INSERT INTO aid_requests (area_name, needs, severity) VALUES
('Charsadda Lowland', 'boats', 4);
