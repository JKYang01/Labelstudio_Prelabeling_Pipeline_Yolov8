import shutil
import os

def clean_directory(directory_path):
    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # Iterate over all files and directories in the given directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                # Remove files
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                # Remove directories and their contents
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f'The directory {directory_path} does not exist.')


if __name__ =="__main__":
    from pathlib import Path
    # Get the directory of the current script
    script_dir = Path(__file__).resolve().parent
    execute_dir = Path(script_dir).resolve().parent
    
    clean_directory(f"{execute_dir}/temp/work")