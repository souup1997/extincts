import os

# Test if Python can see your CSV folder path
CSVfolder = "R:/ABETdata/CSV/"
path_exists = os.path.exists(CSVfolder)
print("CSVfolder path exists:", path_exists)  # Should print True if path is valid

# Test a specific file or subfolder path (e.g., '2024/10-28-24')
specific_path = os.path.join(CSVfolder, '2024', '10-28-24')
specific_path_exists = os.path.exists(specific_path)
print("Specific path exists:", specific_path_exists)