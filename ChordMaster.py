from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
import os
from pygame import *
from tkinter import messagebox, font

keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
intervals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
major_scale = [0, 2, 4, 5, 7, 9, 11]
minor_scale = [0, 2, 3, 5, 7, 8, 10]
pitches = []
for i in range(2, 6):
    pitches += [k + str(i) for k in keys]
guitar_pitches = pitches[:pitches.index('F5') + 1]  # C2 ~ F5
harmonics = ['', 'm', 'dim', 'aug', '7', 'M7', 'm7', 'mM7', 'dim7', 'm7(b5)', '6', 'm6', '5']
sus_tones = [0, 2, 4]
add_tones = [0, 2, 9, 11, 13]

guitar_tunes = ['E4', 'B3', 'G3', 'D3', 'A2', 'E2']


class Note:
    def __init__(self, key: str):
        if len(key) > 1 and key[1] == 'b':
            self.key = keys[keys.index(key[0]) - 1]
        else:
            self.key = key

    def __str__(self):
        return self.key

    def __int__(self):
        return keys.index(self.key)

    def __eq__(self, note):
        return self.key == note.key

    def __add__(self, n: int):
        i = keys.index(self.key)
        key = keys[(i + n) % 12]
        return Note(key)

    def __sub__(self, n: int):
        i = keys.index(self.key)
        key = keys[(i - n) % 12]
        return Note(key)

    def get_interval(self, i: int, mode: str = 'Major'):
        r = keys.index(self.key)
        if i > 0:
            n = (i - 1) % 7
        else:
            n = i % 7
        if mode in ['MAJOR', 'Major', 'Maj', 'major']:
            return Note(keys[(r + major_scale[n]) % 12])
        elif mode in ['minor', 'm']:
            return Note(keys[(r + minor_scale[n]) % 12])
        elif mode in ['perfect'] and n in [0, 3, 4]:
            return Note(keys[(r + major_scale[n]) % 12])

    def get_pitched(self, pitch: int):
        return PitchedNote(self.key, pitch)


class PitchedNote(Note):
    def __init__(self, key: str, pitch: int):
        Note.__init__(self, key)
        self.pitch = pitch

    def __str__(self):
        return self.key + str(self.pitch)

    def __int__(self):
        return int(super()) + self.pitch * 12

    def __eq__(self, note):
        return self.key == note.key and self.pitch == note.pitch

    def __add__(self, n: int):
        key = str(super().__add__(n))
        pitch = self.pitch
        if keys.index(key) < keys.index(self.key):
            pitch += 1
        return PitchedNote(key, pitch)

    def __sub__(self, n: int):
        key = str(super().__sub__(n))
        pitch = self.pitch
        if keys.index(key) > keys.index(self.key):
            pitch -= 1
        return PitchedNote(key, pitch)

    def play(self, inst='piano'):
        file = mixer.Sound(f'soundbank/{inst}/{str(self)}.wav')
        mixer.find_channel(True).play(file)


