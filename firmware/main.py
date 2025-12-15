from src.controller import Controller
from src.repository import Repository
from src.display import LCD_Display

repository = Repository()
display = LCD_Display(repository)
controller = Controller(repository, display)

controller.start_display()