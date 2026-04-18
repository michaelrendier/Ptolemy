# play a sound on key press
from Tkinter import *
from pygame import mixer
def on_key(event):
    # detect any normal key press (0..9, A..Z, a..z)
    if event.char == event.keysym:
        if event.char == '1':
            # play the sound instance
            d1.play()
        if event.char == '2':
            d2.play()
prompt = 'Press key 1 or 2 to play a sound'
# initialize the pygame mixer
mixer.init(44100)
# pick sounds you have ...
# copy to working directory or indicate full path
try:
    # create the sound instances
    d1 = mixer.Sound("/usr/share/sounds/purple/alert.wav")
    d2 = mixer.Sound("/usr/share/sounds/purple/logout.wav")
except:
    prompt = "Error: Sound file not found"
root = Tk()
label1 = Label(root, text=prompt, width=len(prompt), bg='yellow', fg='red')
label1.pack()
label1.bind_all('<Key>', on_key)
# start the event loop
root.mainloop()