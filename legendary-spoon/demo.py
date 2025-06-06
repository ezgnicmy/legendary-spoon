

if __name__ == '__main__':
    if __package__ is None: # Enables file loading from subdirectories though not in the root i.e. the main level (main level has no package and cannot be imported from a sub-directory)
        import sys
        import os
#        print("__package__ = ", __package__) # Outputs "None"
#        print("__name__ = ", __name__) # Outputs "__main__"
        #sys.path.append(  os.path.dirname( os.path.dirname(  os.path.abspath(__file__)  )  )  ) # Takes the parent directory from the absolute path
#            import os.path
#        path = os.path.realpath(os.path.abspath(__file__))
#        sys.path.insert(0, os.path.dirname(os.path.dirname(path)))
        from main import main as lg_main # When executed directly
    else:
#        from .. import main as lg_main # Enables module (-m legendary_spoon.demo) loading
        from main import main as lg_main # When imported i.e. used from the main (-level)

    # DEMO TUTORIAL, WILL GUIDE THE USER TO GET IT RUNNING, made to run with Python 3.4.3, though works on later versions. Uses some Python 3 features.
    # How to run: python demo.py

    # Helps you set up custom environment variables so that it does not disturb the operations of any other software
    # Needs the open-source ffmpeg and balcon executables to work its job, you can download them for free, they cannot be included because they use stricter licenses

    '''
    This is intended to be a demo of what the project can do. It does not qualify as a test as it does not aim to cover the functional parts of the project as a whole

    The intended purpose of this file is to show a bit about how and what this project can do and what kind of value it offers in practice.
    '''

import os

import logging # For a slightly fancier error logging
import subprocess # For forking the main script

# To save the last used parameters to reduce the need to re-type stuff
from configparser import ConfigParser
config = ConfigParser()


# For saving last used parameters into a file, the actions are 'r' and 'w', use 'content' variable in cases you just want to assign a name to a value
# Returns the value of the processed variable when successful and probably None if unsuccessful (an error is logged or an exception is raised)
def settings_action(file_name, action, variable , target_section_variable = 'content',  value = None):
            try:
                    if action not in ['r', 'w']:
                        print('Error - action \'{0}\' non-identified - please use \'r\' or \'n\'.'.format(action))
                    config.read(os.path.abspath(file_name))
                    #print('sections: ', config.sections(), ", config file: ", config_file_path) # DEBUG
                    full_value_path = os.path.abspath(value) # Convert the path into a full path
                    if not os.path.exists(full_value_path): # Warn the user in case the file not existing
                        print('Warning - the file \'{}\'does not exist.'.format(full_value_path)) # Allow inserting added-later stuff, hence only a warning text.
                    # Do the rear i.e. 'r' action - read it and return it
                    if action == 'r': # read action
                        if config.has_section(variable):
                            return config.get(variable, target_section_variable)
                        else: # This is the case of reading despite the target not existing, return None to signal it, check_file() method will use it to check for previous values
                            return None
                    # From this point forward: the 'w' action
                    elif not config.has_section(variable):
                        config.add_section(variable)
                    config.set(variable, target_section_variable, full_value_path)
                    with open(file_name, action) as f: # This operation blocks disk reads - do not put anything other than writing actions here
                        if action == 'w': # This should be always true for now - mostly here in case more read-write modes are added
                            config.write(f)
                    return value
            except BaseException:
                logging.exception('Exception when processing the section variable-value pair \'{0}\' = \'{1}\' '.format(variable, value))

