CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    tg_id INTEGER NOT NULL UNIQUE,
    username TEXT DEFAULT '',
    is_admin BOOLEAN DEFAULT false
);

CREATE TABLE marathons (
   id SERIAL PRIMARY KEY,
   chat_id BIGINT NOT NULL,
   name TEXT UNIQUE NOT NULL,
   start_date DATE NOT NULL,
   end_date DATE NOT NULL,
   price INTEGER NOT NULL,
   created_by INTEGER REFERENCES members(id) NOT NULL
);

CREATE TABLE marathon_members (
    id SERIAL PRIMARY KEY,
    marathon_id INTEGER NOT NULL REFERENCES marathons(id) ON DELETE CASCADE,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (marathon_id, member_id)
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