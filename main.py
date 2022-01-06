from kivy.app import App
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
# from kivy.uix.image import Image
from kivy.uix.button import Button
# from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, ScreenManagerException, Screen, FadeTransition
from kivy.clock import Clock
from kivy.uix.textinput import TextInput

import sqlite3
from sqlite3 import Error

# from textwrap import dedent
from time import sleep

ARTSAKH_FONT = {
        "name": "Artsakh",
        "fn_regular": "fonts/Artsakh-Font.ttf",
        "fn_bold": "fonts/Artsakh-Font.ttf",
        "fn_italic": "fonts/Artsakh-Font.ttf",
        "fn_bolditalic": "fonts/Artsakh-Font.ttf"
    }
AGHVOR_FONT = {
        "name": "Aghvor",
        "fn_regular": "fonts/davel-aghvor.otf",
        "fn_bold": "fonts/davel-aghvor.otf",
        "fn_italic": "fonts/davel-aghvor.otf",
        "fn_bolditalic": "fonts/davel-aghvor.otf"
    }

LabelBase.register(**ARTSAKH_FONT)
LabelBase.register(**AGHVOR_FONT)

def screen_transaction(self, screen, direction="right"):
    try:
        self.manager.current = screen
    except ScreenManagerException as e:
        print(e)
    
    self.manager.transition.direction = direction


class DBconnection:

    def __init__(self):
    
        db_file = "db/library.db"
        self.table_name = "library"
        sql_create_library_table = """ CREATE TABLE IF NOT EXISTS library (
                                            id integer PRIMARY KEY,
                                            author text NOT NULL,
                                            language text NOT NULL,
                                            genre text,
                                            tags text,
                                            publishing_date text,
                                            notes text
                                        ); """

        # create a database connection
        self.conn = self.create_connection(db_file)

        # create tables
        if self.conn is not None:
            # create projects table
            self.create_table(self.conn, sql_create_library_table)

        else:
            print("Error! cannot create the database connection.")
        

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return conn


    def create_table(self, conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)


    def insert_values(self, author, language, genre, tags, publishing_date, notes):

        insert_into_table_sql = "INSERT INTO {}(author, language, genre, tags, publishing_date, notes) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(self.table_name, author, language, genre, tags, publishing_date, notes)
    
        # print("==")
        # print(insert_into_table_sql)
        
        try:
            c = self.conn.cursor()
            c.execute(insert_into_table_sql)
            self.conn.commit()
        except Error as e:
            print("INSERT ERROR: ", e)


    def show_values(self):

        select_from_table_sql = "SELECT * FROM {}".format(self.table_name)
        table_content = ""
        # return ""
        try:
            c = self.conn.cursor()
            for row in c.execute(select_from_table_sql):
                pass
                # print(row)
                # my_row = ""
                # for i in list(row):
                    # print(str(i))
                    # my_row += " " + str(i)
                table_content += "\n" + str(row) # .strip()
        except Error as e:
            print(e)

        return table_content