# A refactoring of the repetitive user input sequence
# Assume that most people check for files, returns a string of a valid directory or an env value or None if neither is established
# The env var parts are not relied on and they mostly do not work unless this is run from the Python parser because of environment resetting
# Config file values (default file name: demo.ini) are loaded if env vars are not found (the most likely case)
# Re-using env_var_name as a config file variable name
def check_file(file_path, env_var_name, is_file=True, config_file_name = 'demo.ini'):
    # Check if the sys env variable exists and offer to re-use it, else ask for a path and save it as an env variable
    #print('file_path: ' + str(file_path)) # DEBUG
    try:
        if file_path is None:
            tmp_input = None
            solution_list = ['y', 'n']
            tmp_env = os.environ.get(env_var_name) 
            # Note: the following will NEVER get invoked in normal circumstances because of how Python env variables get wiped as soon as the interpreter exits after finishing the script
            # Try to utilize the env variables to minimize repeated typing of identical parameters
            # Fall back to the config file values
            tmp_config_value = settings_action(config_file_name, 'r', env_var_name)
            # print( '\nAfter reading the config file: {0} = {1}'.format( env_var_name, tmp_config_value)) # DEBUG
            tmp_some_value = tmp_env if tmp_env is not None else tmp_config_value
            if tmp_env is not None or tmp_config_value is not None:
                input_msg = '\nFound a previous input value for {0} (\'{1}\') - do you want to use it? (y/n) > '.format(env_var_name, tmp_some_value)
                while (tmp_input not in solution_list):
                    tmp_input = user_input(input_msg).lower()
            # Flow back into the user input prompt if needed OR re-use the value from the environment value and continue onward
            if tmp_input == 'n':
                return None
            else: # The tmp_input == 'y' case
                file_path = tmp_some_value
                return file_path
        # To prevent an unintended flow-through and to repeat the prompt
        if file_path is None:
            return None
        env_value = os.path.abspath(os.environ.get(env_var_name))
        #print('{} and {}'.format(env_var_name, file_path)) # DEBUG
        # Step 1: Check if it is a valid file
        full_path = os.path.abspath(file_path)
        if (os.path.isdir(full_path) and not is_file) or (os.path.isfile(full_path) and is_file):
            # Set and / or update the new valid directory as an env parameter and inform the user , most ineffectual
            os.environ[env_var_name] = full_path
            # Add the new path to the config file
            tmp_config_value = settings_action(config_file_name, 'w', env_var_name, value = full_path)
            #print('{} and {}'.format(env_var_name, file_path)) # DEBUG
#            print('Path accepted accepted. Non-critical environmental variable {0} set to {1}'.format(env_var_name, file_path)) # DEBUG
            print('Path \'{0}\' accepted.'.format(file_path))
            return file_path # Not returning None signals success, return file_path instead of full_path to not confuse the reader with a changed input
        else: 
                print('No valid image directory provided - file_path = {}'.format(file_path))
                #print('Environmental variable {0}, not assigned, {1}'.format(env_var_name, file_path)) #DEBUG
                return None # Will return None upon failure
    except BaseException:
        logging.exception('Exception while set up the directory paths, file_path: {0}, env value {1} = {2}'.format(file_path, env_var_name, env_value))

# Collect command-line stdin from the user, allow mute input_message to make this more valuable to recycle
# If needed to extend with features such as checks or pre-formatting, they could be added here
def user_input(input_message=""):
    return input(input_message) # It can be this simple until more features are needed, a placeholder implementation

# Loops some repetitive check_file checks
def check_loop(file_path, env_variable, input_message, is_file = True):
    while ( file_path is None):
            file_path = check_file(file_path, env_variable, is_file = is_file)
            if file_path is None: #  Do a prompt only if no stored values are found
                file_path = check_file(user_input(input_message), env_variable, is_file = is_file) # Does a user prompt and feeds it into check_file() as a parameter
    return file_path


# Runs a simple demo prompt
def main():

    # The (non-)used custom env variables
    imgdir_env_variable = 'LEGENDARY_SPOON_IMGDIR'
    balcon_path_env_variable = 'LEGENDARY_SPOON_BALCON_PATH'
    ffmpeg_path_env_variable = 'LEGENDARY_SPOON_FFMPEG_PATH'
    voice_env_variable = 'LEGENDARY_SPOON_VOICE'
    
