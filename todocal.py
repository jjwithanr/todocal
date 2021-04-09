# Tkinter class structure
import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import *
import sqlite3 as sq
import GoogleCal

"""
Ideas:
- extended selection
- two listboxes with input tasks and scehduled tasks in another color font
    - seperate sign-in and schedule button
        - don't allow schedule button when not signed in
    - transition to that from the pop out selected window
- add the footer showing whether the user is signed in
- change time check (default: 1 week)
- QA test for scheduling (friday doesn't scheulde past the weeeknd problem?)
"""

class Scheduler(tk.Frame):
    def __init__(self, root, task):
        tk.Frame.__init__(self, root)
        self.root = root
        self.task = task
        self.selected = []
        self._draw()

    def show_tasks(self):
        self.Tasks.delete(0,'end')
        for i in self.task: self.Tasks.insert('end', i)

    def get_selected(self):
        self.selected = [self.task[i] for i in self.Tasks.curselection()]
        self.selectWindow.destroy()
        self.schedule_event()

    def open_task_selection(self) -> list:
        # Create new window
        self.selectWindow = tk.Toplevel(self.root)
        self.selectWindow.title("Choose tasks to schedule")
        self.selectWindow.geometry("400x300")
        icon = tk.PhotoImage(file="todo-icon.png")
        self.selectWindow.iconphoto(False, icon)
        # Window widgets
        scrollbar = tk.Scrollbar(self.selectWindow)
        scrollbar.pack(side="right", fill = "both")
        self.Tasks = tk.Listbox(self.selectWindow, height=11, width=30, font=font.Font(size=15), selectmode=tk.EXTENDED)
        self.Tasks.pack(fill=tk.BOTH, expand=True)
        self.Tasks.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command=self.Tasks.yview)
        # ! add warning for no selected tasks?
        self.close_bio_btn = tk.Button(self.selectWindow, text="Confirm", width=25, command=self.get_selected)
        self.close_bio_btn.pack(side=tk.TOP, pady=5)

        self.show_tasks()
        return self.selected

    def schedule_event(self):
        # ? move spinbox to selectedWindow?
        # ? add footer saying what Google account signed into.
        # ! sign-in button and schedule button? 

        def getAvailability() -> dict:
            # Get time from spinboxes and convert to string
            s = self.start_hour.get() + ":" + self.start_min.get() + self.start_clock12hr.get()
            e = self.end_hour.get() + ":" + self.end_min.get() + self.end_clock12hr.get()
            if not (s and e):
                messagebox.showerror("Error", "Invalid time range")
                return {}
            # Convert string into datetime time objects
            start = datetime.strptime(s, "%I:%M%p").time()
            end = datetime.strptime(e, "%I:%M%p").time()
            if start >= end:
                messagebox.showerror("Error","Invalid time range")
                return {1:1}
            else:
                # * insert setting for time duration here
                return GoogleCal.schedule_time(start, end, time_duaration=7)

        if not self.task:
            # Must have a task to schedule task
            messagebox.showinfo('Cannot schedule', 'Add a task')
        else:
            # Check busyness and find available date
            scheduled_times = getAvailability()
            if scheduled_times == {1:1}: return 0
            elif scheduled_times:
                # All tasks are in the description
                # NOTE: can use settings for single select task scheduling? this is default ...
                GoogleCal.create_event(scheduled_times["start"], scheduled_times["end"], description="\n".join(self.selected) if self.selected else "\n".join(self.task))
                started = scheduled_times["start"].strftime("%I:%M%p")
                ended = scheduled_times["end"].strftime("%I:%M%p")
                date = scheduled_times["end"].strftime("%b %d")
                messagebox.showinfo("Sucess", "Created event from " + started + " to " + ended + " on " + date)
            else:
                messagebox.showinfo("Failure", "You are unavailable during this time")

    def _draw(self):
        scheduleFrame = tk.Frame(master=self.root)
        scheduleFrame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=False)
        calendarLabel = ttk.Label(scheduleFrame, text='Schedule Time:')
        calendarLabel.pack(side=tk.LEFT, padx=5)

        # Spinboxes to pick time
        self.start_hour = ttk.Spinbox(master=scheduleFrame, from_=1,to=12, wrap=True, width=3, state="readonly")
        self.start_hour.set(4)
        self.start_hour.pack(side=tk.LEFT, padx=5)
        self.start_min = ttk.Spinbox(master=scheduleFrame, from_=0,to=59, wrap=True, width=3, state="readonly")
        self.start_min.set(0)
        self.start_min.pack(side=tk.LEFT, padx=5)
        self.start_clock12hr = ttk.Spinbox(master=scheduleFrame, values=("AM", "PM"), wrap=True, width=3)
        self.start_clock12hr.set("PM")
        self.start_clock12hr.pack(side=tk.LEFT, padx=5)
        bufferLabel = tk.Label(scheduleFrame, text="to")
        bufferLabel.pack(side=tk.LEFT, padx=5)
        self.end_hour = ttk.Spinbox(master=scheduleFrame, from_=1,to=12, wrap=True, width=3, state="readonly")
        self.end_hour.set(6)
        self.end_hour.pack(side=tk.LEFT, padx=5)
        self.end_min = ttk.Spinbox(master=scheduleFrame, from_=0,to=59, wrap=True, width=3, state="readonly")
        self.end_min.set(0)
        self.end_min.pack(side=tk.LEFT, padx=5)
        self.end_clock12hr = ttk.Spinbox(master=scheduleFrame, values=("AM", "PM"), wrap=True, width=3)
        self.end_clock12hr.set("PM")
        self.end_clock12hr.pack(side=tk.LEFT, padx=5)

        # Callback to create event for desired time
        scheduleBtn = ttk.Button(scheduleFrame, text='Confirm', width=10, command=self.open_task_selection)
        scheduleBtn.pack(side=tk.LEFT, padx=5)