class CustomRelativeLayout(RelativeLayout):

    def __init__(self, x_start=0.3, y_start=0.3, margin=0.1):
        super(CustomRelativeLayout, self).__init__()
        
        self.x = x_start
        self.y = y_start + margin
        self.margin = margin
        self.first_label_len = None
        self.widgets = {}
    
    def add_entry(self, widget_id, multiline_text_input=False):
    
        if self.first_label_len is None:
            self.first_label_len = len(widget_id)
    
        self.y = self.y - self.margin
        label_x_margin = (self.first_label_len - len(widget_id)) * 0.01
        text_input_width = 0.06
        if multiline_text_input:
            text_input_width = 0.12

        label = Label(
            text=widget_id.replace("_", " "),
            font_name='fonts/davel-aghvor.otf',
            font_size=30,
            pos_hint={"center_x": self.x + label_x_margin, "center_y": self.y},
            size_hint=(0.2, 0.15)
            )
        
        text_input = TextInput(
            hint_text='Enter {}'.format(widget_id.replace("_", " ")),
            font_name='Aghvor',
            pos_hint={'center_x': self.x + 0.2, 'center_y': self.y},
            size_hint=(0.25, text_input_width),
            multiline=multiline_text_input
            )
        
        self.add_widget(label)
        self.add_widget(text_input)
        
        self.widgets[widget_id] = {
            "label": label,
            "text": text_input
        }
        
        return label, text_input

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.rel_layout = RelativeLayout()

        with self.canvas.before:
            self._rect = Rectangle(size=self.size, pos=self.pos, source="Images/Library.jpg")

        self.bind(size=self._update_rect, pos=self._update_rect)


        self.my_library_label = Label(
            text="L I B R A R Y",
            font_name='Aghvor',
            font_size=40,
            pos_hint={"center_x": .5, "center_y": .8}
            )

        self.add_book_button = Button(
            text="Add Book",
            background_normal='',
        	background_color=(.94, .35, .13, 1),
			font_name='fonts/davel-aghvor.otf',
			font_size=30,			
			pos_hint={ "center_x": .5, "center_y": .6},
			size_hint=(0.2, 0.15),
            on_release=lambda *x: screen_transaction(self, "add_book", "right")
            )

        self.find_book_button = Button(
            text="Find Book",
            background_normal='',
        	background_color=(.14, .12, .13, .95),
			font_name='fonts/davel-aghvor.otf',
			font_size=27,			
			pos_hint={ "center_x": .5, "center_y": .4},
			size_hint=(0.2, 0.15),
            on_release=lambda *x: screen_transaction(self, "find_book", "left")
            )

        self.rel_layout.add_widget(self.my_library_label)
        self.rel_layout.add_widget(self.add_book_button)
        self.rel_layout.add_widget(self.find_book_button)
        self.add_widget(self.rel_layout)


    def _update_rect(self, instance, value):
        self._rect.pos = instance.pos
        self._rect.size = instance.size


