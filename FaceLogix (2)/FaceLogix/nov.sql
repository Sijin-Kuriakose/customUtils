ALTER TABLE attendance 
modify COLUMN statuses ENUM(
    'Present',
    'Late Arrival',
    'Early Departure',
    'Absent',
    'Half Day Present',
    'Half Day Leave'
) DEFAULT NULL;