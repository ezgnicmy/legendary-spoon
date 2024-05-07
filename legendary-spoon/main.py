# POSSIBLE TODO: Make the command line parameter implementation modular so that it can be used with front ends and software other than balcon and ffmpeg

# The package will be None unless set manually in some cases, which will prevent importing modules i.e. .py files from it
__package__ = "legendary_spoon"


import os
import sys

import logging # Deals with some exception messaging
import subprocess # Implements forking i.e. starting command line processes to do type in the setting parameters in an automated fashion
import random # For generating dynamic slideshows to serve as basic, impromptu footage

# (2) used for getting the length of a .wav audio file
import wave
import contextlib

import argparse # Processes command line parameters

# To allow some simple configuration re-use for lazy people
from configparser import ConfigParser
config = ConfigParser()

def save_setting(config, config_file_path, param_list_s, curr_s_index):
                    tmp = curr_s_index
                    config.read(config_file_path)
                    #print('sections: ', config.sections(), ", config file: ", config_file_path) # DEBUG
                    full_program_path = os.path.abspath(param_list_s[tmp+1]) # Convert the path into a full path
                    if not os.path.exists(full_program_path): # Warn the user in case the file not existing
                        print('Warning - the program file does not exist. The conversion is not likely to work.')
                    if not config.has_section(param_list_s[tmp]):
                        config.add_section(param_list_s[tmp])
                    config.set(param_list_s[tmp], 'TEXT2SPEECH_PROGRAM_PATH', full_program_path)
                    with open(config_file_path, 'w') as f: # This operation blocks disk reads - do not put anything other than writing actions here
                        config.write(f)


# Deals with the -p and -v flags
def check_program(program_param, config_file_path, parser, p_type="undefined"):
        text_to_speech_program_path = None
        if program_param is not None and program_param.lower() is not 'default':
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
                        raise ValueError('Program not found in the given path :', tmp_path)
            except BaseException:
                logging.exception('Exception when processing a save-preset parameter %s', program_param)
        return text_to_speech_program_path

# A subprocess wrapper
# subprocess is the Python equivalent for fork() - has the strange quirks such as 1) requiring command-line strings as whitespace-delimited string list and 2) cannot deal with single quotes i.e. '', meaning you have to use double-quotes "" in the parameter inputs to avoid critical issues with it
def command_line_execute(whitespace_split_command, success_message='The subprocess exited without issues.', failure_message='A failure happened while running'):
        try:
            ret_code = subprocess.call(whitespace_split_command)
            if ret_code == 0:
                print(success_message)
                return ret_code
            else:
                print("Error code \'{}\' with the subprocess parameters {}: {}".format(ret_code, whitespace_split_command, failure_message))
                # sys.exit(1) # Use the code 1 to signal a command-line error
                return ret_code
        except FileNotFoundError:
            print ("The program file \'{0}\' not found. Exiting.".format(whitespace_split_command))
            sys.exit(1) # Use the code 1 to signal a command-line error

