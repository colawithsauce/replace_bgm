# Replace the BGM of a video.
This program can replace the video's audio-track with randomly played music from user's subdirectories. User can use the file 'script.txt' to control two aspect of the audio generating: which subdirectory and what's the duration it would be played.

For example, if you have this directory hierarchy:

``` sh
$ tree .
.
├── BELLS
├── BGM
└── script.txt

```

And in your `script.txt`:

``` sh
$ cat script.txt
BGM
45
BELLS
10
```

Each two lines is a rule entry, the former line in entry stand for the directory which contains some audio files that you wanna play, and the later line tell the program how long would the music in the directory played in one cycle. It would cycle the entries if the video dosen't end after all entries had comsumed.

# How to use it?
## Installation

``` sh
$ # clone this project or download this project.
$ pip install -r requirements.txt   # install the requirements
```

## Usage
For windows:
1. Make some directories in this project, and place some music you love in this directory.
2. Write `script.txt` in the format I have mentioned above.
3. Drag the video file of which you wanna replace audio track into the icon of file `replace_bgm.bat`, and the result would appear in the directory "./target"

For OSX and Linux:
1. Make some directories in this project, and place some music you love in this directory.
2. Write `script.txt` in the format I have mentioned above.
3. Open Terminal, and type `sh replace_bgm.sh example_video.mkv`, then the result file `target/out_example_video.mkv` would be auto generted. (I have hadn't found a way to do drag-and-drop executing in Linux likes it in Windows. I don't know whether it is supported or not in OSX since I did not have such kind of device :< )
