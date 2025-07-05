CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    feedback TEXT,
    date_submitted DATETIME,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
facelogixthird_eyeemployees