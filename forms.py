from aiogram.dispatcher.filters.state import StatesGroup, State

class Form(StatesGroup):
  start = State()
  admin = State()
  add_cup =State()