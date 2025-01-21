import rumps
import time
import os

'''
Antonio Leon
01/21/2025
MBT for MacOS
v. 2.0
'''

class TimerApp(rumps.App):
    def __init__(self):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        self.history_file = os.path.join(script_directory, "timer_history.txt")
        icon_path = os.path.join(script_directory, "sandClock2.png")
        super(TimerApp, self).__init__("Timer", icon=icon_path)
        self.timer = rumps.Timer(self.update_timer, 1)
        self.start_time = None
        self.remaining_time = None
        self.is_running = False

        # Set up menu
        self.menu = [
            rumps.MenuItem("Set Custom Time", callback=self.set_custom_time),
            None,
            rumps.MenuItem("Quick Timers"),
            None,
            rumps.MenuItem("⏸ Pause", callback=self.pause_timer),
            rumps.MenuItem("▶ Resume", callback=self.resume_timer),
            rumps.MenuItem("⏹ Stop", callback=self.stop_timer),
            None
        ]

        # Add submenu for Quick Timers
        self.menu["Quick Timers"].add(rumps.MenuItem("5 Minutes", callback=lambda _: self.start_timer(5 * 60)))
        self.menu["Quick Timers"].add(rumps.MenuItem("10 Minutes", callback=lambda _: self.start_timer(10 * 60)))
        self.menu["Quick Timers"].add(rumps.MenuItem("30 Minutes", callback=lambda _: self.start_timer(30 * 60)))

        self.update_menu_state()

    def update_timer(self, sender):
        elapsed_time = time.time() - self.start_time
        remaining_time = max(0, self.remaining_time - elapsed_time)
        minutes = int(remaining_time / 60)
        seconds = int(remaining_time % 60)
        time_str = "{:02d}:{:02d}".format(minutes, seconds)
        self.title = time_str

        if remaining_time == 0:
            self.timer.stop()
            self.is_running = False
            self.log_event("Timer Finished")
            rumps.notification(title="Timer Expired", subtitle="Time is up!", message="")
            self.update_menu_state()

    @rumps.clicked("Set Custom Time")
    def set_custom_time(self, _):
        response = rumps.Window(
            title="Set a Custom Timer",
            message="Enter time in minutes:",
            default_text="10",
            ok="Start Timer",
            cancel="Cancel",
            dimensions=(220, 50)
        ).run()

        if response.clicked:
            try:
                minutes = int(response.text.strip())
                if minutes > 0:
                    self.start_timer(minutes * 60)
                else:
                    rumps.alert(
                        title="❌ Invalid Input ❌",
                        message="Please enter a positive number greater than 0."
                    )
            except ValueError:
                rumps.alert(
                    title="❌ Invalid Input ❌",
                    message="Please enter a valid whole number."
                )

    def pause_timer(self, _):
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            elapsed_time = time.time() - self.start_time
            self.remaining_time -= elapsed_time
            self.log_event("Timer Paused")
            self.update_menu_state()

    def resume_timer(self, _):
        if not self.is_running and self.remaining_time and self.remaining_time > 0:
            self.start_time = time.time()
            self.timer.start()
            self.is_running = True
            self.log_event("Timer Resumed")
            self.update_menu_state()

    def stop_timer(self, _):
        if self.is_running or self.remaining_time:
            self.timer.stop()
            self.is_running = False
            self.remaining_time = None
            self.start_time = None
            self.log_event("Timer Stopped")
            self.title = ""
            self.update_menu_state()

    def start_timer(self, duration):
        self.remaining_time = duration
        self.start_time = time.time()
        self.timer.start()
        self.is_running = True
        self.log_event(f"Timer Started ({duration // 60} minutes)")
        self.update_menu_state()

    def update_menu_state(self):
        """Enable/disable menu items based on the timer's current state."""
        self.menu["⏸ Pause"].set_callback(self.pause_timer if self.is_running else None)
        self.menu["▶ Resume"].set_callback(self.resume_timer if not self.is_running and self.remaining_time else None)
        self.menu["⏹ Stop"].set_callback(self.stop_timer if self.is_running or self.remaining_time else None)

    def log_event(self, event):
        """Log an event to the history file with a timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(self.history_file, "a") as file:
            file.write(f"[{timestamp}] {event}\n")

if __name__ == '__main__':
    app = TimerApp()
    app.run()
