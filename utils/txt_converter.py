import os
import shutil


def convert_files_to_txt(project_dirs, file_names, output_dir):
    """
    Converts specified files in multiple project directories to .txt files in an output directory.

    Args:
        project_dirs (list): A list of paths to the project directories.
        file_names (list): A list of file names (without extensions) to convert.
        output_dir (str): The path to the output directory where the .txt files will be saved.

    Returns:
        None
    """
    # Delete all files in the output directory
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    for project_dir in project_dirs:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_name, file_ext = os.path.splitext(file)
                if file_name in file_names:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(output_dir, f"{file_name}{file_ext}.txt")
                    with open(src_file, 'r') as f:
                        content = f.read()
                    with open(dest_file, 'w') as f:
                        f.write(content)
                    print(f"Created {dest_file}")
                    with open(os.path.join(output_dir, "zzz_LAST_INPUT.txt"), "w") as f:
                        f.write(file_names_input)


if __name__ == "__main__":
    output_dir = r"G:\Mi unidad\Programming"
    file_names_input = input("Enter the file names (separated by commas) to convert: ")
    file_names = [name.strip().replace(" ", "_") for name in file_names_input.split(", ")]

    project_dirs = [
        r"C:\Users\danie\PycharmProjects\Cuesty\arminio",
        r"C:\Users\danie\PycharmProjects\Cuesty\utils",
        r"C:\Users\danie\PycharmProjects\Cuesty\tusk3",
        r"C:\Users\danie\PycharmProjects\Cuesty\frontend",
    ]

    convert_files_to_txt(project_dirs, file_names, output_dir)