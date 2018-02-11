import datetime
import random

def get_random_serialnumber():
    random.seed()
    return float(random.randint(1, 2**8))

# Refill the provided cartridge
def refill(cartridge):
    cartridge.current_material_quantity = cartridge.initial_material_quantity
    cartridge.last_use_date.FromDatetime(datetime.datetime.now())
    cartridge.manufacturing_date.FromDatetime(datetime.datetime.now())
    cartridge.serial_number = get_random_serialnumber()

    return cartridge



