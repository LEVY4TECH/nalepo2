-- ===============================
-- Database: nalepo
-- ===============================

CREATE DATABASE nalepo;

\c nalepo;


-- ===============================
-- USERS TABLE
-- ===============================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);


-- ===============================
-- BLOGS TABLE
-- ===============================
CREATE TABLE blogs (
    blog_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT blogs_user_id_fkey
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


-- ===============================
-- CAMPAIGNS TABLE
-- ===============================
CREATE TABLE campaigns (
    campaign_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    goal_amount NUMERIC(12,2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ===============================
-- DONATIONS TABLE
-- ===============================
CREATE TABLE donations (
    donation_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    campaign_id INTEGER,
    amount NUMERIC(12,2) NOT NULL,
    donation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT donations_user_id_fkey
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT donations_campaign_id_fkey
        FOREIGN KEY (campaign_id)
        REFERENCES campaigns(campaign_id)
        ON DELETE CASCADE
);


-- ===============================
-- PAYMENTS TABLE
-- ===============================
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    donation_id INTEGER,
    provider VARCHAR(255) NOT NULL,
    amount NUMERIC(12,2),
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ===============================
-- EVENTS TABLE
-- ===============================
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    event_date DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ===============================
-- EVENT REGISTRATION TABLE
-- ===============================
CREATE TABLE event_registration (
    eventreg_id SERIAL PRIMARY KEY,
    event_id INTEGER,
    user_id INTEGER,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'registered',
    CONSTRAINT event_registration_event_id_fkey
        FOREIGN KEY (event_id)
        REFERENCES events(event_id)
        ON DELETE CASCADE,
    CONSTRAINT event_registration_user_id_fkey
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


-- ===============================
-- CONTACT TABLE
-- ===============================
CREATE TABLE contact (
    contact_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ===============================
-- CONTACT MESSAGES TABLE
-- ===============================
CREATE TABLE contact_messages (
    contact_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    messages TEXT NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT false
);


-- ===============================
-- VOLUNTEERS TABLE
-- ===============================
CREATE TABLE volunteers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone_digits VARCHAR(15) NOT NULL,
    period VARCHAR(50) NOT NULL,
    skills TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    date_applied TIMESTAMP DEFAULT now(),
    CONSTRAINT volunteers_user_id_fkey
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);