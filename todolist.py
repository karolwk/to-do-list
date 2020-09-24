from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# initialising the parent class for a table
Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


class ToDoList:
    def __init__(self, db_name: str):
        # Table and database initialising
        engine = create_engine(f'sqlite:///{db_name}.db?check_same_thread=False')
        Base.metadata.create_all(engine)
        # Session and interaction with database initialising
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def add_task(self):
        """Adds task to database"""
        new_row = Table(task=input("Enter task\n"), deadline=datetime.strptime(input("Enter deadline\n"), '%Y-%m-%d'))
        self.session.add(new_row)
        print("The task has been added!\n")
        self.session.commit()

    def choose_action(self, num):
        """Chooses action to do from user input"""
        print()
        actions = {0: lambda: 0,
                   1: lambda: self.print_today_tasks(),
                   2: lambda: self.print_weekly_tasks(),
                   3: lambda: self.print_all_tasks(),
                   4: lambda: self.print_missed_tasks(),
                   5: lambda: self.add_task(),
                   6: lambda: self.delete_task()}
        return actions[num]()

    def delete_task(self):
        """Prints missed tasks and deletes tasks with chosen number"""
        print("Choose the number of the task you want to delete:")
        rows = self.print_missed_tasks(False)
        if rows:
            inp = int(input())
            self.session.delete(rows[inp - 1])
            print("The task has been deleted!")
            self.session.commit()
        else:
            print("Nothing to delete\n")

    def print_today_tasks(self):
        """Prints tasks for today"""
        print(datetime.strftime(datetime.today(), 'Today %d %b'))
        self.print_day_tasks(datetime.today())

    def print_weekly_tasks(self):
        """Prints tasks for one week for each day"""
        today = datetime.today()
        for _ in range(7):
            print(datetime.strftime(today, '%A %d %b'))
            self.print_day_tasks(today)
            today += timedelta(days=1)

    def print_day_tasks(self, today: datetime):
        """Prints all tasks for a day"""
        rows = self.session.query(Table).filter(Table.deadline == today.date()).all()
        if rows:
            for c, row in enumerate(rows, 1):
                print(f'{c}. {row.task}')
        else:
            print("Nothing to do!")
        print()

    def print_all_tasks(self):
        """Prints and returns all tasks from database ordered by date"""
        rows = self.session.query(Table).order_by(Table.deadline).all()
        print('All tasks:')
        self.print_tasks(rows, 'Nothing to do!')
        return rows

    def print_missed_tasks(self, print_msg=True):
        """Prints and returns all tasks whose deadline was missed (date is earlier than today's date)"""
        rows = self.session.query(Table).filter(Table.deadline <= datetime.today().date()).all()
        if print_msg:
            print('Missed tasks:')
        if rows and print_msg:
            self.print_tasks(rows, 'Nothing is missed!')
        elif not rows and print_msg:
            print("Nothing is missed!")
        return rows

    @staticmethod
    def print_tasks(rows, msg):
        """Prints all tasks with %d and %b date format at the end"""
        if rows:
            for c, row in enumerate(rows, 1):
                print(f"{c}. {row.task}. {datetime.strftime(row.deadline, '%d %b')}")
        else:
            print(f"{msg}")
        print()

    @staticmethod
    def print_menu():
        """Prints menu"""
        print("1) Today's tasks\n2) Week's tasks\n3) All tasks\n4) Missed tasks\n5) Add task\n6) Delete task\n0) Exit")

    def main(self):
        while True:
            self.print_menu()
            inp = int(input())
            if self.choose_action(inp) == 0:
                print("Bye!")
                break


if __name__ == "__main__":
    ToDoList('todo').main()
