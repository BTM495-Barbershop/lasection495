CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    phone_number TEXT UNIQUE,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('barber', 'customer')) NOT NULL
);

CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    time_slot TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(location_id) REFERENCES locations(id),
    UNIQUE(user_id, location_id, month, day, time_slot)
);

INSERT INTO locations (name) VALUES 
    ('Downtown'),
    ('Old Montreal'),
    ('Cote-Des-Neiges');

INSERT INTO users (email, phone_number, password, role) VALUES 
    ('barber1@example.com', '1234567890', 'password123', 'barber'),
    ('barber2@example.com', '2345678901', 'password456', 'barber'),
    ('customer1@example.com', '9876543210', 'password789', 'customer'),
    ('customer2@example.com', '8765432109', 'password321', 'customer');

INSERT INTO availability (user_id, location_id, month, day, time_slot) VALUES
    (1, 1, 11, 18, '09:00'),
    (1, 1, 11, 18, '09:30'),
    (1, 1, 11, 18, '10:00'),
    (1, 2, 11, 19, '10:30'),
    (1, 3, 11, 20, '11:00');
