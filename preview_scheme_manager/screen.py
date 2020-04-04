import npyscreen
from preview_scheme_manager.terminal_config import WindowsTerminalConfigFile
import subprocess


# This application class serves as a wrapper for the initialization of curses
# and also manages the actual forms of the application

class SchemeManager(npyscreen.NPSAppManaged):
    def onStart(self):
        # npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.config_file = WindowsTerminalConfigFile()
        self.config = self.config_file.reload()
        self.registerForm("MAIN", SchemeListForm(self.config_file))
        # self.registerForm("Testing", OtherForm(self.config))

class SchemeList(npyscreen.MultiLineAction):
    def __init__(self, *args, **kwargs):
        self.config_file = WindowsTerminalConfigFile()
        self.config = self.config_file.config
        super().__init__(*args, **kwargs)

    def actionHighlighted(self, scheme_name, key_press):
        self.config.set_scheme(scheme_name)
        self.config_file.write()
        if key_press == 32: #space-bar
            self.h_cursor_line_down(32) # no idea if I'm supposed to put the key-code here but it works?
        title = self.parent._widgets_by_id[0]
        title.value = self.config.get_current_scheme()
        title.display()


class SchemeListForm(npyscreen.Form):
    def __init__(self, config):
        self.config_file = config
        self.config = self.config_file.config
        super().__init__()

    def create(self):
        self.add(npyscreen.TitleFixedText, name = "Current Scheme:", value=self.config.get_current_scheme(), max_width=40)
        self.add(SchemeList, name = "Scheme List", values=self.config.schemes(), max_height=None, max_width=30)

    def afterEditing(self):
        self.parentApp.setNextForm(None)