class Chord(Note):
    def __init__(self, key, harmonic: str, sus_tone: int = 0, add_tone: int = 0, inversion: int = 0):
        Note.__init__(self, key)

        if harmonic in ['Maj7', 'maj7', '7M']:
            self.harmonic = 'M7'
        elif harmonic == 'm7M':
            self.harmonic = 'mM7'
        elif harmonic == '+':
            self.harmonic = 'aug'
        else:
            self.harmonic = harmonic

        if self.harmonic in ['', '7', 'M7'] and sus_tone in sus_tones:
            self.sus_tone = sus_tone
        else:
            self.sus_tone = 0

        self.add_tone = 0
        if self.harmonic not in ['aug', 'dim', 'dim7', '5']:
            if add_tone in add_tones:
                if not (sus_tone in [2, 4] and add_tone in [sus_tone, sus_tone+7]):
                    self.add_tone = add_tone

        if self.harmonic == '5':
            self.inversion = 0
        else:
            if inversion > 0:
                self.inversion = inversion
            else:
                self.inversion = 0

        if harmonic.startswith('m') or harmonic.startswith('dim'):
            self.mode = 'minor'
        else:
            self.mode = 'Major'

        self.notes = []  # notes list
        self.root_note = Note(self.key)
        note_list = [self.root_note]

        if self.harmonic == '':
            note_list.append(self.root_note.get_interval(3, 'Major'))  # major 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th
        elif self.harmonic == 'm':
            note_list.append(self.root_note.get_interval(3, 'minor'))  # minor 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th
        elif self.harmonic == 'dim':
            note_list.append(self.root_note.get_interval(3, 'minor'))  # minor 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect') - 1)  # diminished 5th
        elif self.harmonic == 'aug':
            note_list.append(self.root_note.get_interval(3, 'Major'))  # major 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect') + 1)  # augmented 5th
        elif self.harmonic == '7':
            note_list.append(self.root_note.get_interval(3, 'Major'))  # major 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th
            note_list.append(self.root_note.get_interval(7, 'minor'))  # minor 7th
        elif self.harmonic == 'm7':
            note_list.append(self.root_note.get_interval(3, 'minor'))  # minor 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th
            note_list.append(self.root_note.get_interval(7, 'minor'))  # minor 7th
        elif self.harmonic == 'M7':
            note_list.append(self.root_note.get_interval(3, 'Major'))  # major 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th
            note_list.append(self.root_note.get_interval(7, 'Major'))  # major 7th
        elif self.harmonic == 'mM7':
            note_list.append(self.root_note.get_interval(3, 'minor'))  # minor 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th
            note_list.append(self.root_note.get_interval(7, 'Major'))  # major 7th
        elif self.harmonic == 'dim7':
            note_list.append(self.root_note.get_interval(3, 'minor'))  # minor 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect') - 1)  # diminished 5th
            note_list.append(self.root_note.get_interval(7, 'minor') - 1)  # diminished 7th
        elif self.harmonic == 'm7(b5)':
            note_list.append(self.root_note.get_interval(3, 'minor'))  # minor 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect') - 1)  # diminished 5th
            note_list.append(self.root_note.get_interval(7, 'minor'))  # minor 7th
        elif self.harmonic == '6':
            note_list.append(self.root_note.get_interval(3, 'Major'))  # major 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th
            note_list.append(self.root_note.get_interval(6, 'Major'))  # major 6th
        elif self.harmonic == 'm6':
            note_list.append(self.root_note.get_interval(3, 'minor'))  # minor 3rd
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th
            note_list.append(self.root_note.get_interval(6, 'Major'))  # major 6th
        elif self.harmonic == '5':
            note_list.append(self.root_note.get_interval(5, 'perfect'))  # perfect 5th

        if self.sus_tone > 0:
            note_list.remove(note_list[1])
            note_list.insert(1, self.root_note.get_interval(self.sus_tone, 'Major'))

        if self.add_tone > 0:
            note_list.insert(1, self.root_note.get_interval(self.add_tone, 'Major'))

        if 0 < self.inversion < len(note_list):
            inversed_note = note_list[self.inversion]
            note_list.insert(0, inversed_note)
            self.root_note = inversed_note

        for note in note_list:
            if note not in self.notes:
                self.notes.append(note)

    def __str__(self):
        c_name = self.key + self.harmonic
        if self.sus_tone > 0:
            c_name += 'sus' + str(self.sus_tone)
        if self.add_tone > 0:
            c_name += 'add' + str(self.add_tone)
        if self.inversion > 0:
            c_name += '/' + self.root_note.key
        return c_name

    def __eq__(self, chord):
        return self.key == chord.key and self.harmonic == chord.harmonic and self.sus_tone == chord.sus_tone \
               and self.add_tone == chord.add_tone and self.inversion == chord.inversion

    def __add__(self, n: int):
        i = keys.index(self.key)
        key = keys[(i + n) % 12]
        return Chord(key, self.harmonic, self.sus_tone, self.add_tone, self.inversion)

    def __sub__(self, n: int):
        i = keys.index(self.key)
        key = keys[(i - n) % 12]
        return Chord(key, self.harmonic, self.sus_tone, self.add_tone, self.inversion)

    def pitched_notes(self, octave: int = 4):
        first = self.notes[0].get_pitched(octave)
        pitched_note_lst = [first]
        for n in range(1, len(self.notes)):
            if int(self.notes[n]) < int(self.notes[n - 1]):
                octave += 1
            pitched_note_lst.append(self.notes[n].get_pitched(octave))
        return pitched_note_lst


