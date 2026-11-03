DELETE FROM camps;
DELETE FROM aid_requests;

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
