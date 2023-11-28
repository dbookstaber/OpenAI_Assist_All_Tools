"""
Minimal GUI for Assistant that can send files in responses.
"""
import threading
import PySimpleGUI as sg
from assistant import *

# GUI element keys
INPUT = '-INPUT-'
OUTPUT = '-OUT-'+sg.WRITE_ONLY_KEY
STATUS = '-STATUS-'

sg.theme('Dark Blue 3')
sg.Print('STDOUT logged here', do_not_reroute_stdout=False)  # Routes stdout to a "debug" window
layout = [[sg.MLine(key=INPUT, size=(60,2), enter_submits=True), sg.StatusBar("<< Message the Assistant", key=STATUS, size=(27,1)),
            sg.Button('Submit', bind_return_key=True, visible=False)],
          [sg.MLine(key=OUTPUT, size=(120, 30), font=("Courier New",), autoscroll=True, write_only=True, disabled=True)]]


def main():
    window = sg.Window('Assistant Demo', layout)

    AI = Assistant()

    while True:  # Event Loop
        event, values = window.read()
        #print('\n', event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Submit' or event == "Input_Enter":
            message = values[INPUT]
            window[OUTPUT].print('Sending:\n\t' + message, c='blue')
            window[INPUT].Update('')  # Clear the input text
            window[STATUS].Update('')
            threading.Thread(target=AI.send_message, args=(window, message), daemon=True).start()
        elif event == AI_WAIT:
            if not window[STATUS].DisplayText:
                window[STATUS].Update("Waiting for assistant response...")
            else:
                window[STATUS].Update('')
        elif event == AI_RESPONSE:
            window[OUTPUT].print('\n[Received response:]', c='red')
            for m in values[AI_RESPONSE]:
                message_content = m.content[0].text
                window[OUTPUT].print(f"{m.role}: {message_content.value}")

                # Offer to download any files sent by assistant
                for index, annotation in enumerate(message_content.annotations):
                    if (file_path := getattr(annotation, 'file_path', None)):
                        cited_file = AI.client.files.retrieve(file_path.file_id)
                        content = AI.client.files.content(file_path.file_id).read()
                        save_file(cited_file.filename, content)

            window[OUTPUT].print('[End response.]', c='red')
            window[STATUS].Update("<< Message the Assistant")

    window.close()

def save_file(filename, content):
    save_layout = [[sg.Text('Enter a filename:')],
              [sg.Input(filename, key='-IN-'), sg.FileBrowse()],
              [sg.B('Save'), sg.B('Exit Without Saving', key='Exit')]]
    save_window = sg.Window('Assistant Generated File', save_layout)
    while True:
        event, values = save_window.read()
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            break
        elif event == 'Save':
            with open(values['-IN-'], "w" if type(content)==str else "wb") as file:
                file.write(content)
            break
    save_window.close()

if __name__ == '__main__':
    main()