class IntervalChord(Chord):
    def __init__(self, fundamental: Chord, key, harmonic: str, inversion: int = 0):
        self.fundamental = fundamental
        self.semitone = (keys.index(key) - int(fundamental)) % 12
        rebased_key = keys[self.semitone]  # interval key with root C
        Chord.__init__(self, rebased_key, harmonic, 0, 0, inversion)
        if fundamental.mode == 'minor':
            self.interval = minor_scale.index(self.semitone)
        else:
            self.interval = major_scale.index(self.semitone)

    def __str__(self):
        c_name = ''
        if self.mode == 'minor':
            c_name += intervals[self.interval].lower()
        else:
            c_name = intervals[self.interval]
        if self.harmonic.startswith('m'):
            c_name += self.harmonic[1:]
        else:
            c_name += self.harmonic
        return c_name


chords = []  # all possible chords (except for inversion)
for key in keys:
    for harmonic in harmonics:
        chords.append(Chord(key, harmonic))
        if harmonic in ['', '7', 'M7']:
            for sus in sus_tones[1:]:
                chords.append(Chord(key, harmonic, sus_tone=sus))
                for add in add_tones[1:]:
                    if add not in [sus, sus+7]:
                        chords.append(Chord(key, harmonic, sus_tone=sus, add_tone=add))
        if harmonic not in ['aug', 'dim', 'dim7', '5']:
            for add in add_tones[1:]:
                chords.append(Chord(key, harmonic, add_tone=add))


def key_to_interval(chord_lst: list[Chord], root_chord: Chord = None):
    interval_lst = []
    if root_chord is None:
        root_chord = chord_lst[0]
    for c in chord_lst[0:]:
        if c and type(c) == Chord:
            try:
                interval_lst.append(IntervalChord(root_chord, c.key, c.harmonic, c.inversion))
            except:
                interval_lst.append('x')
    return interval_lst


def find_chord(notes: list[str]):
    root_note = notes[0]
    note_lst = []
    for note in notes:
        if note not in note_lst:
            note_lst.append(note)
    note_lst.sort()
    results = []
    sub_results = []
    for chord in chords:
        cnt = 0
        chord_notes = [str(note) for note in chord.notes]
        if root_note in chord_notes:
            chord = Chord(
                chord.key, chord.harmonic, chord.sus_tone, chord.add_tone,
                inversion=chord_notes.index(root_note)
            )
            for n in note_lst:
                if n in chord_notes:
                    cnt += 1
            if cnt == len(note_lst):
                if cnt == len(chord_notes):
                    if chord.inversion == 0:
                        results.insert(0, chord)
                    else:
                        results.append(chord)
                else:
                    sub_results.append(chord)
    if len(results) == 0:
        results = sub_results
    return results