class View(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self._draw()
    
    def _draw(self):
        scrollbar = tk.Scrollbar(self.root)
        scrollbar.pack(side="right", fill = "both")
        viewFrame = tk.Frame(master=self.root)
        viewFrame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=10, pady=10)
        self.viewTasks = tk.Listbox(viewFrame, height=11, width = 30, font=font.Font(size=15), selectmode=tk.SINGLE)
        self.viewTasks.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.viewTasks.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command=self.viewTasks.yview)
        self.viewTasks.config(selectmode=tk.SINGLE)

        # ? Add a scheduled tasks view? shows which ones are already assigned with its date next to it?


class MainApp(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self._init_database()
        self._draw()

    def addTask(self):
        word = self.entry.get()
        if len(word)==0:
            messagebox.showinfo('Empty Entry', 'Enter task name')
        else:
            self.task.append(word)
            self.cur.execute('insert into tasks values (?)', (word,))
            self.listUpdate()
            self.entry.delete(0,'end')

    def listUpdate(self):
        self.clearList()
        for i in self.task:
            self.view.viewTasks.insert('end', i)

    def delOne(self):
        try:
            val = self.view.viewTasks.get(self.view.viewTasks.curselection())
            print("TEST TEST ***", val)
            if val in self.task:
                self.oldTasks.append(val)
                self.task.remove(val)
                self.listUpdate()
                self.cur.execute('delete from tasks where title = ?', (val,))
        except:
            messagebox.showinfo('Cannot Delete', 'No Task Item Selected')

    def deleteAll(self):
        mb = messagebox.askyesno('Delete All','Are you sure?')
        if mb == True:
            while(len(self.task) != 0):
                deleted = self.task.pop()
                self.oldTasks.append(deleted)
            self.cur.execute('delete from tasks')
            self.listUpdate()

    def undoTask(self):
        try:
            word = self.oldTasks.pop()
            self.task.append(word)
            self.cur.execute('insert into tasks values (?)', (word,))
            self.listUpdate()
        except:
            messagebox.showerror("Error", "Nothing to undo")

    def clearList(self):
        self.view.viewTasks.delete(0,'end')

    def bye(self):
        self.root.destroy()

    def retrieveDB(self):
        while(len(self.task) != 0):
            self.task.pop()
        for row in self.cur.execute('select title from tasks'):
            self.task.append(row[0])

    def _init_database(self):
        self.conn = sq.connect('todo.db')
        self.cur = self.conn.cursor()
        self.cur.execute('create table if not exists tasks (title text)')
        self.task = []
        self.oldTasks = []
        self.oldIndex = 0

    def _draw(self):
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_settings = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(menu=menu_settings, label='Settings')
        # Change from 1 week to up to 1 month
        # ! time settings


        # Change from all tasks in description to single select task and make that the title
        menu_settings.add_command(label="Schedule Preferences")

        # Add buttons
        buttonFrame = tk.Frame(master=self.root, width=50)
        buttonFrame.pack(fill=tk.BOTH, side=tk.LEFT, padx=10)
        todoLabel = ttk.Label(buttonFrame, text = 'To-Do List')
        todoLabel.pack(pady=7)
        taskLabel = ttk.Label(buttonFrame, text='Enter task title: ')
        taskLabel.pack(pady=5)
        self.entry = ttk.Entry(buttonFrame, width=21)
        self.entry.pack(pady=5)
        addBtn = ttk.Button(buttonFrame, text='Add task', width=20, command=self.addTask)
        addBtn.pack(pady=5)
        delBtn = ttk.Button(buttonFrame, text='Delete', width=20, command=self.delOne)
        delBtn.pack(pady=5)
        clearBtn = ttk.Button(buttonFrame, text='Delete all', width=20, command=self.deleteAll)
        clearBtn.pack(pady=5)
        undoBtn = ttk.Button(buttonFrame, text='Undo delete', width=20, command=self.undoTask)
        undoBtn.pack(pady=5)
        exitBtn = ttk.Button(buttonFrame, text='Exit', width=20, command=self.bye)
        exitBtn.pack(pady=5)

        self.scheduler = Scheduler(self.root, self.task)
        self.view = View(self.root)

        self.retrieveDB()
        self.listUpdate()
        self.root.mainloop()
        self.conn.commit()
        self.cur.close()


if __name__ == "__main__":
    root = tk.Tk()
    root.title('ToDo Cal')
    icon = tk.PhotoImage(file="todo-icon.png")
    root.iconphoto(False, icon)
    root.geometry("650x280")
    root.configure(bg="#d6d6d6")
    root.minsize(650, 280)

    MainApp(root)