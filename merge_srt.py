"""
The program is used to merge a given list of .srt or .vtt files as a "chat style" dialogue 
with provided user names by sorting the lines based on the timestamp, and creating a new file 
with the merged contents and user name prepended to each line of text

This program takes in a list of file names as input, each in the format "user name from file name". 
The program reads the contents of these files, which should be in either the .srt or .vtt format, 
and creates a new file that contains the merged contents of the input files, with the user name 
prepended to each line of text. The program sorts the lines based on the timestamp, and if a merged 
output file name is not provided, it creates one in the './output' folder with a name in the format
of first_file_name_user_name1_user_name2. The program also supports logging at different levels,
and can handle the creation of the output folder if it does not exist.
"""
from typing import List
import argparse
import logging
import os
import re

vtt_pattern = re.compile(r"(\d{2}:\d{2}(:\d{2})?.\d{3}) --> (\d{2}:\d{2}(:\d{2})?.\d{3})\n(.*\n)", re.MULTILINE )
srt_pattern = re.compile(r"(^\d+$)\n^(\d\d:[0-5]\d:[0-5]\d,\d{1,3}) --> (\d\d:[0-5]\d:[0-5]\d,\d{1,3})$\n((?:^.+$\n?)+)", re.MULTILINE)

def merge_same_speaker_lines(lines: List)-> List:
    """
    Merge consecutive lines spoken by the same speaker into a single line,
    and return a new list of merged lines.
    """
    prev_user = None
    first_timestamp = None
    prev_text = ""
    merged_lines = []

    for timestamp, user, text in lines:
        if user == prev_user:
            if prev_text:
                prev_text += " "

            prev_text += text.strip()
        else:
            # save current user
            merged_lines.append((first_timestamp, prev_user, prev_text))

            # Start collecting for new user
            prev_text = text.strip()
            prev_user = user
            first_timestamp = timestamp
    
    if prev_text != "":
        merged_lines.append((first_timestamp, prev_user, prev_text))

    return merged_lines


def merge_files(file_list: List[str], merged_file_path: str, neat: bool) -> None:
    # Create a dictionary to store the file name and user name
    file_list = [file_string.split(" from ") for file_string in file_list]
    logging.info(file_list)

    # Create a list to store all lines from all files in a format of a tuple (timestamp, "[<user name>]: <text>")
    lines = []

    for user_name, file_name in file_list:
        logging.info(f"Parsing file {file_name} for user {user_name}")
        with open(file_name, "r", newline='\n') as rf:
            file_lines = rf.readlines()
            joined = ''.join(file_lines)

            if file_name.endswith('.srt'):
                # for i in range(0, len(file_lines), 3):
                #     timestamp = file_lines[i].strip()
                #     text = file_lines[i+1].strip()
                #     lines.append((timestamp, user_name, text))
                for match in re.finditer(srt_pattern, joined):
                    if match:
                        # We are skipping group 1 - Serial number
                        timestamp = match.group(2)
                        text = match.group(4)
                        lines.append((timestamp, user_name, text))
            elif file_name.endswith('.vtt'):
                for match in re.finditer(vtt_pattern, joined):
                    if match:
                        timestamp = match.group(1)
                        text = match.group()
                        lines.append((timestamp, user_name, text))
            else:
                logging.warning(f"Encountered file {file_name} with an unsupported format. Only .srt and .vtt are supported.")
    
    logging.info(f"Sorting {len(lines)} lines")
    # Sort the list of lines by the timestamp
    lines.sort(key=lambda x: re.findall(r'\d+', x[0]) )

    if neat:
        # Make it more readable by merging lines spoken by the same speaker
        logging.info("Collating consequtive lines said by the same user")
        lines = merge_same_speaker_lines(lines)
    else:
        logging.info("Each srt/vtt record written as new line. Set --neat to merge into one line per user")

    #Create a new file to write the merged contents
    if merged_file_path is None:
        output_folder = './output'
        _, first_file_name = os.path.split(file_list[0][1])
        merged_file_name = f"{first_file_name}_{'_'.join([item[0] for item in file_list])}.txt"
        merged_file_path = os.path.join(output_folder, merged_file_name)

    else:
        output_folder, merged_file_name = os.path.split(merged_file_path)
    
    merged_file_path = os.path.abspath(merged_file_path)
    output_folder, _ = os.path.split(merged_file_path)
    os.makedirs(output_folder, exist_ok=True)    # create the output folder if it does not exist

    logging.info(f"creating {merged_file_path} with {len(lines)} lines of text")
    with open(merged_file_path, "w", encoding='utf-8') as merged_file:
        merged_file.writelines([f"[{line[1]}]: {line[2]}\n" for line in lines])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge multiple files with prefixing user name')
    parser.add_argument("--log", default="warning", choices=["debug", "info", "warning", "error", "critical"])
    parser.add_argument('file_list', type=str, nargs='+', help='List of files in the format <user name> from <file name>')
    parser.add_argument('--merged_output', type=str, default=None, help='File path/name for the merge text. If set undefined, it will be saved to ./output/<first file name>_user1_...userN.txt')
    parser.add_argument("--neat", action='store_true', help="When present, consequetive lines spoken by the same person will be merged together for easier reading. Otherwise each line will be separately prepended with user name")
    args = parser.parse_args()

    log_level = getattr(logging, args.log.upper())
    logging.basicConfig(level=log_level, format='%(asctime)s %(message)s')

    merge_files(args.file_list, args.merged_output, args.neat)
