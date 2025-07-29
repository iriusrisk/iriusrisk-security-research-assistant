import pandas as pd

# Create sample controls data
controls_data = {
    'Name': [
        'Access Control',
        'Data Encryption', 
        'Input Validation',
        'Logging and Monitoring',
        'Network Security'
    ],
    'Description': [
        'Implement user authentication and authorization mechanisms to control access to system resources',
        'Encrypt sensitive data at rest and in transit using strong cryptographic algorithms',
        'Validate and sanitize all user inputs to prevent injection attacks',
        'Implement comprehensive logging and monitoring to detect security incidents',
        'Deploy firewalls and network segmentation to protect against network-based attacks'
    ]
}

# Create DataFrame and save as XLSX
df = pd.DataFrame(controls_data)
df.to_excel('test_controls.xlsx', index=False)
print("Test controls file created: test_controls.xlsx") 