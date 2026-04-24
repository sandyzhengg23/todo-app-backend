class ReminderSender:
    def send(self, user, task):
        raise NotImplementedError("ReminderSender subclasses must implement send().")


class ConsoleReminderSender(ReminderSender):
    def send(self, user, task):
        print(f"Reminder sent to {user.username}: {task.title}")