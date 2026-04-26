-- Create Topics Table
CREATE TABLE IF NOT EXISTS topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content LONGTEXT NOT NULL,
    equations LONGTEXT, -- Stored as JSON
    breakdowns LONGTEXT -- Stored as JSON
);

-- Create Subtopics Table
CREATE TABLE IF NOT EXISTS subtopics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,
    parent_topic VARCHAR(255) NOT NULL, -- The slug of the parent topic
    title TEXT NOT NULL,
    content LONGTEXT NOT NULL,
    equations LONGTEXT, -- Stored as JSON
    breakdowns LONGTEXT  -- Stored as JSON
);

-- Create Simulations Table
CREATE TABLE IF NOT EXISTS simulations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(255) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    physics LONGTEXT NOT NULL,
    equations LONGTEXT -- Stored as JSON
);

-- Example Insertion (Seed Data for one topic)
-- INSERT INTO topics (slug, title, content, equations, breakdowns) VALUES (
--     'classical-mechanics', 
--     'Classical Mechanics', 
--     '<p>Your content here...</p>', 
--     '["F = ma", "p = mv"]', 
--     '{"F = ma": "Force equals mass times acceleration"}'
-- );