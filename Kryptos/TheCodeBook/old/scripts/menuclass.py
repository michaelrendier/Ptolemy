class Topmenu(Frame):
    
    def __init__(self, master):
        ###Create the menu
        menu = Menu(root)
        root.config(menu=menu)

        ###Create file menu
        filemenu = Menu(menu)
        menu.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='New', command=self.filemenunew)
        filemenu.add_command(label='Open', command=self.filemenuopen)
        filemenu.add_command(label='Save', command=self.filemenusave)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.filemenuexit)

    ###Create file new function
    def filemenunew(self):
        pass
    
    ###Create file open function
    def filemenuopen(self):
        pass

    ###Create file save function
    def filemenusave(self):
        pass
    
    ###Create file exit function
    def filemenuexit(self):
        if tkMessageBox.askokcancel('Quit', 'Do you really wish to quit?'):
            root.destroy()