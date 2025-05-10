import os
import csv
import shutil
from pathlib import Path

# Paths
train_dir = Path("model/train")
classes_file = train_dir / "_classes.csv"
images_dir = train_dir

# Create class directories if they don't exist
for i in range(1, 8):
    class_dir = train_dir / f"class_{i}"
    os.makedirs(class_dir, exist_ok=True)

# Read the CSV file and move images to appropriate class directories
with open(classes_file, 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    
    for row in reader:
        if len(row) < 8:
            print(f"Skipping invalid row: {row}")
            continue
            
        filename = row[0].strip()
        class_values = [int(val) for val in row[1:8]]
        
        # Find the class (1-indexed)
        try:
            class_idx = class_values.index(1) + 1
            
            # Source and destination paths
            src_path = images_dir / filename
            dst_path = train_dir / f"class_{class_idx}" / filename
            
            # Move the file if it exists
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                print(f"Moved {filename} to class_{class_idx}")
            else:
                print(f"File not found: {src_path}")
                
        except ValueError:
            print(f"No class found for {filename}, class values: {class_values}")

print("Finished organizing files into class directories") 