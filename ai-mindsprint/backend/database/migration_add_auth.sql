-- Migration script to add authentication fields to users table
-- Run this if you already have a users table without password_hash

-- Add password_hash column if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Add email_verified column if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false;

-- Add last_login column if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- Update existing users: set password_hash to a placeholder (users will need to reset password)
-- Or you can set a default password for testing
-- UPDATE users SET password_hash = '$2b$12$default_hash_here' WHERE password_hash IS NULL;

-- Make password_hash NOT NULL for new users (optional, comment out if you have existing users)
-- ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;

-- Note: If you have existing users, they will need to use password reset functionality
-- to set their passwords after this migration

