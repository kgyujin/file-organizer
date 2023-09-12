import os
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox, Entry, IntVar, StringVar
from tkinter.ttk import Label, Button, Progressbar, Checkbutton
from ttkthemes import ThemedTk

# Define the text for each language.
LANGUAGES = {
    "ENG": {
        "select_dir": "Select Directory",
        "move_files": "Move Files",
        "extensions_placeholder": "Enter extensions (ex: jpg, png)",
        "select_target_folder": "Select Target Folder",
        "include_subfolders": "Include Subfolders",
        'save_log_txt': 'Save Log as .txt',
},
'KOR': {
    'select_dir': '정리할 폴더 선택하기',
    'move_files': '파일 정리하기',
    'extensions_placeholder': 'jpg, png처럼 확장자 입력하기',
    'select_target_folder': '결과 폴더 선택하기',
    'include_subfolders':  '하위 폴더까지 정리하기',
    'save_log_txt':'정리된 내역 log.txt 저장하기'
}
}

def select_directory(label):
    selected_dir = filedialog.askdirectory() 
    label.config(text=selected_dir)
    return selected_dir

def get_files_to_move(source_dir , extensions , include_subfolders):
    if include_subfolders:
        return [os.path.join(root,name)
            for root , dirs , files in os.walk(source_dir)
            for name in files 
            if name.endswith(extensions)]
    
    else:
        return [os.path.join(source_dir,name)
            for name in os.listdir(source_dir) 
            if name.endswith(extensions)]

def move_files(source_label,
                target_label,
                extensions_entry,
                progress,
                include_subfolders=False,
                log_enabled=False):

    source_dir = source_label.cget("text")
    target_dir = target_label.cget("text")
    extensions = tuple(extensions_entry.get().split(', '))
    
    if not source_dir or not target_dir or not extensions:
        messagebox.showinfo("Info", "select path or input extensions.\n파일 경로와 확장자를 입력해주세요.")
        return
    
    files_to_move = get_files_to_move(source_dir , extensions , include_subfolders)

        
    progress['maximum'] = len(files_to_move)

    for i , filepath in enumerate(files_to_move):
        filename = os.path.basename(filepath) # Get the filename from the filepath.
        print(f'Moving {filename}')
        
        # Create a new file name if a file with the same name already exists in the destination directory.
        base_name, ext = os.path.splitext(filename)
        count = 0
        while os.path.exists(os.path.join(target_dir, filename)):
            count += 1
            filename = f"{base_name}_{count}{ext}"
            
        shutil.move(filepath , os.path.join(target_dir,filename))

        progress['value'] = i+1 # update progress bar

	# Save log if the checkbox is checked.
    if log_enabled:
        timestamp_str=datetime.now().strftime('%Y%m%d-%H%M%S')
        with open(os.path.join(target_dir,f'{timestamp_str}_log.txt'), 'a') as f:
            f.write(f'{source_dir}/{filename}\n')

    messagebox.showinfo("Success", "file organizer end.\n파일 정리가 완료되었습니다.")


# Create and configure the main window.
root=ThemedTk(theme="arc")
root.title('File Organizer')  

try:
    root.iconbitmap('file-organizer.ico')
except:
    pass  # Ignore if icon file is not available

language_var = StringVar(value="ENG") 

def toggle_language():
    current_lang = language_var.get()
    new_lang = {"ENG":"KOR", 
                "KOR":"ENG"}[current_lang]
                
    switch_language(new_lang)

lang_button = Button(root,text="KOR",command=toggle_language)
lang_button.grid(row=0,column=0)

source_label=Label(root)
source_button=Button(root,text="정리할 폴더 선택하기", command=lambda : select_directory(source_label))
source_button.grid(row=1,column=0)

source_label.grid(row=2,column=0)

ext_entry=Entry(root,width=30)
placeholder ='jpg, png처럼 확장자 입력하기'
ext_entry.insert(0 , placeholder)
ext_entry['fg'] = 'grey'
def on_focusin(event):
    if ext_entry.get() == placeholder:
        ext_entry.delete(0,"end")
        ext_entry['fg'] = 'black'

def on_focusout(event):
    if not ext_entry.get():
        ext_entry.insert(0 , placeholder)
        ext_entry['fg'] = 'grey'

ext_entry.bind("<FocusIn>", on_focusin)
ext_entry.bind("<FocusOut>",on_focusout )
ext_entry.grid(row=3,column=0)

target_label=Label(root)
target_button=Button(root,text="결과 폴더 선택하기", command=lambda : select_directory(target_label))
target_button.grid(row =4,column =0)

target_label.grid(row =5,column =0)

# Checkboxes for additional options.
subfolder_var=IntVar()
log_var=IntVar()

subfolder_checkbutton = Checkbutton(root,text="하위 폴더까지 정리하기", variable=subfolder_var)
subfolder_checkbutton.grid(row=6,columnspan =2)

log_checkbutton = Checkbutton(root,text="정리된 내역 log.txt 저장하기", variable=log_var)
log_checkbutton.grid(row=7,columnspan=2)

progress = Progressbar(root,length = 200) # Progress bar 추가
progress .grid (row = 8,columnspan = 2)

move_button = Button(
    root,
    text="파일 정리하기",
    command=lambda: move_files(
        source_label, target_label, ext_entry, progress , bool(subfolder_var.get()), log_var.get()
    ),
)
move_button.grid(row=10,columnspan=2)

def switch_language(lang):
    language_var.set(lang)
    
    lang_button.config(text={"ENG":"KOR", 
                            "KOR":"ENG"}[lang]) # Update button text to opposite language
    
    source_button.config(text=LANGUAGES[lang]['select_dir'])
    target_button.config(text=LANGUAGES[lang]['select_target_folder'])

    global placeholder  # Make sure we are modifying the global variable
    if ext_entry.get() == LANGUAGES['ENG']['extensions_placeholder'] or ext_entry.get() == LANGUAGES['KOR']['extensions_placeholder']:
        ext_entry.delete(0,"end")
        placeholder = LANGUAGES[lang]['extensions_placeholder']
        ext_entry.insert(0 , placeholder)

    move_button.config(text = LANGUAGES[lang]['move_files'])

    subfolder_checkbutton.config(text = LANGUAGES[lang]['include_subfolders'])

    log_checkbutton.config(text = LANGUAGES[lang]['save_log_txt'])

switch_language(language_var.get())  # Set initial language for all UI elements

root.mainloop()