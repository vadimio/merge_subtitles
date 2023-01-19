# merge_subtitles
Merge a list of subtitle files in a .srt or .vtt format based on a timestamp to make chat like txt file.

# Warning
Only the .VTT has been tested. I do not have .SRT transcriptions yet. Will update as soon as I am done

# Usage
## usage: merge_srt.py [-h] [--log {debug,info,warning,error,critical}] [--merged_output MERGED_OUTPUT] [--neat] file_list [file_list ...]

Merge multiple files with prefixing user name

## positional arguments:
  file_list             List of files in the format <user name> from <file name>

## options:
####  -h, --help            
show this help message and exit
####  --log {debug,info,warning,error,critical}
####  --merged_output MERGED_OUTPUT
File path/name for the merge text. 
If set undefined, it will be saved to ./output/first_file_name_user1_user2_..._userN.txt
####  --neat                
When present, consequetive lines spoken by the same person will be merged together for easier reading. Otherwise each line will be separately prepended with user name
  
# Command Line Example
python3 merge_srt.py "john from ./Recording_1083.vtt" "jane from ./Recording_1084.vtt" --merged_output="./merged_result.txt" --clean
