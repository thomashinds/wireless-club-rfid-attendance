import npyscreen
import signal
import curses
from datetime import datetime

from .json_store import JsonFileStore


class AttendanceSheet(npyscreen.GridColTitles):
    def __init__(self, *args, **kwargs):
        npyscreen.GridColTitles.__init__(self, *args, **kwargs)
        self.col_titles = ["Name", "Cards", "Attendance Count"]
        self.values = []
        self.select_whole_line = True
        self.default_column_number = 3
        db = self.parent.parentApp.database
        for id in db.all_person_ids():
            person = db.find_person_by_id(id)
            name = person.get_name()
            cards = person.get_cards()
            attendance = person.get_attendance()
            row = [
                name,
                "No cards" if len(cards) == 0 else
                ", ".join([hex(x) for x in cards]),
                str(len(attendance)),
                person
            ]
            self.values.append(row)
        self.values.sort(key=lambda x: x[0])

    def set_up_handlers(self):
        npyscreen.GridColTitles.set_up_handlers(self)
        self.handlers[curses.ascii.NL] = self.h_select

    def h_select(self, inpt):
        self.parent.root_menu()


class AttendanceDisplay(npyscreen.FormWithMenus):
    class ExitButton(npyscreen.MiniButtonPress):
        def whenPressed(self):
            self.parent.a_exit()

    FIX_MINIMUM_SIZE_WHEN_CREATED = False
    OK_BUTTON_TEXT = "Exit"
    OKBUTTON_TYPE = ExitButton

    def create(self):
        npyscreen.FormWithMenus.create(self)
        self.wMain = self.add(AttendanceSheet)
        m = self.new_menu()
        m.addItem("View Attendance", self.m_view_att)
        m.addItem("Edit Cards", self.m_not_impl)
        m.addItem("Edit Name", self.m_not_impl)

    def m_view_att(self, *args):
        self.parentApp.getForm("ATTVIEW").value = self.wMain.values[
            self.wMain.edit_cell[0]][3]
        self.parentApp.switchForm("ATTVIEW")

    def m_not_impl(self, *args):
        npyscreen.notify_confirm("This feature hasn't been implemented yet")

    def beforeEditing(self):
        self.handlers["^X"] = lambda *args: None

    def draw_form(self):
        npyscreen.Form.draw_form(self)

    def a_exit(self):
        self.parentApp.switchForm(None)


class AttendanceViewPerson(npyscreen.Form):
    FIX_MINIMUM_SIZE_WHEN_CREATED = False

    def create(self):
        self.value = None
        self.wgAttList = self.add(npyscreen.MultiLineAction,
                                  name="Attendance:")
        self.wgAttList.values = []

    def beforeEditing(self):
        if self.value is not None:
            self.name = "View Attendance For: " + self.value.get_name()
            attendance = self.value.get_attendance()
            self.wgAttList.values = [
                datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                for ts in attendance
            ]
            if len(self.wgAttList.values) == 0:
                self.wgAttList.values = ["<No attendance>"]
        else:
            self.wgAttList.values = ["<No person selected>"]

    def afterEditing(self):
        self.parentApp.switchFormPrevious()


class AttendanceTui(npyscreen.NPSAppManaged):
    def onStart(self):
        self.database = JsonFileStore()
        self.addForm("MAIN", AttendanceDisplay, name="Attendance Database")
        self.addForm("ATTVIEW", AttendanceViewPerson,
                     name="View Attendance Dates")


def sigint(myApp):
    if npyscreen.notify_ok_cancel("Exit?"):
        myApp.switchForm(None)


def main():
    myApp = AttendanceTui()
    signal.signal(signal.SIGINT, lambda *args: sigint(myApp))
    myApp.run()


if __name__ == "__main__":
    main()
