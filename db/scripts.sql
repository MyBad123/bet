CREATE TABLE IF NOT EXISTS event (
    id SERIAL PRIMARY KEY,
    coefficient NUMERIC(3, 2) NOT NULL,
    deadline INTEGER NOT NULL,
    state INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS user_bet (
    id SERIAL PRIMARY KEY,
    sum_bet INTEGER NOT NULL,
    result INTEGER,
    event_id INTEGER REFERENCES event ON DELETE SET NULL
);
