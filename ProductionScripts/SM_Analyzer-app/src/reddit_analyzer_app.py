import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
import logging
import signal

def signal_handler(signum, frame):
    # Log the termination signal
    logging.info(f"Received signal {signum}. Initiating graceful shutdown...")
    # Get the main window instance and trigger data saving
    if hasattr(signal_handler, 'window') and signal_handler.window:
        # Add cancellation before saving state
        signal_handler.window.cancel_current_operations()
        signal_handler.window.save_current_state()
    # Exit the application
    QApplication.quit()

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination request
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    # Store window reference in signal handler
    signal_handler.window = window
    
    # Add global cancellation shortcut (Ctrl+Break or Ctrl+C)
    def handle_keyboard_interrupt():
        window.cancel_current_operations()
    
    app.instance().installEventFilter(window)  # Enable event filtering
    
    # Connect quit handlers
    app.aboutToQuit.connect(lambda: window.cancel_current_operations())
    app.aboutToQuit.connect(lambda: window.save_current_state())
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 