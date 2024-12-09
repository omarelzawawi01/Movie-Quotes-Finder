import os

# Specify the directory containing the text files
directory = "movie_scripts"

# Iterate through all files in the directory
for filename in os.listdir(directory):
    # Check if the file ends with ", The.txt"
    if filename.endswith(", The.txt"):
        # Construct the new filename by removing the ", The" suffix
        new_filename = filename.replace(", The.txt", ".txt")
        
        # Get the full path to the old and new filenames
        old_file = os.path.join(directory, filename)
        new_file = os.path.join(directory, new_filename)
        
        # Rename the file
        os.rename(old_file, new_file)
        print(f'Renamed: "{filename}" to "{new_filename}"')

print("Renaming complete.")
