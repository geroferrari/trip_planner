#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime
import pyinputplus as pyip
import pickle
import typer
import os.path

app = typer.Typer()

import logging
logger = logging.getLogger(__name__)

travel_inputs = ['departure_city', 'departure_date', 'destination_city', 
                   'destination_date', 'transport_type', 'transport_price',
                   'transport_booked', 'transport_paid']

df_travel = pd.DataFrame(columns=travel_inputs)



def set_trip_duration() -> int:
    trip_start_date = pyip.inputDate('When your trip begins (YYYY/MM/DD): ')
    trip_end_date = pyip.inputDate('When your trip ends (YYYY/MM/DD): ')
    return (trip_end_date-trip_start_date).days

# recorrer una lista de funciones a la que le paso de parametro un candidato y le hace un chequeo
chequeo = []
chequeo.append(lambda var: var['departure_day'] < var['destination_day'] )
#si alguna falla no la agrego y le pregunto devuelta

from functools import partial
#armar una funcion partial functools 
# para chequear con lo que ya hay en la bdd, deberia pooder acceder al df_travel
# chequeo.append(lambda var: all(map(lambda x:,df_travel)))
# la salida del candidato no este entre las salidas de cosas previas, para que no se pisen
chequeo.append(lambda var: all(r['destination_day'] > var['departure_day'] > r['departure_day'] for r in df_travel.iterrows()))

# poner un presupuesto al principio y que vaya restando

def handle_travel_inputs(day: int): 
    # Primero prguntar todo y despues pasarle todos los parametros a una funcion
    # Try y llamar a la funcion
    # chequear que las fechas sean las correctas
    # hay que ver si encuentra colisiones de las fechas, la tengo que catchear y hacer algo
    #que el catch me guarde todas las variables

    departure_place = pyip.inputStr('Departure Place (City-Country): ')
    departure_day = pyip.inputDatetime('Departure Day & Hour (YYYY/MM/DD HH:MM): ')
    destination_place = pyip.inputStr('Destination Place (City-Country: ')
    destination_date = pyip.inputDatetime('Destination Day & Hour (YYYY/MM/DD HH:MM): ')
    transport_type = pyip.inputMenu(['car', 'taxi', 'bus', 'train', 'plane', 'boat'], 'Transport Type: \n ')
    transport_price = pyip.inputInt('Transport Price (in U$D): ') 
    transport_booked = pyip.inputYesNo('Is it already booked?') 
    transport_paid = pyip.inputYesNo('Is it already paid?') 
    if not transport_paid:
        transport_payment_date =  pyip.inputDate('When do you have to pay the transport ticket (YYYY/MM/DD): ')

    df_travel.at[day, 'departure_city'] = departure_place 
    df_travel.at[day, 'departure_date'] = departure_day
    df_travel.at[day, 'destination_city'] = destination_place
    df_travel.at[day, 'destination_date'] = destination_date
    df_travel.at[day, 'transport_type'] =  transport_type
    df_travel.at[day, 'transport_price'] = transport_price
    df_travel.at[day, 'transport_booked'] = transport_booked
    df_travel.at[day, 'transport_paid'] =  transport_paid
    if not transport_paid:
        df_travel.at[day, 'transport_payment_date'] = transport_payment_date
 
def handle_stay_inputs():
    # TODO: add hotel, tours, sightseeing, prices, atractions, etc
    pass


@app.command()
def view(trip_name: str):
    logger.info("Aplication in view mode")
    logger.info(f"You have selected trip: {trip_name}")

    pass
    

@app.command()
def add(trip_name: str, new: bool):
    logger.info("Aplication in Add mode")

    if not new:
        if os.path.exists(f'database_{trip_name}'):
            try:
                file = open(f'database_{trip_name}', 'rb')
            except IOError:
                # TODO : do something else
                logger.error(f"The file {trip_name} have issues, try again later")
                return 0
            
        data = pickle.load(file)
        print(data)
        file.close()

    logger.info(f"You have selected trip: {trip_name}")
    
    # trip_start_date = pyip.inputDate('When your trip begins (YYYY/MM/DD): ')
    # trip_end_date = pyip.inputDate('When your trip ends (YYYY/MM/DD): ')
    
    trip_duration = set_trip_duration()
    
    logger.info(f'Your trip is going to last {trip_duration} days')
    logger.info('Lets complete the calendar with your activities & plans')
    
    
    for day in range(trip_duration):
        decision = pyip.inputMenu(['travel', 'stay', 'blank'] ,f'Day {day}: What are your plans? (select one)\n')
        
        if decision == 'travel':
            handle_travel_inputs(day = day)
        
        elif decision == 'stay':
            handle_stay_inputs()
            
        elif decision == 'blank':
            # TODO: should skip this day, and continue with the next one
            continue
            
        else:
            logger.error("unexpected error, please try again")

        logger.info(f"Activities for day {day}: {df_travel.loc[[day]]}")

        file = open(f'database_{trip_name}', 'wb')
        pickle.dump(df_travel, file)
        file.close()

                
    else:
        #TODO: Print information of the trip.
        pass
        
    # LOGURU? 
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Just logger")


if __name__ == '__main__':
    app()

#hacer una funcion    