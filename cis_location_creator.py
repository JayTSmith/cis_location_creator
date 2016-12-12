# Filename: cis_location_creator.py
# Author: Justin Smith
# Date: 12/08/16

'''
CHANGELOG:

1.1 - Added more internal documentation
      Fixed an issue where an image wouldn't display on the first open'''

from PIL import Image
import json
import tkinter as tk
import tkinter.ttk as ttk

VERSION_NUMBER = 1.1


class Application(tk.Tk):
    
    def __init__(self):
        global VERSION_NUMBER
        
        super(Application, self).__init__()
        self.title('CIS Location Creator {}'.format(VERSION_NUMBER))

        # These data values are used within the program for certain reasons that could be bad if modified.
        self._data = {}
        self._lastIndex = 0

        # This serves as a placeholder for the image of the currently selected location
        self.activeImage = None
        
        self.create_widgets()
        
    def create_widgets(self):
        '''Creates the widgets used by the program and sets them up for use in the
           proper functions and such.'''

        selected_neighbors = {'n':tk.StringVar(),
                              'e':tk.StringVar(),
                              'w':tk.StringVar(),
                              's':tk.StringVar(),
                              'u':tk.StringVar(),
                              'd':tk.StringVar(),}

        def _update_connections_menus():
            '''Updates all of the menus to allow selection of any new neighbor
               ids added to the data file.'''
            #Clear all of the menus
            locationNorthInput['menu'].delete(0, tk.END)
            locationEastInput['menu'].delete(0, tk.END)
            locationWestInput['menu'].delete(0, tk.END)
            locationSouthInput['menu'].delete(0, tk.END)
            locationUpInput['menu'].delete(0, tk.END)
            locationDownInput['menu'].delete(0, tk.END)

            # A tuple of the actual dropdowns and the key of its associated key
            optionMenus = ( (locationNorthInput, 'n'),
                            (locationEastInput, 'e'),
                            (locationWestInput, 'w'),
                            (locationSouthInput, 's'),
                            (locationUpInput, 'u'),
                            (locationDownInput, 'd'))

            for menu in optionMenus:
                menu[0]['menu'].add_command(label='', command=tk._setit(selected_neighbors[menu[1]],
                                                                        ''))
                for connection in locationListBox.get(0, tk.END):
                    menu[0]['menu'].add_command(label=connection, command=tk._setit(selected_neighbors[menu[1]],
                                                                                 connection))

        def add_location():
            '''Adds a new id into the listbox for the user and
               adds a new entry into the data directory for the program.'''
            
            idNumber = '{0}'.format(len(list(self._data.keys())))
            newLocation = {idNumber: {'img': '',
                                      'connections':{'n':'',
                                                     'e':'',
                                                     'W':'',
                                                     's':'',
                                                     'u':'',
                                                     'd':''},
                                      'description':'',
                                      'shortDescription':'',
                                      'terrain':'',
                                      'monsterChance':'0',
                                      'randomTreasureChance':'0',
                                      'dungeonChance':'0'}}
            self._data.update(newLocation)
            locationListBox.insert(tk.END, idNumber)

        def browse_location_image():
            '''Opens a dialog box to allow the user to browse their computer for an image
               If the dialog is given a proper path, the image will be moved to a subdirectory called images.'''
            from tkinter.filedialog import askopenfilename
            from shutil import copy
            import os

            acceptedTypes = (('Image Files', '*.gif *.bmp'),)
            rawFilePath = askopenfilename(filetypes=acceptedTypes)

            if rawFilePath:
                try:
                    os.makedirs('./images/')
                except OSError:
                    pass
                
                if os.path.relpath(os.path.dirname(rawFilePath)) != 'images':
                    copy(rawFilePath, './images/')

                newFilePath = os.path.relpath(os.path.join('./images', os.path.basename(rawFilePath)))

                locationImgInput.delete(0, tk.END)
                locationImgInput.insert(0, newFilePath)    
                display_location_image()

        def display_location_image():
            self.activeImage = tk.PhotoImage(file=locationImgInput.get())
            scaleW = int(round(self.activeImage.width() / 100))
            scaleH = int(round(self.activeImage.height() / 100))
            self.activeImage = self.activeImage.subsample(scaleW, scaleH)
            locationPreviewLabel.configure(image=self.activeImage)

        def display_location_info(event):
            try:
                # Saves the current location before switching indicies
                save_location()
                
                self._lastIndex = locationListBox.curselection()[0]
                curLocation = self._data[locationListBox.get(self._lastIndex)]

                # Clear out the input fields
                locationImgInput.delete(0, tk.END)
                locationTerrainInput.delete(0, tk.END)
                locationLongDescription.delete('0.0', tk.END)
                locationShortDescription.delete('0.0', tk.END)
                locationMonsterSpinner.delete(0, tk.END)
                locationRandomTreasureSpinner.delete(0, tk.END)
                locationDungeonSpinner.delete(0, tk.END)

                # Reset the connections
                for var in selected_neighbors.values():
                    var.set('')

                # Insert the location's data into the Entry
                locationCurrentIdLabel['text'] = locationListBox.get(self._lastIndex)
                locationImgInput.insert(0, curLocation['img'])
                locationTerrainInput.insert(0, curLocation['terrain'])
                locationLongDescription.insert('0.0', curLocation['description'])
                locationShortDescription.insert('0.0', curLocation['shortDescription'])
                locationMonsterSpinner.insert(0, curLocation['monsterChance'])
                locationRandomTreasureSpinner.insert(0, curLocation['randomTreasureChance'])
                locationDungeonSpinner.insert(0, curLocation['dungeonChance'])

                display_location_image()

                _update_connections_menus()
                
            except KeyError:
                pass

        def delete_location():
            '''Removes a location from the listbox and from the program's internal database.'''
            self._data.pop(locationListBox.get(self._lastIndex))
            locationListBox.delete(self._lastIndex)
            _update_connections_menus()

        def save_location():
            '''Updates a location within the program's internal database.'''
            try:
                curLocation = self._data[locationListBox.get(self._lastIndex)]
                curLocation['img'] = locationImgInput.get()
                curLocation['description'] = locationLongDescription.get('0.0', tk.END)
                curLocation['shortDescription'] = locationShortDescription.get('0.0', tk.END)
                curLocation['terrain'] = locationTerrainInput.get()
                curLocation['monsterChance'] = locationMonsterSpinner.get()
                curLocation['randomTreasureChance'] = locationRandomTreasureSpinner.get()
                curLocation['dungeonChance'] = locationDungeonSpinner.get()
            except KeyError:
                print('No data currently exists.')
            
        def save():
            '''Exports a datafile containing the data contained in the variable self._data.
               The datafile's name is locations.json and it is in the current directory of the script.'''
            import json
            
            with open('locations.json', 'w+') as data_file:
                json.dump(self._data, data_file, indent=4)

        def load():
            '''Tries to load locations.json into the program from the current directory.

               If it fails, it will print a message to console explaining the reason for failure.'''
            try:
                with open('locations.json', 'r') as data_file:
                    self._data = json.load(data_file)
            except FileNotFoundError:
                print('location.json doesn\'t exist.')
            except PermissionError:
                print('Invalid permissions!')
            except ValueError:
                print('locations.json is empty.')

            # Empties the listbox of the program and repopulate it with the entries in the datafile.
            locationListBox.delete(0, tk.END)
            for key in self._data.keys():
                locationListBox.insert(tk.END, key)

        # Creates the menubar
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Save    Ctrl+S', command=save)
        filemenu.add_command(label='Load', command=load)
        filemenu.add_command(label='Quit', command=self.destroy)
        menubar.add_cascade(label='File', menu=filemenu)

        # Adds the menusbar to the Application
        self.config(menu=menubar)

        # Configures the row to evenly on both sides
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # This frame is stuck to the left side of the window
        leftSideFrame = tk.Frame(self)
        leftSideFrame.rowconfigure(1, weight=1)
        leftSideFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)

        # Adds another location into the listbox and gives the id
        # that is based off the current number of entries
        locationAddBtn = tk.Button(leftSideFrame, text='Add Location', command=add_location)
        locationAddBtn.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)

        # Serves as the method of selection for the end-user
        locationListBox = tk.Listbox(leftSideFrame)
        locationListBox.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W+tk.S,)

        # This frame is stuck to the right side of the window
        rightSideFrame = tk.Frame(self)
        rightSideFrame.columnconfigure(1, weight=1)
        rightSideFrame.rowconfigure(7, weight=1)
        rightSideFrame.grid(row=0, column=1, sticky=tk.N+tk.E+tk.W+tk.S)

        # The following widgets are used to control the current locations data
        # entiries that are usually the second word in the identifer.
        locationIdLabel = tk.Label(rightSideFrame, text='ID: ')
        locationIdLabel.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
        locationCurrentIdLabel = tk.Label(rightSideFrame, text='')
        locationCurrentIdLabel.configure(relief=tk.RIDGE)
        locationCurrentIdLabel.grid(row=0, column=1, columnspan=2, sticky=tk.N+tk.E+tk.W+tk.S)

        locationImgLabel = tk.Label(rightSideFrame, text='Image source: ')
        locationImgLabel.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
        locationImgInput = tk.Entry(rightSideFrame)
        locationImgInput.grid(row=1, column=1, sticky=tk.N+tk.E+tk.W+tk.S)
        locationBrowseButton = tk.Button(rightSideFrame, text='Browse', command=browse_location_image)
        locationBrowseButton.grid(row=1, column=2, sticky=tk.N+tk.E+tk.W+tk.S)

        locationTerrainLabel = tk.Label(rightSideFrame, text='Terrain: ')
        locationTerrainLabel.grid(row=2, column=0, sticky=tk.N+tk.E+tk.W+tk.S)
        locationTerrainInput = tk.Entry(rightSideFrame)
        locationTerrainInput.grid(row=2, column=1, columnspan=2, sticky=tk.N+tk.E+tk.W+tk.S)

        locationMonsterLabel = tk.Label(rightSideFrame, text='Monster Chance: ')
        locationMonsterLabel.grid(row=3, column=0)
        locationMonsterSpinner = tk.Spinbox(rightSideFrame, to=100, from_=0)
        locationMonsterSpinner.grid(row=3, column=1, columnspan=2, sticky=tk.E+tk.W)

        locationRandomTreasureLabel = tk.Label(rightSideFrame, text='Random Treasure Chance: ')
        locationRandomTreasureLabel.grid(row=4, column=0)
        locationRandomTreasureSpinner = tk.Spinbox(rightSideFrame, to=100, from_=0)
        locationRandomTreasureSpinner.grid(row=4, column=1, columnspan=2, sticky=tk.E+tk.W)

        locationDungeonLabel = tk.Label(rightSideFrame, text='Dungeon Chance: ')
        locationDungeonLabel.grid(row=5, column=0)
        locationDungeonSpinner = tk.Spinbox(rightSideFrame, to=100, from_=0)
        locationDungeonSpinner.grid(row=5, column=1, columnspan=2, sticky=tk.E+tk.W)

        locationPreviewLabelFrame= tk.LabelFrame(rightSideFrame, text='Preview of Location Image')
        locationPreviewLabelFrame.columnconfigure(0, weight=1)
        locationPreviewLabelFrame.grid(row=6, column=0, columnspan=3, sticky=tk.N+tk.E+tk.W+tk.S, pady=1)
        locationPreviewLabel = tk.Label(locationPreviewLabelFrame, image=self.activeImage)
        locationPreviewLabel.grid(sticky=tk.E+tk.W)

        # Contains the details of the location such as description and travel
        locationDetailsNotebook = ttk.Notebook(rightSideFrame)
        locationDetailsNotebook.grid(row=7, column=0, columnspan=3, sticky=tk.N+tk.E+tk.W+tk.S, pady=1)

        locationLongDescription = tk.Text(locationDetailsNotebook)
        locationLongDescription.grid(sticky=tk.N+tk.E+tk.W+tk.S)
        locationDetailsNotebook.add(locationLongDescription, text='Description')

        locationShortDescription = tk.Text(locationDetailsNotebook)
        locationShortDescription.grid(sticky=tk.N+tk.E+tk.W+tk.S)
        locationDetailsNotebook.add(locationShortDescription, text='Short Description')
        
        locationConnectionFrame = tk.Frame(locationDetailsNotebook)
        locationConnectionFrame.columnconfigure(0, weight=1)
        locationConnectionFrame.columnconfigure(1, weight=1)
        # Configure every row to space out evenly
        for i in range(6):
            locationConnectionFrame.rowconfigure(i, weight=1)
        locationConnectionFrame.grid()

        # Creates the labels and dropdowns that tell the current connections to other locations
        locationNorthLabel = tk.Label(locationConnectionFrame, text='North: ')
        locationNorthLabel.grid(row=0, column=0)
        locationNorthInput = tk.OptionMenu(locationConnectionFrame, selected_neighbors['n'], [])
        locationNorthInput.grid(row=0, column=1)

        locationSouthLabel = tk.Label(locationConnectionFrame, text='South: ')
        locationSouthLabel.grid(row=1, column=0)
        locationSouthInput = tk.OptionMenu(locationConnectionFrame, selected_neighbors['s'], [])
        locationSouthInput.grid(row=1, column=1)

        locationEastLabel = tk.Label(locationConnectionFrame, text='East: ')
        locationEastLabel.grid(row=2, column=0)
        locationEastInput = tk.OptionMenu(locationConnectionFrame, selected_neighbors['e'], [])
        locationEastInput.grid(row=2, column=1)

        locationWestLabel = tk.Label(locationConnectionFrame, text='West: ')
        locationWestLabel.grid(row=3, column=0)
        locationWestInput = tk.OptionMenu(locationConnectionFrame, selected_neighbors['w'], [])
        locationWestInput.grid(row=3, column=1)

        locationUpLabel = tk.Label(locationConnectionFrame, text='Up: ')
        locationUpLabel.grid(row=4, column=0)
        locationUpInput = tk.OptionMenu(locationConnectionFrame,selected_neighbors['u'], [])
        locationUpInput.grid(row=4, column=1)

        locationDownLabel = tk.Label(locationConnectionFrame, text='Down: ')
        locationDownLabel.grid(row=5, column=0)
        locationDownInput = tk.OptionMenu(locationConnectionFrame, selected_neighbors['d'], [])
        locationDownInput.grid(row=5, column=1)
        
        locationDetailsNotebook.add(locationConnectionFrame, text='Connections')

        # Creates the buttons that control the saving and deleting of the location
        locationSaveButton = tk.Button(rightSideFrame, text='Save this location!', command=save_location)
        locationSaveButton.grid(row=8, column=0, columnspan=3, sticky=tk.E + tk.W)
        locationDeleteButton = tk.Button(rightSideFrame, text='Delete this location!', command=delete_location)
        locationDeleteButton.grid(row=9, column=0, columnspan=3, sticky=tk.E + tk.W)

        locationListBox.bind('<<ListboxSelect>>', display_location_info)
        self.bind('<Control-s>', lambda e: save())
        self.bind('<F7>', lambda e: print(self.winfo_height(), self.winfo_width()))

        # Called mainly because the program can act strangely if this function is not called
        _update_connections_menus()
        

if __name__ == '__main__':
    app = Application()
    app.geometry('500x600')
    app.mainloop()
