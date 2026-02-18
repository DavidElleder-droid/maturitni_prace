from pydantic import BaseModel


class Car(BaseModel):
    year:int
    model:str
    power:float #kWh
    brand:str

auto=Car(year=1999, model="911", power=440, brand= "Porsche")

print(auto)

