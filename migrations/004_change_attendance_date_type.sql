-- Migration to change attendance session_date from TIMESTAMP to DATE
-- This removes time component from attendance tracking

BEGIN;

-- Step 1: Create a temporary DATE column
ALTER TABLE attendances ADD COLUMN session_date_new DATE;

-- Step 2: Copy data, converting TIMESTAMP to DATE
UPDATE attendances SET session_date_new = session_date::DATE;

-- Step 3: Drop old column
ALTER TABLE attendances DROP COLUMN session_date;

-- Step 4: Rename new column
ALTER TABLE attendances RENAME COLUMN session_date_new TO session_date;

-- Step 5: Make NOT NULL and add index
ALTER TABLE attendances ALTER COLUMN session_date SET NOT NULL;
CREATE INDEX IF NOT EXISTS idx_attendances_session_date ON attendances(session_date);

-- Step 6: Add unique constraint to prevent duplicate attendance on same day
-- (one student can have only one attendance record per day per group)
ALTER TABLE attendances 
ADD CONSTRAINT uq_attendance_student_group_date 
UNIQUE (student_id, group_id, session_date);

COMMIT;
