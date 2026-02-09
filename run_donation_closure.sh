#!/bin/bash
# Wrapper script to run donation closure with virtual environment

cd /home/ubuntu/JMCDonations

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "ERROR: Virtual environment not found at .venv/bin/activate"
    exit 1
fi

# Run the Python script
python run_donation_closure.py

# Capture exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

exit $EXIT_CODE
