/home/ubuntu/topuniv/env/bin
#!/bin/bash

# Activate the Python virtual environment
source /home/ubuntu/topuniv/env/bin/activate

# Starting number
number=1

# Run the loop until the specified upper limit
while [ $number -le 268 ]; do
    echo "Running: whed $number"
    whed $number  # Execute the whed command with the current number
    number=$((number + 1))  # Increment the number
done

echo "All commands executed!"

