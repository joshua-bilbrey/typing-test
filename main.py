import tkinter as tk
import math
import requests
import random
from gutenbergpy.gutenbergcache import GutenbergCache
from tkinter import Tk, Label, Text, Button, Canvas, PhotoImage

# one time creation of cache
# GutenbergCache.create()

PINK = '#F4BFBF'
ORANGE = '#FFD9C0'
YELLOW = '#FAF0D7'
DARK_YELLOW = '#EFE6CF'
BLUE = '#8CC0DE'
DARK_BLUE = '#75A9C8'


def get_book():
    book_link = random.choice(links)
    response = requests.get(book_link)
    response.encoding = 'utf-8'
    return response.text


def get_test_words():
    global text
    continue_searching = True
    while continue_searching:
        book_text = get_book()
        clean_text = book_text[3000:-22000]
        for index in range(len(clean_text)):
            if clean_text[index].isupper() and clean_text[index + 1].islower():
                final_text = clean_text[index: index + 2000]
                # check if seems to have simple Enlgish words
                if ' a ' in final_text and 'the' in final_text:
                    # check for no a few special characters that would be hard to type on Enlgish keyboards
                    if 'é' not in final_text and '�' not in final_text and 'ö' not in final_text:
                        # replace characters to make scoring easier and text more readable
                        for item in [['\r\n\r\n', '\n'], ['\r\n', ' '], ['”', '"'], ['“', '"'], ['’', "'"]]:
                            final_text = final_text.replace(item[0], item[1])

                        test_words.config(state='normal')
                        test_words.delete(1.0, tk.END)
                        test_words.insert(1.0, final_text)
                        test_words.config(state='disabled')

                        text = final_text

                        continue_searching = False
                        break


def get_text():
    return typing_area.get(1.0, tk.END).strip('\n')


def focus_in(_):
    if typing_area['foreground'] == 'dark grey' and typing_area['state'] == 'normal':
        typing_area.delete(1.0, tk.END)
        typing_area.config(fg='grey')
    typing_area.focus_set()


def focus_out():
    typing_area.delete(1.0, tk.END)
    typing_area.config(fg='dark grey')
    typing_area.insert(1.0, 'Start Typing Here')


def button_pressed():
    window.focus()
    if button.cget('text') == 'Start' or button.cget('text') == 'Restart':
        result_label.config(text='')
        typing_area.config(state='normal')
        typing_area.focus()
        button.config(text='Stop')
        countdown(60)
        test_words.see(1.0)
        new_text_button.config(state='disabled')
    elif button.cget('text') == 'Stop':
        button.config(text='Start')
        window.after_cancel(timer)
        timer_label.config(text='00:00')

        focus_out()

        typing_area.config(state='disabled')
        new_text_button.config(state='normal')


def key_pressed(event):
    if typing_area['state'] == 'normal':
        typing_length = len(get_text())
        try:
            if text[typing_length - 1] != get_text()[-1]:
                event.widget.tag_add('wrong_letter', 'insert-1c')
            scroll()
        except IndexError:
            pass


def score_wpm():
    number_of_errors = 0
    tag_ranges = list(typing_area.tag_ranges('wrong_letter'))
    while tag_ranges:
        letters = typing_area.get(tag_ranges[0], tag_ranges[1])
        number_of_errors += len(letters)
        tag_ranges.pop(0)
        tag_ranges.pop(0)

    final_text = get_text()
    final_words = final_text.split(' ')
    number_of_words = len(final_words)
    calculated_wpm = number_of_words - round(number_of_errors / 4.7)
    result_text = f'{number_of_words} WPM\n{number_of_errors} Errors\n(≈{calculated_wpm} WPM)'

    result_label.config(text=result_text)


def countdown(count):
    minute = math.floor(count / 60)
    second = count % 60
    if minute < 10:
        minute = f"0{minute}"
    if second < 10:
        second = f"0{second}"

    timer_label.config(text=f"{minute}:{second}")
    if count > 0:
        global timer
        timer = window.after(1000, countdown, count - 1)
    else:
        typing_area.config(fg='dark grey')
        typing_area.config(state='disabled')
        new_text_button.config(state='normal')
        button.config(text='Restart')
        score_wpm()


def scroll():
    line = typing_area.index('end-1c')
    add_value = 225
    base_value = int(line.split('.')[1])
    final_value = add_value + base_value
    index = "1." + str(final_value)
    test_words.see(index)


cache = GutenbergCache.get_cache()
links = cache.native_query('SELECT name FROM downloadlinks WHERE downloadtypeid = 10').fetchall()
links = [link[0] for link in links if '.txt' in link[0]]
timer = None
text = ''


window = Tk()
window.title('Typing Test')
window.geometry('800x600')
window.config(pady=30, padx=30, bg=ORANGE)
window.resizable(False, False)

test_words = Text(window,
                  fg='grey',
                  bg=YELLOW,
                  width=45,
                  height=7,
                  borderwidth=0,
                  font=('Bell Gothic Std Black', 18, 'normal'),
                  wrap='word')

get_test_words()
test_words.config(state='disabled')
test_words.pack(anchor='w')

typing_area = Text(window,
                   fg='dark grey',
                   bg=YELLOW,
                   width=45,
                   height=8,
                   borderwidth=0,
                   font=('Bell Gothic Std Black', 18, 'normal'),
                   wrap='word')
typing_area.insert(1.0, 'Start Typing Here')

typing_area.bind('<FocusIn>', focus_in)
typing_area.tag_config('wrong_letter', foreground=PINK)
typing_area.pack(anchor='w', pady=30)
typing_area.config(state='disabled')

button = Button(window)
button.config(text='Start',
              command=button_pressed,
              borderwidth=0,
              font=('Courier', 18, 'bold'),
              bg=BLUE,
              fg="grey",
              activebackground=DARK_BLUE,
              activeforeground="dark grey",
              height=2,
              width=30)
button.pack()

new_text_button = Button(window)
new_text_button.config(text='New Text',
                       command=get_test_words,
                       borderwidth=0,
                       font=('Courier', 18, 'bold'),
                       bg=YELLOW,
                       fg="grey",
                       activebackground=DARK_YELLOW,
                       activeforeground="dark grey",
                       height=2,
                       width=10)
new_text_button.place(x=0, y=470)

canvas = Canvas(window, width=102, height=124, bg=ORANGE, highlightthickness=0)
clock = PhotoImage(file='clock.png')
canvas.create_image(0, 0, image=clock, anchor='nw')
canvas.place(x=625, y=0)

timer_label = Label(window, fg='grey', bg=BLUE, text='00:00', font=('Courier', 18, 'bold'))
timer_label.place(x=640, y=43)

result_label = Label(window, fg=PINK, bg=ORANGE, text='', font=('Courier', 18, 'bold'))
result_label.place(x=610, y=250)

window.bind('<Key>', key_pressed)

window.mainloop()

# fix checking apostrophes and quotes (text is directional, typing is not)