# Returns the length of the parameter .wav file, the unit: seconds (int)
def get_wave_file_length(wave_file_path):
        # Get the length of the generated .wav file to fit the slideshow with it
        speech_duration = 0
        try:
            with contextlib.closing(wave.open(wave_file_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                speech_duration = int(frames // rate) + (frames % rate > 0) # Ceil(-ing) i.e. round upwards to the next full integer, uses the formula: int(n // d) + (n % d > 0)
                #print("Duration: ", speech_duration) # DEBUG
        except FileNotFoundError:
            logging.exception('Exception when looking up a wave file duration %s', wave_file_path)
        return speech_duration

# Writes a concat file list for ffmpeg to combine files with
def create_concat_file(image_list, concat_file_name, default_image_duration = 6):
        image_list_concat_string = ""
        try:
            for file_name in image_list:
                image_list_concat_string = image_list_concat_string + 'file \'' + file_name + '\'\nduration ' + default_image_duration + '\n'

            with open(concat_file_name, 'w') as f:
                f.write(image_list_concat_string)
            return 0 # For mons - the exceptions do the heavy lifting
        except BaseException:
            logging.exception('Exception while trying to create a concat file %s', concat_file_name)

# Deletes the files used to generate the video
def remove_listed_files(file_list):
        try:
            for file in file_list:
                os.remove(file)
        except BaseException:
            logging.exception('Exception while deleting the temporary image list file \'%s\'', file)

# Method part end


# A modulizing trick: wrap the whole thing inside a main() function / object, import-friendly, enabling multiple instantiating and using it as a component in other source code
def main():

    # Balcon is the command-line implementation of balabolka, a particularly capable, open-source, text-to-speech software. It uses the Windows Speech API.
    # E.g.:  balcon -i textfile -w output.wav
    
    # Checks and reads the program path from the config file, program_param can be a preset config alias or a full path
    # Possible: add checking for the program type ("text2speech" or "video") # NOT IMPLEMENTED
    # Used by -p and -v flags



    imgDir = None # Stores the directory path to the randomly selected video background pictures
    param_s, param_s_path, param_p, param_i, param_o = (None,)*5 # Mass-initialize a bunch of variables as None - currently UNUSED


    # Initialize the command line parser
    parser = argparse.ArgumentParser(description='Text-to-Video Converter', epilog="For example, type \'python main.py -s balcon FULL_FILE_SYSTEM_PATH_TO_BALCON -i text_for_speech.txt -p balcon -o output.wav\' to produce a computer-voiced audio from the text by utilizing balcon (installed separately)." )

    parser.add_argument("-s", help="Save a program path, syntax PROGRAM_ALIAS PROGRAM_PATH {PROGRAM_ALIAS PROGRAM_PATH}, is read before -p allowing you to immediately use it. You can give multiple -s flags and they will all be processed.", metavar=("PROGRAM_ALIAS", "PROGRAM_PATH"), nargs="*")
    parser.add_argument("-p", action='store', help="The preset program path alias or the full TEXT2SPEECH program path, use -s flag to set a preset", metavar="TEXT2SPEECH_PROGRAM_ALIAS_OR_PATH")
    parser.add_argument("-i", help="The text file used to generate the audio file text-to-speech style from.", metavar="INPUT_FILE")
    parser.add_argument("-v", help="The path to the video generation / converter / rendering program such as ffmpeg, used to put the speech into a video.", metavar="VIDEO_PROGRAM")
    parser.add_argument("-o", default="output.mp4", help="The output file name. Usually defaults to output.[EXT] (.wav and .mp4), depending on the used text-to-speech program.", type=str, metavar="OUTPUT_FILE")
    parser.add_argument("--imgdir", action="store", help="The directory where the images for the image slideshow are..", metavar="IMAGE_DIRECTORY")

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


    # print("s: ", args.s) # DEBUG


    ''' Calculation-effienct ways to generate integers from floating point values when dividing -- n = the value and d = divider:
        -to round down: int(x)
        -to round to the nearest integer: (n + d // 2) // d
        -to round up: int(n // d) + (n % d > 0)
    
        You should not store things as non-integers as they are computationally intesive. For example, it is much faster to process 1377 + 1234 than 1.377 + 1.234 as the decimal part is an approximation using exclusively 1/(2^[-n]) numbers. The approximation introduces nonsense deviations to the number values that cause accurate value checks to unpredictably fail or succeed, especially if you store the approximated value and lock-in the deviation. E.g. in Python 3.4.3 interpreter:
        >>a = 1.1111111111111111; print("a: ", a, ", is a equal to 1.1111111111111111: ", a == 1.1111111111111111);
        a:  1.1111111111111112 , is a equal to 1.1111111111111111:  True
    
        1.1111111111111112 is an approximation of 10 / 9.
    
        So the printed or otherwise outputed values tend to have the conversion errors while the value assignments tend to preserve information of what the original value was. So even if you used a's value to intialize a new variable, it would retain its original number reference without errors. Though if you ever convert floating point numbers to strings i.e. TEXT for storage and such later re-use e.g. for writing them into files, note that the written value might deviate from the original value as it is converted into string. The conversion cuts the connection to the source formula and makes it impossible to validate or correct later. This deviation might become worse if applied to other deviated numbers and the deviation starts growing exponentially every time a relevant float is calculated and re-assigned.
    
        There was a real life incident where the floating point errors led to people dying.    
    
        "On February 25, 1991, during the Gulf War, a Patriot missile defense system let a Scud get through. It hit a barracks, killing 28 people. The problem was in the differencing of floating point numbers obtained by converting and scaling an integer timing register." web.ma.utexas.edu/users/arbogast/misc/disasters.html
    
        Apparently the system had been running for hours, so that the initially neglible number differences grew so high the system could no longer do its job properly. That "scaling" implies multiplication / division calculations that produce those floating point conversion deviations from the intended numbers when reused after converting. It is a number formatting issue, really. If the system regularly samples fresh values instead of relying on old never-updated numbers, critical issues are unlikely. One trick even non-programming mathematicians know to use is to use the complete equations instead of cutting it down to smaller calculations that will multiply the result deviation. It is the storing and the displaying phase that creates the errors, not the calculations themselves.
    
        So as along as you use integers instead of floats whenever you can and do not consider floats acccurate source numbers for comparisons or keep them around for further calculations, you will not have major issues with them. They only become a problem if you repeatedly use them wrong or as accurate valuations instead of the approximations they are.
    
        '''



    # Flag -s: Save preset configurations to the file 'config.ini' because it is an established file name
    # Needs to be processed before the -p flag so that you can utilize the preset converter path immediately and not have to input the path twice
    s_values_set = [] # Tracks and lists the added or changed config preset entries
    if args.s is not None and len(args.s) > 1 and args.s[0] is not None and args.s[1] is not None:
        try:
            # The following line simply divides the param list length by 2 and rounds it down
            for i in range(int(len(args.s) / 2)):
                tmp = i * 2; # A store-only variable, practically a constant. It is there simplify the index parameters and to cut down on redundant calculations
                if os.path.exists(os.path.abspath(args.s[tmp])): # Check out of sync params (here: the alias name) - reject AND do-not-fix behavior
                    print("Error, got a file path - a program alias expected: ", args.s[tmp])
                elif not os.path.exists(os.path.abspath(args.s[tmp+1])): # See above, validating the file system path
                    print("Error, did not get a valid file path param as expected: ", args.s[tmp+1])
                elif args.s[0].lower() is 'default':
                    print('Forbidden alias name detected, do not use \"default\" as your preset alias.')
                else:
                    save_setting(config = config, config_file_path = config_file_path, param_list_s = args.s, curr_s_index = tmp)
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
    # TODO: Possible to add the support for command-line text strings later, as-in stdin or sth, it seems like a clunky idea have unless you have no file access whatsoever
    if args.i is None or not isinstance(args.i, str):
        print("No input parameter given, nothing to do. Type \'python", parser.prog, "--help\' to get a list of commands." )
        sys.exit(1) # Use the code 1 to signal a command-line error
    else:
        full_input_path = os.path.abspath(args.i)
        if not os.path.exists(full_input_path):
            print("Input file not found, exiting.")
            sys.exit(1) # Use the code 1 to signal a command-line error
    ''' # DEBUG_START
    if s_flag_set:
        print("Preset aliases set: ", s_values_set)
    ''' # DEBUG_END
    # print(args) # DEBUG
    #print(parser) # DEBUG

    # Flag -o: Change the output file name when needed - if you do not specify the file extensions, files with the extensions .wav and .mp4 will be generated
    use_default_file_types = False

    chosen_file_name_extension = ".mp4" # The default file type
    available_file_name = None
    tmp = args.o.split('.')
    tmp_all_but_the_last_part = ""
    # Do this assignment now - all recurring positional checks avoided
    tmp_all_but_the_last_part = tmp_all_but_the_last_part + tmp[0]
    # This is mostly to accommodate files like the ones in class libraries where they use dot separators in file names outside the extension part
    for i in range(1, len(tmp)-1):
        tmp_all_but_the_last_part = tmp_all_but_the_last_part + '.' + tmp[i]
    current_file_name_base = ''
    chosen_file_name_base = ''
    if '.' not in args.o or len(tmp) < 1:
        use_default_file_types = True
        chosen_file_name_extension = '.mp4'
        current_file_name_base = args.o # Use the output parameter as-is as it only contains the base file name part and no dot-followed extension
    else:
        chosen_file_name_extension = '.' + tmp[len(tmp)-1]
        current_file_name_base = tmp_all_but_the_last_part
    #    for i in range(len(tmp-1)): # Intentionally leave out the last element - for cases where the user has .'s in the base name part
    #        current_file_name_base = current_file_name_base + tmp[i] + '.'
    #    current_file_name_base = current_file_name_base[:-1] # Remove the last dot, removes the last character from the string
    # Check that the intended file names are not in use and if they are, append numbers at the end until it works
    attempt_limit = 1000 # Eliminate infinite looping
    i = 0 # A stepper variable
    tmp_file_name = None
    # balcon generates .wav files by default
    text_to_speech_audio_file_extension = '.wav'
    # No need to fight file name conflicts - just create a new one and let the user delete the old ones as needed
    print('Current_file_name_base: {}, and chosen_file_name_extension: {}'.format(current_file_name_base, chosen_file_name_extension))
    if os.path.exists(os.path.abspath(current_file_name_base + chosen_file_name_extension)) or os.path.exists(os.path.abspath(current_file_name_base + text_to_speech_audio_file_extension)):
        tmp_file_name = current_file_name_base + '{foo:03d}'.format(foo=i)
        #print("Testing - tmp_file_name: ", tmp_file_name) # DEBUG
        while (os.path.exists(os.path.abspath(tmp_file_name + ".wav")) or os.path.exists(os.path.abspath(tmp_file_name + chosen_file_name_extension))) and i < attempt_limit:
            # Pad the name with zeroes and incremented numbers if the file already exists
            i = i + 1 # i = 1000 would get printed as 1000 despite 03d
            tmp_file_name = current_file_name_base + '{foo:03d}'.format(foo=i)
    else:
        print('Good - this file does not exist yet:', current_file_name_base + chosen_file_name_extension)
        tmp_file_name = current_file_name_base
        


    if i < 1000:
        # There is a special case where the initially suggested name is available
        if tmp_file_name is None:
            tmp_file_name = current_file_name_base
        print("File name selected:", tmp_file_name )
        chosen_file_name_base = tmp_file_name
    else:
        print("Error, could not assign a file name.")
        sys.exit(1) # Use the code 1 to signal a command-line error
    print("The full assigned file name: ", chosen_file_name_base + chosen_file_name_extension)


    # Flag --imgdir: Supplies the image directory path for the video rendering program
    image_directory = os.path.abspath(args.imgdir)
    #print("image_directory: ", image_directory, ", args.imgdir: ", args.imgdir) # DEBUG
    if image_directory is None or not os.path.isdir(image_directory):
        print('Error - {} is not an existing directory.'.format(image_directory))


    # TODO: Let the user set up the program parameters preferably with a graphical front-end with preset common program options
    command_parameter_string = None
    split_command = []
    balcon_output_extension = ".wav"

    # EXPERIMENTAL, to test the command flow, will be replaced later with something more systematic and common-purpose implementation
    # Case 1: Try to test for balcon, you can add other options as elif's 
    #print(text_to_speech_program_path) # DEBUG
    if text_to_speech_program_path is not None and 'balcon' in text_to_speech_program_path:
        command_parameter_string = "-f {0} -w {1}".format(full_input_path, os.path.abspath(chosen_file_name_base + balcon_output_extension))
        split_command = command_parameter_string.split(" ")
    #print(command_parameter_string) # DEBUG
    #print(split_command) #DEBUG
    if  text_to_speech_program_path is None:
        text_to_speech_program_path = []


    # EXPERIMENTAL / PLACEHOLDER implementation here: use ffmpeg and an image directory of the user to create a video slideshow featuring the T2S audio and the images as a slideshow with 10 second duration with each image - repeat the image sequence if the audio is longer than their single-run image durations put together

    ''' Merge videos with the concat protocol
    You can also join videos with the concat protocol. The following code stitches four videos without re-encoding them.

    ffmpeg -f concat -i file.txt -c copy output.mp4

    Options:
    -profile:v baseline -pix_fmt yuv420p
    This makes the produced video playable with a lot of picky video players. If you use PNG pictures, you need to apply -pix_mt yuv420p or equivalent for compatibility, otherwise the generated videos will not be playable outside ffplay

    A useful slideshow command with 640x360 aspect-ratio-preserving padding applied i.e. it shrinks the images a bit while preserving the look by adding black sidebar padding:
    ffmpeg -f concat -i list777.txt -vf "scale=w=640:h=360:force_original_aspect_ratio=1,pad=640:360:(ow-iw)/2:(oh-ih)/2" -t 17 -profile:v baseline -pix_fmt yuv420p roflcopter.mp4
    ''' # COMMENT_END

    # Get a file list with full file paths, excluding the directories - further type checks could pointlessly exclude future file types
    image_list = [os.path.join(image_directory, file) for file in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, file))]

    # Create an -i option for every image file separately - ffmpeg works best that way bc otherwise it will try to apply the same codec for all of the files
    image_input_param_string = ''
    stream_selections = ''
    for i in range(len(image_list)):
        image_input_param_string = image_input_param_string + '-i {} '.format(image_list[i])
        stream_selections = stream_selections + '[{}:v] '.format(str(i))




    # Create a concat file for the images, basically the output file name with a .txt extension, e.g. output074.txt. Consider adding deletion measures later to de-clutter, though it might be bad for troubleshooting as it documents the attempted video generation parameters
    concat_file_extension = '.txt'
    concat_file_name = chosen_file_name_base + concat_file_extension
    image_list_concat_string = ""
    # The duration individual images will be shown on-screen in seconds
    default_image_duration = '6'
    selected_image_duration = default_image_duration

    # Shuffle the list to create varied video slideshow fodder
    random.seed() # Reset the random seed allegedly based on the runtime time
    random.shuffle(image_list)
    
    # Currently not used, probably
    '''
    try:
        for file_name in image_list:
            image_list_concat_string = image_list_concat_string + 'file \'' + file_name + '\'\nduration ' + default_image_duration + '\n'

        with open(concat_file_name, 'w') as f:
            f.write(image_list_concat_string)
    except BaseException:
            logging.exception('Exception while trying to create a concat file %s from the image directory \'%s\'', chosen_file_name_base + '.txt', image_directory)
    '''

    # Create a random sequence of images based on the given image directory


    ''' # DEFUNC
    # Put the randomized image list in the form ffmpeg concat can utilize

    # Try to save conditional checks by adding the first entry separately and then the rest of them prefixed with the '|' AKA pipe or vertical bar
    if len(image_list) > 0:
        image_list_concat_string = image_list_concat_string + image_list[0]
    # In case there are more than one (1) image in the list: add them along with the | prefix
    if len(image_list) > 1: 
        for i in range(1, len(image_list)):
            image_list_concat_string = image_list_concat_string + '|' + image_list[i]
    #print('image_list_concat_string: {}'.format(image_list_concat_string)) #DEBUG and warning - can generate a lot of text
    '''

    # Set video dimensions - e.g. 640x360 (16:9) is the 360p resolution YouTube uses
    video_width = "640"
    video_height = "360"


    # Phase 2: Try to convert the video with ffmpeg
    # EXPERIMENTAL - assumes that the file type extension will be .mp4 - expanding on this would require manipulating the "-c:v libx264" flagging

    # Utilizes concat demuxer of ffmpeg if possible
    video_parameter_string, audio_video_parameter, split_video_command, split_audio_video_command = (None,)*4

    # The following string is something like '-i output.wav'
    text_to_speech_input_option = '-i {} '.format(chosen_file_name_base+text_to_speech_audio_file_extension)

    # Note: subprocess.call() is for P3.4- - you can replace it with run() in 3.5+ for extra functionality - this code is made for Python 3.4.3 the last version supported by Windows XP
    # P3.5+ recommend using subprocess.run() instead as it has more functionality, though that functionality is not backwards compatible
    program_path_list = [text_to_speech_program_path] # subprocess.call() needs it all to be wrapped with a de-whitespace'd list

    # Step #1: Do the T2S 
    #    print([text_to_speech_program_path, command_parameter_string], split_command, ["python", "--version"]) # DEBUG?
    # These subprocess tasks are treated as failure intolerant. You can change this later if you want to make things more failure proof and incorporate alternative solutions
    command_line_execute(whitespace_split_command= program_path_list + split_command, success_message="The text-to-speech program executed successfully.", failure_message='An error occurred with the text-to-speech program. Check if the program is open in another program and close it or use another output file name.')


    # Step #2: Do the video generation
    '''
     Two (2) sub-steps / ffmpeg exexcutions:
     1. Combine as many images matching the format of the initial image as possible. For example, if it is PNG, it will reject all non-PNG images as it cannot do many-to-one conversions.
     2. Combine the generated video-only slideshow video from that one image format variety with the generated text to speech clip and cut it according to the length of the audio.
 
     # TODO?: If this was to be to worked to an insane degree, it would combine things until the file extension change was detected and started a new separate video file while keeping track of the duration to stop once enough footage had been generated. After that, it would combine the video parts into one.
    '''

    wave_file_name = os.path.abspath(chosen_file_name_base + '.wav')
    speech_duration = get_wave_file_length(wave_file_path=wave_file_name)

    # Save the temporary files for later deletion
    temporary_file_list = []
    video_chunk_count = 0
    video_duration_left = int(speech_duration if speech_duration > 0 else 0)
    
    if video_program_path is not None and 'ffmpeg' in video_program_path:
        # Assigns at minimum 0 to the video duration
        #video_parameter_string = "{0}{1}-filter_complex \"{5}[{6}:a] concat=n={2}:v=1:a=1 [v] [a]\" -map \"[v]\" -map \"[a]\" -r 1 -s 640x360 -vframes 1000 -c:v libx264 -crf 15 -profile:v baseline -pix_fmt yuv420p {3}{4}".format(image_input_param_string, text_to_speech_input_option, str(len(image_list)+1), chosen_file_name_base, chosen_file_name_extension, stream_selections, str(len(image_list))) # Just something interesting that was too obscure to get working
        
        # Denote the video-only part with "_video_only", the -an explicitly tells ffmpeg to not include any audio tracks
              
        video_parameter_string = "-f concat -i {0} -vf scale=w={1}:h={2}:force_original_aspect_ratio=1,pad={1}:{2}:(ow-iw)/2:(oh-ih)/2 -t {3} -profile:v baseline -pix_fmt yuv420p -an {4}".format(concat_file_name, video_width, video_height, str(speech_duration), chosen_file_name_base + "_video_only" + chosen_file_name_extension)
        split_video_command = video_parameter_string.split(" ")
        
        audio_video_parameter_string = '-i {} -i {} -c:v copy {}'.format(chosen_file_name_base + "_video_only" + chosen_file_name_extension, wave_file_name, chosen_file_name_base + chosen_file_name_extension)
        split_audio_video_command = audio_video_parameter_string.split(" ")

        # TODO: Change this part to iterate each image segment iteratively so that you generate the video chunks per each image and then combine it
        # Note: This will occasionally break if your images are not of the same type or there are not enough images. Try to have images of the same file type.
        chunk_file_list = []
        if video_parameter_string is not None:
            image_count = len(image_list)
            # Step 1: generate video chunks per image (sidesteps multiple image format issues)
            while(video_duration_left > 0):
                tmp_video_chunk_file_name = str(chosen_file_name_base + "_video_only_" + str(video_chunk_count) + chosen_file_name_extension)
                tmp_current_duration = int(selected_image_duration) if int(selected_image_duration) < int(video_duration_left) else int(video_duration_left)
                video_chunk_command_string = "-i {0} -vf scale=w={1}:h={2}:force_original_aspect_ratio=1,pad={1}:{2}:(ow-iw)/2:(oh-ih)/2 -t {3} -profile:v baseline -pix_fmt yuv420p -an {4}".format( image_list[ video_chunk_count % image_count ], video_width, video_height, str(tmp_current_duration), tmp_video_chunk_file_name)
                split_video_chunk_command = video_chunk_command_string.split(" ")
                # Generates the chunk
                tmp_ret = command_line_execute(whitespace_split_command= [video_program_path] + split_video_chunk_command, success_message="", failure_message="Failed to generate a video chunk.")
                # Add the new file if the chunk generation produces a clean result, else keep it as is
                chunk_file_list = chunk_file_list + [tmp_video_chunk_file_name]
                temporary_file_list = ( temporary_file_list + [tmp_video_chunk_file_name] if tmp_ret == 0 else temporary_file_list )
                video_chunk_count = video_chunk_count + 1
                video_duration_left = video_duration_left - tmp_current_duration
            # Step 1.1: create one extra chunk to sidestep the combatibility issues related to having only one chunk - only VLC and ffplay will play those files i.e. largely non-playable, it is related to how awfully ffmpeg encodes those image-derived video tracks, will probably get cut off anyway
            blank_duration = 1
            blank_chunk_file_name = str(chosen_file_name_base + "_video_only_" + 'blank' + chosen_file_name_extension)
            blank_chunk_command_string = "-f lavfi -i color=c=black:s={0}x{1} -vf scale=w={0}:h={1}:force_original_aspect_ratio=1,pad={0}:{1}:(ow-iw)/2:(oh-ih)/2: -t {2} -profile:v baseline -pix_fmt yuv420p -an {3}".format( video_width, video_height, str(blank_duration), blank_chunk_file_name)
            split_blank_chunk_command = blank_chunk_command_string.split(" ")
            tmp_ret = command_line_execute(whitespace_split_command= [video_program_path] + split_blank_chunk_command, success_message="", failure_message="Failed to generate the blank chunk.")
            # The blank chunk is added to the list of to-be-combined video chunks, eliminating issues with how ffmpeg makes single-image videos
            chunk_file_list = chunk_file_list + [blank_chunk_file_name]
            
            # Step 2: combine the video-only chunks
            # Create the chunk listing file for ffmpeg
            create_concat_file(image_list = chunk_file_list, concat_file_name = concat_file_name, default_image_duration = selected_image_duration)
        
            # The video_only + video + audio stuff
            command_line_execute(whitespace_split_command= [video_program_path] + split_video_command, success_message="The video-only generation program executed successfully.", failure_message="An error occurred with the video rendering program. Check that your image files are of the same file type (especially if you get error 69), if the files are open in another program and close it or use another output file name. Often simply repeating the command will fix the issue as the order it picks images from the directory is randomized each time.")
            command_line_execute(whitespace_split_command= [video_program_path] + split_audio_video_command, success_message="The audio-video generation program executed successfully.", failure_message="An error occurred with the video rendering program. Check that your image files are of the same file type (especially if you get error 69), if the files are open in another program and close it or use another output file name. Often simply repeating the command will fix the issue as the order it picks images from the directory is randomized each time.")

        # Remove the redundant work-in-progress files
        # TODO: Add the temporary file list part and make a function out of it so that it processes the whole list iterartively, saving the file you are currently processing for error reporting
        #print("Deleting the now-redundant files (used to make combine the images into a video) \"{0}\"".format(concat_file_name)) # DEBUG
        # Recycle chunk_file_list as it already has most of the to-be-deleted files listed in it and the rest to it
        chunk_file_list = chunk_file_list + [concat_file_name, str(chosen_file_name_base + text_to_speech_audio_file_extension), str(chosen_file_name_base + "_video_only" + chosen_file_name_extension)]
        # Clean up by removing unnecessary files
        remove_listed_files(chunk_file_list)

        '''
        try:
            os.remove(concat_file_name) # Delete the chunk combination concat file
            #print("A redundant metainformation file {} successfully removed.".format(concat_file_name)) # DEBUG
            os.remove(chosen_file_name_base + "_video_only" + chosen_file_name_extension)
            #print("A redundant video-only file {} successfully removed.".format(chosen_file_name_base + "_video_only" + chosen_file_name_extension)) # DEBUG
            os.remove(chosen_file_name_base + text_to_speech_audio_file_extension) # In case you do not want to use the generated .wav file later in some other place
            #print("A redundant text-to-speech audio file {} successfully removed.".format(chosen_file_name_base + text_to_speech_audio_file_extension)) # DEBUG
        except BaseException:
            logging.exception('Exception while deleting the temporary image list file \'%s\'', concat_file_name)
        '''
           
#    print("__package__ = ", __package__) # Outputs "None"
#    print("__name__ = ", __name__) # Outputs "__main__"
    return 0 # This is useful in case it crashes before reaching this point, i.e. would effectively return None . Copefully.
# END_OF_MAIN - leave the main stuff inside main()

# This structuring prevents the possible script code from being unintentionally executed when importing the module
if __name__ == '__main__':
    import os
    import sys
    sys.exit(main())