#    print('img evn:' + str(os.environ.get(imgdir_env_variable ))) # DEBUG
#    print('bal evn:' + str(os.environ.get(balcon_path_env_variable ))) # DEBUG
#    print('ff evn:' + str(os.environ.get(ffmpeg_path_env_variable ))) # DEBUG
    
    
    #print('\nWelcome to legendary-spoon the text-to-video generator that incorporates images and computer voice to make videos with minimum excessive effort and thanks for you interest.')
    print('\nWelcome to legendary-spoon the text-to-video generator')
    #print('\nThis is a demo of the video generation tool. It relies on other software and assets, so you need to download and install them for it to work. You need to have balcon and ffmpeg installed in your system. You also need some images to add graphics to the videos. You will get links to all of these.')
    print('\nThis is a demo of the video generation tool. It relies on other software and assets, so you need to download and install them for it to work.')
    print('\n1. If you do not have images already, you can download some from here: https://archive.org/details/2020-random-memes ')
    print('\n2. If you do not have balcon, you can download it from here: https://cross-plus-a.com/bconsole.htm ')
    print('\n3. If you do not yet have ffmpeg installed, you can get it from here: https://ffmpeg.org/download.html')

    image_dir, balcon_path, ffmpeg_path, balcon_voice = (None,)*4

  
    image_dir_input_msg = "\nGive the path of the image directory you want to source images from, unless you have set it earlier (with this prompt or manually with {0} env variable): > ".format(imgdir_env_variable)
  
    image_dir = check_loop(image_dir, imgdir_env_variable, image_dir_input_msg, is_file = False) # Checks for stored values and prompts for a file path if old paths cannot be used

    
#            env_image_dir = os.environ.get(imgdir_env_variable)
#            if os.path.isdir(  os.path.abspath(image_dir)  ):
#                continue
#            elif env_image_dir is not None):
#                image_dir = env_image_dir
#            else:
#                print('No image directory provided.')

    balcon_input_msg = "\nGive the path of the balcon executable you want to use, unless you have set it earlier (with this prompt or manually with {0} env variable): > ".format(balcon_path_env_variable)

    balcon_path = check_loop(balcon_path, balcon_path_env_variable, balcon_input_msg, is_file = True) # A stored path and then a possible prompt
    
    ffmpeg_input_msg = "\nGive the path of the ffmpeg executable you want to use, unless you have set it earlier (with this prompt or manually with {0} env variable): > ".format(ffmpeg_path_env_variable)
    
    ffmpeg_path = check_loop(ffmpeg_path, ffmpeg_path_env_variable, ffmpeg_input_msg, is_file = True) # Stored file and possible a prompt

    balcon_voice_msg = "\nOptionally, input ONE UNIQUE NAME WORD of the voice you want to use or type \'list\' to print a list of all voices or press enter to use the default voice: > "
    balcon_list_command = '{0} -l'.format(balcon_path).split(" ")
    balcon_voice_command = ''
    tmp_voice = '' # Needed in the larger scope to show the parameter value later
    while True:
        tmp_voice = user_input( balcon_voice_msg)
        
        # Cut the name parameter down to one word that balcon expects as a parameter
        tmp_voice0 = tmp_voice
        tmp_voice_split = tmp_voice.split()
        if len(tmp_voice_split) > 0:
            # Take the last word in the voice name string and use it as a balcon voice parameter
            tmp_voice = tmp_voice_split[-1]

        if tmp_voice == 'list':
            subprocess.call(balcon_list_command)
            continue
        elif tmp_voice == '': # Use the default voice
            break
        else:
            balcon_voice_command = ' --voice {}'.format(tmp_voice) # Use whatever the user parameter is
            break

    # Let's see if the variables have changed
    #print('img evn:' + str(os.environ.get(imgdir_env_variable ))) # DEBUG
    #print('bal evn:' + str(os.environ.get(balcon_path_env_variable ))) # DEBUG
    #print('ff evn:' + str(os.environ.get(ffmpeg_path_env_variable ))) # DEBUG

    #print('img param:' + str( image_dir)) # DEBUG
    #print('bal param:' + str( balcon_path)) # DEBUG
    #print('ff param:' + str( ffmpeg_path)) # DEBUG


    if tmp_voice != '':
        print('\nA voice word parameter was given and the word used was: {}'.format(tmp_voice))
    print('\nParameters received, attempting to generate a video with them...')

    # Now use those collected paths to input them into the video generator with subprocess
    # sample_story.txt is provided by the repository

    command_split = 'python main.py -i sample_story.txt -s balcon {} ffmpeg {} -p balcon -v ffmpeg --imgdir {}{}'.format(balcon_path, ffmpeg_path, image_dir, balcon_voice_command).split(" ")

    try:
        subprocess.call(command_split)
    except FileNotFoundError:
            print ("The program file \'{0}\' not found. Exiting.".format(whitespace_split_command))
            sys.exit(1) # Use the code 1 to signal a command-line error

# END_OF_MAIN()

# Main level stuff starts

main()
