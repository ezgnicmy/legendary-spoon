# TODO: Make the command line parameter implementation work AND then modulize it so that it can be recycled as-is with both the command line AND an external front end feeding params to it

# JOB #1: Input a text file into the stuff like balabolka / balcon
# E.g.:  balcon -i textfile -w output.wav
# As syntax: -p audio_program -i i_param -w o_param

import os
import sys

import logging # Deals with some exception messaging
import subprocess # Implements forking i.e. starting command line processes to do type in the setting parameters in an automated fashion



import argparse # Processes command line parameters

# To allow some simple configuration re-use for lazy people
from configparser import ConfigParser
config = ConfigParser()

# Checks and reads the program path from the config file, program_param can be a preset config alias or a full path
# Possible: add checking for the program type ("text2speech" or "video")
# Used by -p and -v flags
def check_program(program_param, config_file_path, parser, p_type="undefined"):
    text_to_speech_program_path = None
    if program_param is not None and program_param.lower() is not 'default':
        print("eat shit")
        try:
            found_section = None
            # Option 1: Try interpreting the path-parametrer as a preset name and finding its preset path from the config file
            config.read(config_file_path)
            if config.has_section(program_param):
                found_section = True
                text_to_speech_program_path = config.get(program_param, 'TEXT2SPEECH_PROGRAM_PATH')
            else:
                # Option 2: Try to to take the path as a file system path
                # TODO: check if there is anything where the program poth points to, though try to be hands-off in case it is some advanced programming trick
                # I.e. check for validity, not for content
                # STEP 1: Check for a local file or the specified full path existing
                tmp_path = os.path.join(cwd, program_param)
                if os.path.exists(tmp_path): # Test for the local path
                    text_to_speech_program_path = tmp_path
                elif os.path.exists(program_param): # Test for the full path existing
                    text_to_speech_program_path = program_param
                else:
                    # The required target file not found, aborting
                    raise ValueError('Program not found in the given path')
        except BaseException:
            logging.exception('Exception when processing a save-preset parameter %s', program_param)
    return text_to_speech_program_path




imgDir = None # Stores the directory path to the randomly selected video background pictures
param_s, param_s_path, param_p, param_i, param_o = (None,)*5 # Mass-initialize a bunch of variables as None - currently UNUSED


# TODO: change the epilog once you start adding the FFMPEG auto-movie conversion functionality to it
parser = argparse.ArgumentParser(description='Text-to-Video Converter', epilog="For example, type \'python main.py -s balcon FULL_FILE_SYSTEM_PATH_TO_BALCON -i text_for_speech.txt -p balcon -o output.wav\' to produce a computer-voiced audio from the text by utilizing balcon (installed separately)." )
# parser.add_argument("strings", metavar="strings", nargs="*", type=str) # Enables an arbitrary number of str params at the end of the command line

parser.add_argument("-s", help="Save a program path, syntax PROGRAM_ALIAS TEXT2SPEECH_PROGRAM_PATH {PROGRAM_ALIAS TEXT2SPEECH_PROGRAM_PATH}, is read before -p allowing you to immediately use it. You can give multiple -s flags and they will all be processed.", metavar=("PROGRAM_ALIAS", "TEXT2SPEECH_PROGRAM_PATH"), nargs="*")
parser.add_argument("-p", action='store', help="The preset program path alias or the full program path, use -s flag to set a preset", metavar="PROGRAM_ALIAS_OR_PATH")
parser.add_argument("-i", help="The text file used to generate the audio file text-to-speech style from.", metavar="INPUT_FILE")
parser.add_argument("-v", help="The path to the video generation / converter / rendering program such as ffmpeg, used to put the speech into a video.", metavar="VIDEO_PROGRAM")
parser.add_argument("-o", default="output", help="The output file name. Usually defaults to output.[EXT] (.wav and .mp4), depending on the used text-to-speech program.", type=str, metavar="OUTPUT_FILE")

cwd = os.getcwd() # Current working directory

args = parser.parse_args() # Put the command line parameter parser together, store the parameter into args as accessable fields

config_file = 'config.ini'
config_file_path = os.path.abspath(config_file)