class AddBook(Screen):
    def __init__(self, **kwargs):
        super(AddBook, self).__init__(**kwargs)       
        # self.rel_layout = RelativeLayout()
        self.rel_layout = CustomRelativeLayout(x_start=0.3, y_start=0.85, margin=0.1)
        
        self.library_db = DBconnection()

        with self.canvas.before:
            self.background_color = (.94, .35, .13, 0.98)
            self._color = Color(*self.background_color)
            # self._rect = Rectangle(size=self.size, pos=self.pos, source="Images/Library.jpg")
            self._rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        # self.author_label = Label(
            # text="Author",
            # font_name='fonts/davel-aghvor.otf',
            # font_size=30,
            # pos_hint={"center_x": .3, "center_y": .65},
            # size_hint=(0.2, 0.15)
            # )
        
        # self.author = TextInput(
            # hint_text='Enter Author',
            # font_name='Aghvor',
            # pos_hint={'center_x': .5, 'center_y': .65},
            # size_hint=(0.25, 0.06),
            # multiline=False
            # )
            # # on_text=lambda *x: process_input(self.author)

        # self.lang_label = Label(
            # text="Language",
            # font_name='fonts/davel-aghvor.otf',
            # font_size=30,
            # pos_hint={"center_x": .27, "center_y": .55},
            # size_hint=(0.2, 0.15)
            # )
        
        # self.lang = TextInput(
            # hint_text='Enter Language',
            # pos_hint={'center_x': .5, 'center_y': .55},
            # size_hint=(0.25, 0.06),
            # multiline=False,
        # )

        # self.genre_label = Label(
            # text="Genre",
            # font_name='fonts/davel-aghvor.otf',
            # font_size=30,
            # pos_hint={"center_x": .3, "center_y": .45},
            # size_hint=(0.2, 0.15)
            # )
        
        # self.genre = TextInput(
            # hint_text='Enter Genre',
            # pos_hint={'center_x': .5, 'center_y': .45},
            # size_hint=(0.25, 0.06),
            # multiline=False,
        # )

        # self.tags_label = Label(
            # text="Tags",
            # font_name='fonts/davel-aghvor.otf',
            # font_size=30,
            # pos_hint={"center_x": .29, "center_y": .35},
            # size_hint=(0.2, 0.15)
            # )
        
        # self.tags = TextInput(
            # hint_text='Enter Tags',
            # pos_hint={'center_x': .5, 'center_y': .35},
            # size_hint=(0.25, 0.06),
            # multiline=False,
        # )

        # self.author.bind(text=lambda *x: self.process_input(self.author))
        # self.lang.bind(text=lambda *x: self.process_input(self.lang))

        self.main_info_button = Button(
            text="Add",
            background_normal='',
        	background_color=(.0, 0.83, .0, 1),
			font_name='Aghvor',
			font_size=25,			
			pos_hint={ "center_x": .45, "center_y": .20},
			size_hint=(0.12, 0.086),
            on_release=self.submit_main_info
            )
        
        self.back_button = Button(
            text="",
            background_normal="Images/back.png",
            background_color=(1,1,1,1),
			font_name='Aghvor',
			font_size=15,			
			pos_hint={ "center_x": .05, "center_y": .96},
			size_hint=(0.11, 0.09),
            on_release=self.back_to_main_menu
            )
        

        # self.author_label, self.author = self.rel_layout.add_entry("Author")
        # self.lang_label, self.lang = self.rel_layout.add_entry("Language")
        # self.genre_label, self.genre = self.rel_layout.add_entry("Genre")
        # self.tags_label, self.tags = self.rel_layout.add_entry("Tags")
        # self.publishing_date_label, self.publishing_date = self.rel_layout.add_entry("Publishing Date")
        # self.notes_label, self.notes = self.rel_layout.add_entry("Notes", multiline_text_input=True)
        
        self.rel_layout.add_entry(widget_id="Author")
        self.rel_layout.add_entry(widget_id="Language")
        self.rel_layout.add_entry(widget_id="Genre")
        self.rel_layout.add_entry(widget_id="Tags")
        self.rel_layout.add_entry(widget_id="Publishing_Date")
        self.rel_layout.add_entry(widget_id="Notes", multiline_text_input=True)
        
        self.rel_layout.add_widget(self.main_info_button)
        self.rel_layout.add_widget(self.back_button)
        self.add_widget(self.rel_layout)

    def submit_main_info(self, _):
        all_widgets = self.rel_layout.widgets 
        valid = True
        entry_values = {}
        for entry in all_widgets:
            entry_value = all_widgets[entry]['text'].text.strip()
            all_widgets[entry]['text'].background_color = (1, 1, 1 , 1)
            
            if not entry_value:
                all_widgets[entry]['text'].background_color = (.99, .04, 0 , 1)
                valid = False

            entry_values[entry.lower()] = entry_value
        
        if not valid:
            return

        self.library_db.insert_values(**entry_values)
        # return
        self.library_db.show_values()
        self.back_to_main_menu(None)
        

    def back_to_main_menu(self, _):
        for widget_id in self.rel_layout.widgets:
            self.rel_layout.widgets[widget_id]["text"].text = ""

        screen_transaction(self, "main", "right")
    
    def _update_rect(self, instance, value):
        self._color.rgba = instance.background_color
        self._rect.pos = instance.pos
        self._rect.size = instance.size
    

class FindBook(Screen):
    def __init__(self, **kwargs):
        super(FindBook, self).__init__(**kwargs)
    
        self.library_db = DBconnection()

        self.lay = RelativeLayout()
    
        self.back_button = Button(
            text="",
            background_normal="Images/back.png",
            background_color=(1,1,1,1),
			font_name='Aghvor',
			font_size=15,			
			pos_hint={ "center_x": .05, "center_y": .96},
			size_hint=(0.11, 0.09),
            on_release=self.back_to_main_menu
            )
    
        self.label = TextInput(
            text="AAA",
            font_name='fonts/davel-aghvor.otf',
            font_size=30,
            size_hint=(0.8, 0.7),
            pos_hint={ "center_x": .4,  "center_y": .16},
            multiline=True
            )
    
        self.lay.add_widget(self.back_button)
        self.lay.add_widget(self.label)
        self.add_widget(self.lay)
    
    def back_to_main_menu(self, _):
        self.label.text = self.library_db.show_values()
        # sleep(10)
        screen_transaction(self, "main", "right")

class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)

# kv = Builder.load_file("WindowManager.kv")

class LibraryApp(App):
    def build(self):
        sm = WindowManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AddBook(name='add_book'))
        sm.add_widget(FindBook(name='find_book'))
        return sm

    def process(self):
        # print(dir(self.root.ids))
        text = self.root.ids.items() # .author.text
        print(text)
    
    

if __name__ == "__main__":
    LibraryApp().run()
