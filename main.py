import rumps
import time
import os

'''
Antonio Leon
01/21/2025
MBT for MacOS
v. 3.00
'''

class TimerApp(rumps.App):
    def __init__(self):
        script_directory = os.path.dirname(os.path.realpath(__file__))
        self.history_file = os.path.join(script_directory, "timer_history.txt")
        icon_path = os.path.join(script_directory, "sandClock2.png")
        super(TimerApp, self).__init__("Timer", icon=icon_path)
        
        # Ensure the history file exists
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w"): pass
        
        self.timer = rumps.Timer(self.update_timer, 1)
        self.start_time = None
        self.remaining_time = None
        self.is_running = False
        self.original_duration = None
        self.custom_message = "Time is up!"  # Default message

        # Set up menu
        self.menu = [
            rumps.MenuItem("Set Custom Time", callback=self.set_custom_time),
            None,
            rumps.MenuItem("⏸ Pause", callback=self.pause_timer),
            rumps.MenuItem("▶ Resume", callback=self.resume_timer),
            rumps.MenuItem("⏹ Stop", callback=self.stop_timer),
            None
        ]

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
            self.title = ""
            self.is_running = False
            self.log_event("Timer Finished")
            original_minutes = self.original_duration // 60  # Calculate original duration in minutes
            rumps.notification(
                title="Time is up!",
                subtitle=f"Your timer for {original_minutes} minutes has ended.",
                message=self.custom_message
            )
            self.update_menu_state()

    @rumps.clicked("Set Custom Time")
    def set_custom_time(self, _):
        # First window to get the timer duration with a toggle for custom message
        time_response = rumps.Window(
            title="Set a Custom Timer",
            message="Enter time in minutes:",
            default_text="10",
            ok="Next",
            cancel="Cancel",
            dimensions=(220, 40)
        )

        # Adding a text field to input 'Yes' or 'No'
        time_response.icon = None
        response = time_response.run()

        if response.clicked:
            try:
                minutes = int(response.text.strip())
                if minutes <= 0:
                    rumps.alert(
                        title="❌ Invalid Input ❌",
                        message="Please enter a positive number greater than 0."
                    )
                    return

                # Ask for a custom message if 'Yes' was entered
                custom_message = "Time is up!"  # Default message
                custom_message_input = rumps.Window(
                    title="Custom Message",
                    message="Enter 'Yes' to add a custom message, or 'No' to skip.",
                    default_text="No",
                    ok="Next",
                    cancel="Cancel",
                    dimensions=(220, 40)
                ).run()

                if custom_message_input.clicked:
                    if custom_message_input.text.strip().lower() == "yes":
                        message_response = rumps.Window(
                            title="Set Custom Notification Message",
                            message="Enter a custom message for the notification:",
                            default_text="Time is up!",
                            ok="Start Timer",
                            cancel="Cancel",
                            dimensions=(220, 40)
                        ).run()

                        if message_response.clicked:
                            custom_message = message_response.text.strip()
                            if not custom_message:
                                custom_message = "Time is up!"  # Default message if none provided

                self.start_timer(minutes * 60, custom_message)

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

    def start_timer(self, duration, custom_message):
        self.original_duration = duration  # Store the original duration
        self.remaining_time = duration
        self.start_time = time.time()
        self.custom_message = custom_message  # Store the custom message
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
