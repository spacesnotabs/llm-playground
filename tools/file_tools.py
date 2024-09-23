import os
import shutil


def read_file(filename: str) -> str:
    """
    Reads the contents of a file.

    :param filename: The path to the file.
    :return: The contents of the file, or an error message if the file cannot be opened.
    """
    if not os.path.exists(filename):
        return ""

    encodings = ['utf-8', 'latin-1', 'ascii', 'utf-16', 'windows-1252']

    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as file:
                content = file.read()
            print(f"Successfully read with {enc} encoding")
            return content
        except UnicodeDecodeError:
            print(f"Failed to read with {enc} encoding")

def write_file(filename: str, content: str) -> str:
    """
    Writes content to a file.

    :param filename: The path to the file.
    :param content: The content to write to the file.
    :return: A message indicating success or failure.
    """
    try:
        print("Writing filename: ", filename)
        # print(content)
        # Check if the target file exists

        if os.path.exists(filename):
            # Create a backup by copying the existing file
            backup_filename = f"{filename}.backup"
            shutil.copy2(filename, backup_filename)
            print(f"Backup created: {backup_filename}")
        else:
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

        processed_content = (
            content.replace('\\n', '\n')
            .replace('\\"', '"')
            .replace("\\'", "'")
        )
        # processed_content = content.encode('utf-8').decode('unicode_escape')
        with open(f"{filename}", 'w') as file:
            file.write(processed_content)
        return "Successfully wrote file."
    except IOError:
        return "Error writing file."

def process_tool_call(tool_name, tool_input):
    """
    Processes a tool call.

    :param tool_name: The name of the tool to call.
    :param tool_input: The input to the tool.
    :return: The result of the tool call.
    """
    print(f"process_tool_call({tool_name}, {tool_input})")
    if tool_name == "read_file":
        return read_file(filename=tool_input["filepath"])
    elif tool_name == "write_file":
        return write_file(filename=tool_input["filepath"],
                          content=tool_input["content"])


import os


def combine_directory_files(directory, output_file, exclude_dirs=None, exclude_extensions=None):
    """
    Combines all files in a directory into a single output file, with file path headers.

    :param directory: The path to the directory containing the files to combine.
    :param output_file: The path to the output file where the combined content will be written.
    :param exclude_dirs: A list of directory names to exclude from the combination.
    :param exclude_extensions: A list of file extensions to exclude from the combination.
    """
    print("exclude_extensions: ", exclude_extensions)
    print("exclude_dirs: ", exclude_dirs)
    if exclude_extensions is None:
        exclude_extensions = []
    if exclude_dirs is None:
        exclude_dirs = []
    with open(output_file, 'w') as out_file:
        for root, dirs, files in os.walk(directory):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                # Exclude files with specified extensions
                _, ext = os.path.splitext(file)
                print(f"file {file} has extension {ext}")
                if ext in exclude_extensions:
                    continue

                file_path = os.path.join(root, file)
                print("Adding file ", file_path)

                # Add a heading for the file
                out_file.write(f" [{file_path}] ")

                # Write the file contents to the output file
                with open(file_path, 'r') as in_file:
                    out_file.write(in_file.read())

    print(f"Combined files written to: {output_file}")
