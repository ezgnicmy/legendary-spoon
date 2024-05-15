# legendary-spoon

Makes a video based on minimum inputs and user interaction

In practice, it can generate a simple yet somewhat configurable slideshow video with text-to-speech audio from a text file and an image directory in about 30 seconds or less. That is when using the current configuration of balcon (T2S) and ffmpeg (video compositing). It is a way more useful than spending minutes doing it by hand and praying that the video editor does not crash.

## Functionality

A text file (input) -> a command line text-to-speech program (customizable, e.g. balcon i.e. a command-line version of balabolka )
+
a image directory for generation for generating the slideshow + the T2S audio -> ffmpeg (video-audio compositing)
-> a video slideshow with the T2S audio track that should play without issues on most players and get accepted to video hosting platforms

The design is so that one could later expand it to support arbitrary parameters and software as it is mostly just a pass-through to the command-line software that generate the audio and video. The best way to implement that would be to add a smart configuring tool that would either extract the parameters needed straight from the source program or to use a text-file-based scheme where the user could specify the command-line passing template for an arbitrary program. The goal would be to make it as simple as editing a configuration file and so that the user-side could update the specifications to match its needs and the changes.

This project is spec'd for Python 3.4.3 (released February 25th, 2015) i.e. the last version that officially supports Windows XP. It should work with later versions. Just look up "python download" and you will probably find what you need.

## How to use

This is integration software, so it relies on the user installing and setting up certain programs and input files beforehand. You need certain free resources:

0) As a Python project, you need the Python to run the script. You can get one from here: https://www.python.org/downloads/ . On Windows, it is recommended to pick the installer version if you do not want to set the PATH environment variable by hand so that the system can find the python executables without having to type full paths every single time.
1) balcon (the currently used text-to-speech command-line software), available at: https://cross-plus-a.com/bconsole.htm
2) ffmpeg (video compositing), downloadable from: https://ffmpeg.org/download.html
3) A text file to input into the T2S. sample_text.txt has been provided for you among the sources. The easiest way to produce a similar text files for testing is to say something to an AI chat bot such as ChatGPT and saving the response.
4) A directory with image files (for creating a slideshow, defaulting to a random image selection order). You can get the required placeholder image set from here: https://archive.org/details/2020-random-memes

- demo.py has all this information and a bunch of helpful input prompts, so it is a bit easier for getting the feel of what this software does.

All the needed stuff is in maain.py - it only uses built-in stuff. demo.py and sample_story.txt are a part of the demonstartion. Note that the order of the parameter flags (the - and -- braced words) does not have to follow the given order. Here is the minimal commands for running them.

demo.py:
python demo

- It incorporates a user input prompt with a save feature, so you have to input the minimum parameters only once and it will save them for you for later use. No repeated typing needed. 

main.py:
python -p BALCON_PATH -i TEXT_FILE -v FFMPEG_PATH --imgdir IMGDIR_PATH

- For example, you could have a Windows setup with the following line working from the source directory:
  python main.py -p D:\balcon\balcon.exe -i sample_text.txt -v D:\ffmpeg\ffmpeg.exe --imgdir D:\pictures

- This will generate a file called output.mp4 if no critical errors were encountered. If something goes wrong and the processing does not seem to end (e.g. if you supply image file types that ffmpeg sucks at processing), you can abort the process any time by pressing CTRL + C. Please note that this might leave behind a lot of temporary files as they are removed only if the processing completes without issues. The rule of thumb is that .JPG and .PNG files are fine while stuff like .GIF might cause major issues. You can always try converting to other file formats to see if it changes things.

The images are re-scaled in a clever way that maintains the proportions by adding black bars padding to the sides. In short, the images will be as big and centered they can without stretching. It does it automatically based on on the dimensions of the individual picture, so you do not have to prepare the pictures in any way.

## The command listing

usage: main.py [-h] [-s [PROGRAM_ALIAS [PROGRAM_PATH ...]]]

               [-p TEXT2SPEECH_PROGRAM_ALIAS_OR_PATH] [-i INPUT_FILE]
               
               [-v VIDEO_PROGRAM] [-o OUTPUT_FILE] [--imgdir IMAGE_DIRECTORY]
               
               [--resolution WIDTHxHEIGHT] [--animation]
               
               [--imgduration IMAGE_DURATION] [--voice VOICE_NAME_PARTIAL]

Text-to-Video Converter

optional arguments:

  -h, --help            show this help message and exit
  
  -s [PROGRAM_ALIAS [PROGRAM_PATH ...]]
  
                        Save a program path, syntax PROGRAM_ALIAS PROGRAM_PATH                        
                        {PROGRAM_ALIAS PROGRAM_PATH}, is read before -p                        
                        allowing you to immediately use it. You can give                        
                        multiple -s flags and they will all be processed.
                        
  -p TEXT2SPEECH_PROGRAM_ALIAS_OR_PATH
  
                        The preset program path alias or the full TEXT2SPEECH                        
                        program path, use -s flag to set a preset
                        
  -i INPUT_FILE         
  
                        The text file used to generate the audio file text-to-  
                        speech style from.
                        
  -v VIDEO_PROGRAM 
  
                        The path to the video generation / converter /  
                        rendering program such as ffmpeg, used to put the                        
                        speech into a video.
                        
  -o OUTPUT_FILE        
  
                        The output file name. Usually defaults to output.[EXT]  
                        (.wav and .mp4), depending on the used text-to-speech                        
                        program.
                        
  --imgdir IMAGE_DIRECTORY
  
                        The directory where the images for the image slideshow                        
                        are..
                        
  --resolution WIDTHxHEIGHT
  
                        Set the video resolution (default: 640x360)
                        
  --animation           
  
                        Enable to switch off random image order.
  
  --imgduration IMAGE_DURATION
  
                        The time in seconds a single image is shown before the                        
                        next one
                        
  --voice VOICE_NAME_PARTIAL
  
                        The name the voice chosen for the text-to-speech

For example, type 'python main.py -s balcon FULL_FILE_SYSTEM_PATH_TO_BALCON -i
text_for_speech.txt -p balcon -o output.wav' to produce a computer-voiced
audio from the text by utilizing balcon (installed separately).
END_OF_HELP

- This is might not be up to date. You check yours by typing:
python main.py --help


## Spare ideas

1. Using recorded audio as the audio track instead of text

## Demo video

https://www.youtube.com/watch?v=BZ7CwPpXuvs 