try:
    # Create the file if it does not exist
    if not os.path.exists(config_file_path):
        config.add_section('default') # You need to add a section for it work and 'default' can be used for that
        config.write(open(config_file_path, 'w'))
except BaseException:
    logging.exception('Error while trying to create the new config file')


print("s: ", args.s) # DEBUG


''' Quick ways to generate integers from floating point values:
    -to round down: int(x)
    -to round to the nearest integer: (n + d // 2) // d
    -to round up: int(n // v) + (n % v > 0)
'''

# Flag -s: Save preset configurations to the file 'config.ini' because it is an established file name
# Needs to be processed before the -p flag so that you can utilize the preset converter path immediately and not have to input the path twice
# TODO: Check how it behaves with multiple -s flags set
s_values_set = [] # Tracks and lists the added or changed config preset entries
if args.s is not None and len(args.s) > 1 and args.s[0] is not None and args.s[1] is not None:
    try:
        # TODO: add a loop to process the multiple -s param pairs
        print("suck a lemon")
        # The following line simply divides the param list length by 2 and rounds it down. Th
        for i in range(int(len(args.s) / 2)):
            tmp = i * 2; # A store-only variable, practically a constant. It is there simplify the index parameters and to cut down on redundant calculations
            if os.path.exists(os.path.abspath(args.s[tmp])): # Check out of sync params (here: the alias name) - reject AND do-not-fix behavior
                print("Error, got a file path - a program alias expected: ", args.s[tmp])
            elif not os.path.exists(os.path.abspath(args.s[tmp+1])): # See above, validating the file system path
                print("Error, did not get a valid file path param as expected: ", args.s[tmp+1])
            elif args.s[0].lower() is 'default':
                print('Forbidden alias name detected, do not use \"default\" as your preset alias.')
            else:
                config.read(config_file_path)
                print('sections: ', config.sections(), ", config file: ", config_file_path) # DEBUG
                full_program_path = os.path.abspath(args.s[tmp+1]) # Convert the path into a full path
                if not os.path.exists(full_program_path): # Warn the user in case the file not existing
                    print('Warning - the program file does not exist. The conversion is not likely to work.')
                if not config.has_section(args.s[tmp]):
                    config.add_section(args.s[tmp])
                config.set(args.s[tmp], 'TEXT2SPEECH_PROGRAM_PATH', full_program_path)
                with open(config_file_path, 'w') as f: # This operation blocks disk reads - do not put anything other than writing actions here
                    config.write(f)
                s_flag_set = True # Used mostly for internal status checking
                s_values_set = s_values_set + [args.s[tmp], args.s[tmp+1]]
    except BaseException:
        logging.exception('Exception when processing a save-preset parameter %s, %s', args.s[0], args.s[1])

text_to_speech_program_path = None
video_program_path = None


# Flag -p: Check if the given program parameter matches a preset name and use the data stored in the preset instead if possible
if args.p is not None:
    text_to_speech_program_path = check_program(program_param=args.p , config_file_path=config_file_path, parser=config, p_type="text2speech")

# Flag -v: Check the video program parameter and if it is in the config file already - essentially the same as with -p
if args.v is not None:
    video_program_path = check_program(program_param=args.v , config_file_path=config_file_path, parser=config, p_type="video")


#print("p: ", args.p) # DEBUG
#print(args.p is not None)
#print(args.p is not None and args.p.lower() is not 'default')

input_file_path = None

# Flag -i: Abort if the required input parameter is not supplied
# TODO: Possible to add the support for command-line text strings later
if args.i is None or not isinstance(args.i, str):
    print("No input parameter given, nothing to do. Type \'python", parser.prog, "--help\' to get a list of commands." )
    sys.exit(1) # Use the code 1 to signal a command-line error
else:
    full_input_path = os.path.abspath(args.i)
    if not os.path.exists(full_input_path):
        print("Input file not found, exiting.")
        sys.exit(1) # Use the code 1 to signal a command-line error
if s_flag_set:
  print("Preset aliases set: ", s_values_set)
#print(args) # DEBUG
#print(parser) # DEBUG