class Player(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.queue = []
        self.delay = IntVar()
        self.delay.set(1000)
        self.root_key = StringVar()
        self.root_mode = StringVar()

        # style configuration
        self.style = ttk.Style(self)
        self.style.theme_use("default")
        self.style.configure(
            "Fret.TCheckbutton",
            padding=10,
            indicatorrelief="flat",
            indicatormargin=-10,
            indicatordiameter=-1,
            relief="raised",
            focusthickness=0,
            highlightthickness=0
        )
        self.style.configure(
            "Fret.TRadiobutton",
            padding=10,
            indicatorrelief="flat",
            indicatormargin=-10,
            indicatordiameter=-1,
            relief="raised",
            focusthickness=0,
            highlightthickness=0,
        )
        self.style.map(
            'Fret.TRadiobutton',
            background=[('disabled', '#dddddd'), ('selected', 'white'), ('active', '#ececec')]
        )
        self.style.map(
            'CB.TCombobox',
            fieldbackground=[('disabled', '#dddddd'), ('readonly', 'white')]
        )

        # GUI settings
        self.title("Chord Master")
        self.geometry("600x280")
        self.resizable(True, True)

        # key bindings

        # menu bar
        mb = Menu(self)

        setting = Menu(mb, tearoff=0)
        setting.add_command(label='종료', command=self.destroy)
        mb.add_cascade(label='설정', menu=setting)

        sounds = Menu(mb, tearoff=0)
        sounds.add_command(label='키올림', command=lambda: self.change_key(1))
        sounds.add_command(label='키내림', command=lambda: self.change_key(-1))
        sounds.add_separator()
        sounds.add_command(label='재생', command=self.play_queue_init)
        sounds.add_command(label='중지', command=self.stop_queue)
        mb.add_cascade(label='코드', menu=sounds)

        tools = Menu(mb, tearoff=0)
        tools.add_command(label='구성음 검색', command=self.note_finder)
        tools.add_command(label='기타 지판', command=self.fretboard_simulator)
        tools.add_command(label='피아노', command=self.piano_simulator)
        tools.add_separator()
        tools.add_command(label='도움말', command=self.helpwindow)
        mb.add_cascade(label='도구', menu=tools)

        self.config(menu=mb)

        # control bar
        self.ctrl_bar = Frame(self, height=1)
        self.ctrl_bar.grid(row=0, column=0, columnspan=10)
        self.b_keyup = Button(self.ctrl_bar, text='반음 올림', height=1, width=8, command=lambda: self.change_key(1))
        self.b_keydown = Button(self.ctrl_bar, text='반음 내림', height=1, width=8, command=lambda: self.change_key(-1))
        self.b_keyup.grid(row=0, column=0)
        self.b_keydown.grid(row=0, column=1)
        self.b_play = Button(self.ctrl_bar, text='▶', height=1, width=3, command=self.play_queue_init)
        self.b_play.grid(row=0, column=2)
        self.b_stop = Button(self.ctrl_bar, text='■', height=1, width=3, command=self.stop_queue)
        self.b_stop.grid(row=0, column=3)
        self.delay_input = Spinbox(self.ctrl_bar, width=6, from_=1, to=5000, increment=10, textvariable=self.delay)
        self.delay_input.grid(row=0, column=4)
        self.label_ms = Label(self.ctrl_bar, text='ms', height=1, width=2)
        self.label_ms.grid(row=0, column=5)

        # text field (key-based)
        self.text_field_kb = Frame(self)
        self.text_field_kb.grid(row=1, column=0, columnspan=30)
        self.text_scroll_kb = Scrollbar(self.text_field_kb)
        self.text_scroll_kb.pack(side=RIGHT, fill=Y)
        self.text_kb = Text(
            self.text_field_kb, height=6, width=60,
            yscrollcommand=self.text_scroll_kb.set,
            font=('Arial', 12,)
        )
        self.text_kb.pack(expand=True, fill=Y)
        self.text_scroll_kb.config(command=self.text_kb.yview)

        # text field (interval-based)
        self.root_select = ttk.Combobox(self, values=[''] + keys, width=3, textvariable=self.root_key)
        self.root_select.grid(row=2, column=0)
        self.mode_select = ttk.Combobox(self, values=['', 'm'], width=2, textvariable=self.root_mode)
        self.mode_select.grid(row=2, column=1)

        self.text_field_ib = Frame(self)
        self.text_field_ib.grid(row=3, column=0, columnspan=100)
        self.text_scroll_ib = Scrollbar(self.text_field_ib)
        self.text_scroll_ib.pack(side=RIGHT, fill=Y)
        self.text_ib = Text(
            self.text_field_ib, height=6, width=60,
            yscrollcommand=self.text_scroll_ib.set,
            font=('Arial', 12,), state=DISABLED
        )
        self.text_ib.pack(expand=True, fill=Y)
        self.text_scroll_ib.config(command=self.text_ib.yview)

    # Note Finder Toplevel
    def note_finder(self):
        chord_vars = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        chord_vars[0].set('C')  # key
        chord_vars[1].set('')  # harmonic
        chord_vars[2].set('0')  # sus tone
        chord_vars[3].set('0')  # add tone
        chord_vars[4].set('0')  # inversion

        notes_txt = StringVar()

        # disable combobox if it is unfit
        def check_option():
            if chord_vars[1].get() in ['', '7', 'M7']:
                sus_select.configure(state="readonly")
            else:
                sus_select.configure(state=DISABLED)
            if chord_vars[1].get() in ['aug', 'dim', 'dim7', '5']:
                add_select.configure(state=DISABLED)
            else:
                add_select.configure(state="readonly")
            if chord_vars[1].get() == '5':
                inversion_select.configure(state=DISABLED)
            else:
                inversion_select.configure(state="readonly")

        # find notes in the searched chord
        def search_notes():
            chord = Chord(
                chord_vars[0].get(), chord_vars[1].get(),
                sus_tone=int(chord_vars[2].get()),
                add_tone=int(chord_vars[3].get()),
                inversion=int(chord_vars[4].get())
            )
            note_list = [str(note) for note in chord.notes]
            notes_txt.set(str(chord) + ': ' + ' '.join(note_list))

        # play chord from the searched notes
        def play_searched_chord():
            mixer.stop()
            search_notes()
            chord = Chord(
                chord_vars[0].get(), chord_vars[1].get(),
                sus_tone=int(chord_vars[2].get()),
                add_tone=int(chord_vars[3].get()),
                inversion=int(chord_vars[4].get())
            )
            self.play_chord(chord, inst='piano', arpeggio=100)

        # append the searched chord to the queue and the text of main window
        def add_chord_to_queue():
            chord = Chord(
                chord_vars[0].get(), chord_vars[1].get(),
                sus_tone=int(chord_vars[2].get()),
                add_tone=int(chord_vars[3].get()),
                inversion=int(chord_vars[4].get())
            )
            self.queue.append(chord)
            self.update_text()

        # Toplevel GUI settings
        window = Toplevel()
        window.geometry('500x120')
        window.title('Note Finder')

        # key bindings
        window.bind('<space>', lambda event: play_searched_chord())

        key_select = ttk.Combobox(
            window, width=3, values=keys, textvariable=chord_vars[0], postcommand=check_option,
            state="readonly", style="CB.TCombobox"
        )
        harmonic_select = ttk.Combobox(
            window, width=6, values=harmonics, textvariable=chord_vars[1], postcommand=check_option,
            state="readonly", style="CB.TCombobox"
        )
        sus_select = ttk.Combobox(
            window, width=2, values=[str(tone) for tone in sus_tones], textvariable=chord_vars[2],
            postcommand=check_option, state="readonly", style="CB.TCombobox"
        )
        add_select = ttk.Combobox(
            window, width=2, values=[str(tone) for tone in add_tones], textvariable=chord_vars[3],
            postcommand=check_option, state="readonly", style="CB.TCombobox"
        )
        inversion_select = ttk.Combobox(
            window, width=4, values=['0', '1', '2', '3'], textvariable=chord_vars[4],
            postcommand=check_option, state="readonly", style="CB.TCombobox"
        )
        label_add = Label(window, text='add')
        label_sus = Label(window, text='sus')
        label_inversion = Label(window, text='inversion:')
        search_button = Button(window, text='검색', command=search_notes)
        play_button = Button(window, text='▶', width=3, command=play_searched_chord)
        plus_button = Button(window, text='+', width=3, command=add_chord_to_queue)
        result_label = Label(window, font=('Arial', 12,), textvariable=notes_txt)
        key_select.grid(row=0, column=0)
        harmonic_select.grid(row=0, column=1)
        label_sus.grid(row=0, column=2)
        sus_select.grid(row=0, column=3)
        label_add.grid(row=0, column=4)
        add_select.grid(row=0, column=5)
        label_inversion.grid(row=0, column=6)
        inversion_select.grid(row=0, column=7)
        search_button.grid(row=0, column=8)
        play_button.grid(row=0, column=9)
        plus_button.grid(row=0, column=10)
        result_label.grid(row=1, column=0, columnspan=11)

    # Guitar Fretboard Simulator Toplevel
    def fretboard_simulator(self):

        fretbuttons = [[], [], [], [], [], []]  # radiobuttons of fretboard

        present_tunes = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        enabled_frets = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        selected_frets = [IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()]

        for f in enabled_frets:
            f.set("O")

        # if the string is disabled(mute), every radio button of fret in the string is disabled
        def check_enabled():
            for i in range(0, 6):
                e = enabled_frets[i].get()
                if e == "X":
                    for j in range(0, 13):
                        fretbuttons[i][j].configure(state=DISABLED)
                elif e == "O":
                    for j in range(0, 13):
                        fretbuttons[i][j].configure(state=NORMAL)

        # play all the marked notes in fretboard
        def play_selected_notes():
            find_suited_chord()
            notes = []
            tunes = []
            for i in range(0, 6):
                if enabled_frets[i].get() == "O":
                    tune = present_tunes[i].get()
                    tunes.append(tune)
                    open_fret = tunes[i]
                    n = keys.index(open_fret[0:-1]) + selected_frets[i].get()
                    note = PitchedNote(keys[n % 12], int(open_fret[-1]) + n // 12)
                    notes.append(note)
                else:
                    tunes.append(None)
            notes.reverse()
            mixer.stop()
            self.play_notes(notes, 0, 100, inst='steel guitar')

        # find appropriate chord from marked notes on fretboard
        def find_suited_chord():
            notes = []
            tunes = []
            for i in range(0, 6):
                if enabled_frets[i].get() == "O":
                    tune = present_tunes[i].get()
                    tunes.append(tune)
                    open_fret = tunes[i]
                    n = keys.index(open_fret[0:-1]) + selected_frets[i].get()
                    key = (keys[n % 12])
                    notes.append(key)
                else:
                    tunes.append(None)
            notes.reverse()
            chord_lst = find_chord(notes)
            chord_listbox.delete(0, END)
            for i in range(len(chord_lst)):
                chord_listbox.insert(i, str(chord_lst[i]))

        # configure every text of radio buttons whenever the tuning(present_tunes) is changed
        def set_tuning():
            tunes = []
            for string in range(0, 6):
                tune = present_tunes[string].get()
                tunes.append(tune)
                open_fret = tunes[string]
                for fret in range(0, 13):
                    n = keys.index(open_fret[0:-1]) + fret
                    pitch = keys[n % 12] + str(int(open_fret[-1]) + n // 12)
                    fretbuttons[string][fret].configure(text=pitch)

        # Toplevel GUI settings
        window = Toplevel()
        window.geometry('720x360')
        window.title('Fretboard')

        # key bindings
        window.bind('<space>', lambda event: play_selected_notes())

        play_button = Button(window, text='▶', width=3, command=play_selected_notes)
        play_button.grid(row=0, column=0)
        search_button = Button(window, text='검색', width=4, command=find_suited_chord)
        search_button.grid(row=0, column=1)
        chord_listbox = Listbox(window, height=5)
        chord_listbox.grid(row=0, column=2)

        fretboard = Frame(window)
        fretboard.grid(row=1, column=0, columnspan=20)
        for string in range(0, 6):
            open_fret = guitar_tunes[string]
            sb = Spinbox(
                fretboard, textvariable=present_tunes[string], values=guitar_pitches,
                width=3, command=set_tuning
            )
            sb.grid(row=string, column=0)
            present_tunes[string].set(open_fret)
            cb = ttk.Checkbutton(
                fretboard, variable=enabled_frets[string], textvariable=enabled_frets[string],
                onvalue="O", offvalue="X", width=2, style="Fret.TCheckbutton", command=check_enabled
            )
            cb.grid(row=string, column=1)
            for fret in range(0, 13):
                n = keys.index(open_fret[0:-1]) + fret
                pitch = keys[n % 12] + str(int(open_fret[-1]) + n // 12)
                rb = ttk.Radiobutton(
                    fretboard, text=pitch, variable=selected_frets[string], value=fret,
                    width=4, style="Fret.TRadiobutton"
                )
                rb.grid(row=string, column=fret + 2)
                fretbuttons[string].append(rb)
        for i in range(0, 13):
            fret_label = Label(fretboard, text=str(i))
            fret_label.grid(row=6, column=i + 2)

    # Piano Simulator Toplevel
    def piano_simulator(self):
        white_keys = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        black_keys = ['C#', 'D#', None, 'F#', 'G#', 'A#', None]
        keybinds = ['z', 's', 'x', 'd', 'c', 'v', 'g', 'b', 'h', 'n', 'j', 'm', ',', 'l', '.', ';', '/',
                    'q', '2', 'w', '3', 'e', '4', 'r', 't', '6', 'y', '7', 'u', 'i', '9', 'o', '0', 'p', '-', '[']

        # Toplevel GUI settings
        window = Toplevel()
        window.geometry('640x260')
        window.title('Piano')

        # key bindings
        for i in range(0, 36):
            pitch = PitchedNote(keys[i % 12], i // 12 + 4)
            window.bind(keybinds[i], lambda event, pitch=pitch: self.play_notes([pitch], 0, 100, inst="piano"))

        keyboard = Frame(window)
        keyboard.grid(row=1, column=0, columnspan=20)
        for i in range(4, 7):
            for j in range(0, 7):
                k = white_keys[j]
                pitch = PitchedNote(k, i)
                key_button = Button(
                    keyboard, width=1, height=5, text=str(pitch), bg='white', activebackground='gray',
                    command=lambda pitch=pitch: self.play_notes([pitch], 0, 100, inst="piano")
                )
                key_button.grid(row=0, column=2 * (j + (i - 4) * 7), rowspan=2, columnspan=2)
        for i in range(4, 7):
            for j in range(0, 7):
                k = black_keys[j]
                if k:
                    pitch = PitchedNote(k, i)
                    key_button = Button(
                        keyboard, width=1, height=3, text=str(pitch), bg='black', activebackground='gray',
                        command=lambda pitch=pitch: self.play_notes([pitch], 0, 100, inst="piano")
                    )
                    key_button.grid(row=0, column=2 * (j + (i - 4) * 7) + 1, rowspan=1, columnspan=2)

    # help window(pop-up)
    def helpwindow(self):
        messagebox.showinfo('도움말',
                            '1. 텍스트 필드에 코드 진행을 작성합니다.\n'
                            '- 코드는 띄어쓰기로 구분하며, \'-\'는 아무것도 재생하지 않는 블럭으로 간주됩니다.\n'
                            '- 코드의 음이름은 대문자로 입력해야 하며, \'b\'는 플랫으로 취급합니다.\n\n'
                            '2. 컨트롤바에서 코드를 조작하거나 재생합니다.\n'
                            '- 반음 올림: 작성한 코드 전체에서 반음 올린 코드로 변환합니다.\n'
                            '- 반음 내림: 작성한 코드 전체에서 반음 내린 코드로 변환합니다.\n'
                            '- 재생: 작성한 코드 진행대로 재생합니다.\n'
                            '- 정지: 재생을 멈춥니다.'
                            '- 재생 속도 설정: 코드를 재생하는 시간 간격을 입력합니다. (정수 밀리초 단위)\n')

    # initiate play_queue from queue[0]
    def play_queue_init(self):
        self.update_queue()
        self.update_text()
        delay = int(self.delay_input.get())
        self.play_queue(0, delay)

    # clear queue and stop mixer
    def stop_queue(self):
        self.queue = []
        mixer.stop()

    # play Chords in queue recursively
    def play_queue(self, n: int, delay: int = 1000):
        if n < len(self.queue):
            try:
                if type(self.queue[n]) is Chord:
                    mixer.stop()
                    self.play_chord(self.queue[n], arpeggio=50)
                elif self.queue[n] == 'x':
                    mixer.stop()
            except self.queue == []:
                pass
            except:
                self.stop_queue()
            finally:
                root.after(delay, lambda: self.play_queue(n + 1, delay))

    # play notes in Chord
    def play_chord(self, chord: Chord, inst='piano', arpeggio: int = 0):
        delay = abs(arpeggio)
        pitched_notes = chord.pitched_notes(octave=4)
        if arpeggio < 0:
            pitched_notes.reverse()
        self.play_notes(pitched_notes, 0, delay, inst=inst)

    # play notes in list recursively
    def play_notes(self, notes: list[PitchedNote], n: int, delay: int, inst='piano'):
        try:
            notes[n].play(inst=inst)
        except:
            messagebox.showerror('Error', f"Failed to play file '{notes[n]}.wav'")
        else:
            n += 1
            if n < len(notes):
                root.after(delay, lambda: self.play_notes(notes, n, delay, inst=inst))

    # change key of all Chord in queue by k
    def change_key(self, k: int):
        self.update_queue()
        q = []
        for c in self.queue:
            if type(c) is Chord:
                r = keys.index(c.key)
                q.append(Chord(keys[(r + k) % 12], c.harmonic, c.sus_tone, c.add_tone, c.inversion))
            elif c == 'x':
                q.append('x')
            elif c == '-':
                q.append(None)
        self.queue = q
        r_key = self.root_key.get()
        if r_key:
            self.root_key.set(keys[(keys.index(r_key) + k) % 12])
        self.update_text()

    # update text from queue
    def update_text(self):
        qtext = []
        for c in self.queue:
            if type(c) is Chord:
                qtext.append(str(c))
            elif c == 'x':
                qtext.append('x')
            elif c is None:
                qtext.append('-')
        self.text_kb.delete('1.0', 'end')
        self.text_kb.insert('1.0', ' '.join(qtext))
        rkey = self.root_key.get()
        rmode = self.root_mode.get()
        if rkey:
            interval_lst = key_to_interval(self.queue, Chord(rkey, rmode))
        else:
            interval_lst = key_to_interval(self.queue)
        interval_lst = [str(i) for i in interval_lst]
        self.text_ib.config(state=NORMAL)
        self.text_ib.delete('1.0', 'end')
        self.text_ib.insert('1.0', ' '.join(interval_lst))
        self.text_ib.config(state=DISABLED)

    # update queue from text
    def update_queue(self):
        q = []
        text = self.text_kb.get('1.0', 'end - 1 chars')
        t_lst = text.split()
        for c in t_lst:
            if c == '-':
                q.append(None)
            elif c == 'x':
                q.append('x')
            else:
                c_sus = None
                c_add = None
                inversed_key = None
                if len(c) > 1 and c[1] in ['#', 'b']:
                    c_key = c[0:2]
                    c = c[2:]
                else:
                    c_key = c[0]
                    c = c[1:]
                if c:
                    if '/' in c:
                        inversed_key = c[c.index('/') + 1:]
                        c = c[:c.index('/')]
                    if 'add' in c:
                        c_add = c[c.index('add') + 3:]
                        c = c[:c.index('add')]
                    if 'sus' in c:
                        c_sus = c[c.index('sus') + 3:]
                        c = c[:c.index('sus')]
                    c_harmonic = c
                else:
                    c_harmonic = ''
                chord = Chord(c_key, c_harmonic, int(c_sus), int(c_add))
                if inversed_key:
                    try:
                        inversion = [str(note) for note in chord.notes].index(inversed_key)
                        chord = Chord(chord.key, chord.harmonic, chord.sus_tone, chord.add_tone, inversion)
                    except:
                        messagebox.showerror('Error', 'Invalid Inversion')
                q.append(chord)
        self.queue = q


init()
mixer.set_num_channels(20)
root = Player()
root.mainloop()
