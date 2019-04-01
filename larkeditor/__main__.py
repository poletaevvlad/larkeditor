import signal
import sys
from larkeditor.application import Application


signal.signal(signal.SIGINT, signal.SIG_DFL)
app = Application()
app.run(sys.argv)