# Flag -o: Change the output file name when needed - if you do not specify the file extensions, files with the extensions .wav and .mp4 will be generated
use_default_file_types = False

chosen_file_name_extension = None
available_file_name = None
tmp = args.o.split('.')
current_file_name_base = None
if '.' not in args.o or len(tmp) < 1:
    use_default_file_types = True
    chosen_file_name_extension = '.mp4'
    current_file_name_base = args.o # Use the output parameter as-is as it only contains the base file name part
else:
    chosen_file_name_extension = '.' + tmp[len(tmp-1)]
    current_file_name_base = ''
    for i in range(len(tmp-1)): # Intentionally leave out the last element - for cases where the user has .'s in the base name part
        current_file_name_base = current_file_name_base + tmp[i] + '.'
    current_file_name_bas = current_file_name_bas[:-1] # Remove the last dot, removes the last character from the string
# Check that the intended file names are not in use and if they are, append numbers at the end until it works
attempt_limit = 1000 # Eliminate infinite looping
i = 0 # A stepper variable
tmp_file_name = None
# No need to fight file name conflicts - just create a new one and let the user delete the old ones as needed 
if os.path.exists(os.path.abspath(current_file_name_base + chosen_file_name_extension)):
    tmp_file_name = current_file_name_base + '{foo:03d}'.format(foo=i)
    while (os.path.exists(os.path.abspath(tmp_file_name + ".wav")) or os.path.exists(os.path.abspath(tmp_file_name + chosen_file_extension))) and i < attempt_limit:
         # Pad the name with zeroes and incremented numbers if the file already exists
         i = i + 1 # i = 1000 would get printed as 1000 despite 03d
         tmp_file_name = current_file_name_base + '{foo:03d}'.format(foo=i)
else:
    print('The file does not exist yet:', current_file_name_base + chosen_file_name_extension)
    tmp_file_name    
         


if i < 1000:
    print("File name selected:", tmp_file_name )
    
else:
    print("Error, could not assign a file name.")





# TODO: Put together the command-line parameter string. Let the user set up the program parameters preferably with a graphical front-end with preset common program options
# TODO: Load the command line command templates from a separate files and use text substitution to fill in the commands.
command_parameter_string = None
split_command = []

# EXPERIMENTAL, to test the command flow, will be replaced later with something more systematic and common-purpose implementation
# Case 1: Try to test for balcon, you can add other options as elif's 
#print(text_to_speech_program_path) # DEBUG
if text_to_speech_program_path is not None and 'balcon' in text_to_speech_program_path:
    command_parameter_string = "-f {0} -w {1}".format(full_input_path, os.path.abspath(args.o))
    split_command = command_parameter_string.split(" ")
#print(command_parameter_string) # DEBUG
#print(split_command) #DEBUG
if  text_to_speech_program_path is None:
     text_to_speech_program_path = []

# Case 2: Try to convert the video with ffmpeg
if video_program_path is not None and 'balcon' in video_program_path:
    video_parameter_string = "-r 1 -f image2 -s 640x360 -start_number 1 -i pics/%04d.jpg -vframes 1000 -c:v libx264 -crf 15  -pix_fmt yuv420p output.mp4"

# Call() is for P3.4- - you can replace it with run() in 3.5+ for extra functionality - this code is made for Python 3.4.3 the last version supported by Windows XP
program_path_list = [text_to_speech_program_path] # subprocess.call() needs it all to be wrapped with a de-whitespace'd list
try:
#    print([text_to_speech_program_path, command_parameter_string], split_command, ["python", "--version"]) # DEBUG?
    ret_code = subprocess.call(program_path_list + split_command)
    if ret_code == 0:
        print("The text-to-speech program executed successfully.")
    else:
        print("An error occurred with the text-to-speech program, error code: ", ret_code, ". Check if the program is open in another program and close it or use another output file name.")
        sys.exit(1) # Use the code 1 to signal a command-line error
except FileNotFoundError:
    print ("Text-to-speech program file \'{0}\' not found. Exiting.".format(text_to_speech_program_path))
    sys.exit(1) # Use the code 1 to signal a command-line error



