from aiogram.fsm.state import StatesGroup, State

class RegisterState(StatesGroup):
    fullname = State()
    phone = State()

class RegisterStateRu(StatesGroup):
    fullname = State()
    phone = State()

class SettingsState(StatesGroup):
    full_name = State()
    phone = State()
    language = State()
