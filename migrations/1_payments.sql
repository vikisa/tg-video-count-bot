CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    marathon_id INTEGER NOT NULL REFERENCES marathons(id),
    member_id INTEGER NOT NULL REFERENCES members(id),
    payment INTEGER
);
