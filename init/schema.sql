CREATE TABLE marathons (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    price INTEGER NOT NULL
);

CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    tg_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT false
);

CREATE TABLE marathon_members (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    marathon_id INTEGER REFERENCES marathons(id) ON DELETE CASCADE,
    joined_date DATE
);

CREATE TABLE ills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    day_count INTEGER NOT NULL
);

CREATE TABLE days (
    id SERIAL PRIMARY KEY,
    date INTEGER NOT NULL,
    marathon_id INTEGER REFERENCES marathons(id),
    members_completed INTEGER[],
    members_forfeit INTEGER[]
);

CREATE TABLE day_results (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    marathon_id INTEGER REFERENCES marathons(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    complete BOOLEAN NOT NULL,
    reused_video BOOLEAN NOT NULL,
    video_unique_id TEXT,
    UNIQUE(member_id, marathon_id, date)
);