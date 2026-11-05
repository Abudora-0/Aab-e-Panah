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

INSERT INTO supply_batches (camp_id, item_name, quantity, expiry_days) VALUES
(1, 'Water bottles', 1000, 30),
(1, 'Rice bags', 300, 180),
(1, 'Medicine kits', 80, 14),
(2, 'Tents', 120, 90),
(2, 'Blankets', 250, 365),
(2, 'Water bottles', 700, 45),
(3, 'Rice bags', 500, 150),
(3, 'Tents', 160, 60),
(3, 'Medicine kits', 100, 10),
(4, 'Blankets', 180, 240),
(4, 'Water bottles', 400, 20),
(4, 'Tents', 70, 75),
(5, 'Rice bags', 450, 120),
(5, 'Medicine kits', 90, 12),
(5, 'Blankets', 220, 300);

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
