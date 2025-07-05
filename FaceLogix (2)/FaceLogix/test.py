from datetime import datetime, time, timedelta

def determine_status(punch_in_time, punch_out_time):
    # Define the time ranges for the statuses
    morning_start = time(16, 19)
    morning_end = time(16, 20)
    afternoon_start = time(16, 11)
    afternoon_end = time(16, 13)  # Extend the afternoon end to 1:59 PM
    evening_start = time(16, 24)
    evening_end = time(16, 26)

    # Convert timedelta objects to time if needed
    if isinstance(punch_in_time, timedelta):
        punch_in_time = (datetime.min + punch_in_time).time()
    if isinstance(punch_out_time, timedelta):
        punch_out_time = (datetime.min + punch_out_time).time()

    # Convert strings to time objects if needed
    if isinstance(punch_in_time, str):
        punch_in_time = datetime.strptime(punch_in_time, '%H:%M:%S').time()
    if isinstance(punch_out_time, str):
        punch_out_time = datetime.strptime(punch_out_time, '%H:%M:%S').time()

    # Determine status
    if punch_in_time and punch_out_time:
        # Half Day (Reorder to check before Early Departure)
        if (morning_start <= punch_in_time <= morning_end and afternoon_start <= punch_out_time <= afternoon_end) or \
           (afternoon_start <= punch_in_time <= afternoon_end and evening_start <= punch_out_time <= evening_end):
            return "Half Day"
        # Present
        elif morning_start <= punch_in_time <= morning_end and evening_start <= punch_out_time <= evening_end:
            return "Present"
        # Late Arrival
        elif punch_in_time > morning_end and evening_start <= punch_out_time <= evening_end:
            return "Late Arrival"
        # Early Departure
        elif morning_start <= punch_in_time <= morning_end and punch_out_time < evening_start:
            return "Early Departure"
    # Absent if none of the conditions are met
    return "Absent"

# Test the function with specific times
punch_in_time = '16:21:28'  # Test punch-in time
punch_out_time = '16:24:19'  # Test punch-out time

status = determine_status(punch_in_time, punch_out_time)
print(f"Status: {status}")
