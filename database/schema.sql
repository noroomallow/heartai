CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personality_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    communication_style REAL DEFAULT 50.0,
    emotional_openness REAL DEFAULT 50.0,
    conflict_style REAL DEFAULT 50.0,
    trust_level REAL DEFAULT 50.0,
    social_preference REAL DEFAULT 50.0,
    relationship_expectation REAL DEFAULT 50.0,
    interests_text TEXT DEFAULT '',
    lifestyle_text TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER,
    partner_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user1_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS compatibility_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relationship_id INTEGER NOT NULL,
    personality_score REAL DEFAULT 0.0,
    interests_score REAL DEFAULT 0.0,
    values_score REAL DEFAULT 0.0,
    communication_score REAL DEFAULT 0.0,
    lifestyle_score REAL DEFAULT 0.0,
    preference_score REAL DEFAULT 0.0,
    overall_score REAL DEFAULT 0.0,
    category VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(relationship_id) REFERENCES relationships(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS astrology_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    birth_date VARCHAR(20) NOT NULL,
    birth_time VARCHAR(20) DEFAULT '',
    birth_place VARCHAR(100) DEFAULT '',
    zodiac_sign VARCHAR(30) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS astrology_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    mode VARCHAR(20) NOT NULL DEFAULT 'single',

    person1_name VARCHAR(200) NOT NULL,

    person2_name VARCHAR(200),

    person1_data TEXT NOT NULL,

    person2_data TEXT,

    combined_data TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);



CREATE TABLE IF NOT EXISTS chat_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relationship_id INTEGER NOT NULL,
    input_type VARCHAR(20) DEFAULT 'text',
    sentiment_score REAL DEFAULT 0.0,
    positive_percentage REAL DEFAULT 0.0,
    neutral_percentage REAL DEFAULT 0.0,
    negative_percentage REAL DEFAULT 0.0,
    communication_score REAL DEFAULT 0.0,
    emotional_tone VARCHAR(50) DEFAULT 'Neutral',
    analysis_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(relationship_id) REFERENCES relationships(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relationship_id INTEGER NOT NULL,
    report_type VARCHAR(50) DEFAULT 'full_compatibility',
    report_content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(relationship_id) REFERENCES relationships(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relationship_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relationship_id INTEGER NOT NULL,
    initial_score REAL DEFAULT 0.0,
    target_score REAL DEFAULT 0.0,
    start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_date DATETIME,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(relationship_id) REFERENCES relationships(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    day_number INTEGER NOT NULL,
    week_number INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT 0,
    completed_at DATETIME,
    FOREIGN KEY(plan_id) REFERENCES relationship_plans(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS progress_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relationship_id INTEGER NOT NULL,
    communication_score REAL DEFAULT 0.0,
    emotional_score REAL DEFAULT 0.0,
    overall_score REAL DEFAULT 0.0,
    notes TEXT,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(relationship_id) REFERENCES relationships(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS assessment_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    relationship_id INTEGER,
    overall_score REAL NOT NULL DEFAULT 0.0,
    category VARCHAR(100) NOT NULL,
    personality_score REAL DEFAULT 0.0,
    compatibility_score REAL DEFAULT 0.0,
    chat_score REAL DEFAULT 0.0,
    emotional_score REAL DEFAULT 0.0,
    trust_score REAL DEFAULT 0.0,
    tests_completed INTEGER DEFAULT 0,
    score_breakdown TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(relationship_id) REFERENCES relationships(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS coach_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    relationship_id INTEGER,
    user_message TEXT NOT NULL,
    ai_reply TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(relationship_id) REFERENCES relationships(id) ON DELETE SET NULL
);
