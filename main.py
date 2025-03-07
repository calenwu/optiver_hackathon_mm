import datetime as dt
import time
import random
import logging

from optibook.synchronous_client import Exchange

exchange = Exchange()
exchange.connect()

logging.getLogger('client').setLevel('ERROR')


def trade_would_breach_position_limit(instrument_id, volume, side, position_limit=10):
    positions = exchange.get_positions()
    position_instrument = positions[instrument_id]

    if side == 'bid':
        return position_instrument + volume > position_limit
    elif side == 'ask':
        return position_instrument - volume < -position_limit
    else:
        raise Exception(f'''Invalid side provided: {side}, expecting 'bid' or 'ask'.''')


def print_positions_and_pnl():
    positions = exchange.get_positions()
    pnl = exchange.get_pnl()

    print('Positions:')
    for instrument_id in positions:
        print(f'  {instrument_id:10s}: {positions[instrument_id]:4.0f}')

    print(f'\nPnL: {pnl:.2f}')


STOCK_A_ID = 'PHILIPS_A'
STOCK_B_ID = 'PHILIPS_B'



print(exchange.get_positions_and_cash())
print(exchange.get_trade_history(STOCK_A_ID))
print(exchange.get_trade_history(STOCK_B_ID))
print(exchange.get_pnl())
while True:
    #____________________________________________________________
    
    order_book_a = exchange.get_last_price_book(STOCK_A_ID)
    order_book_b = exchange.get_last_price_book(STOCK_B_ID)
    positions = exchange.get_positions()
    position_a = positions[STOCK_A_ID]
    position_b = positions[STOCK_B_ID]
    
    exchange.delete_orders(STOCK_A_ID)
    exchange.delete_orders(STOCK_B_ID)
    # buy from a sell to b
    if order_book_a.asks[0].price < order_book_b.bids[0].price:
        volume_to_buy = min(order_book_a.asks[0].volume, order_book_b.bids[0].volume)
        volume_to_buy = min(volume_to_buy, 200 - position_a)
        volume_to_buy = min(volume_to_buy, 200 + position_b)
        if volume_to_buy > 0:
            exchange.insert_order(
                instrument_id=STOCK_A_ID,
                price=order_book_a.asks[0].price,
                volume=volume_to_buy,
                side='bid',
                order_type='ioc'
            )
            exchange.insert_order(
                instrument_id=STOCK_B_ID,
                price=order_book_b.bids[0].price,
                volume=volume_to_buy,
                side='ask',
                order_type='ioc'
            )
    if order_book_b.asks[0].price < order_book_a.bids[0].price:
        volume_to_buy = min(order_book_b.asks[0].volume, order_book_a.bids[0].volume)
        volume_to_buy = min(volume_to_buy, 200 - position_b)
        volume_to_buy = min(volume_to_buy, 200 + position_a)
        if volume_to_buy > 0:
            exchange.insert_order(
                instrument_id=STOCK_B_ID,
                price=order_book_b.asks[0].price,
                volume=volume_to_buy,
                side='bid',
                order_type='ioc'
            )
            exchange.insert_order(
                instrument_id=STOCK_A_ID,
                price=order_book_a.bids[0].price,
                volume=volume_to_buy,
                side='ask',
                order_type='ioc'
            )
            
    
    order_book_a = exchange.get_last_price_book(STOCK_A_ID)
    order_book_b = exchange.get_last_price_book(STOCK_B_ID)
    positions = exchange.get_positions()
    position_a = positions[STOCK_A_ID]
    position_b = positions[STOCK_B_ID]
    
    
    # Market marking a
    if order_book_a.asks[0].price - order_book_a.bids[0].price > 0.25:
        if (position_a + position_b) > 50:
            if (position_a > 0):
                exchange.insert_order(
                    instrument_id=STOCK_A_ID,
                    price=order_book_a.asks[0].price - 0.1,
                    volume=abs(position_a + position_b),
                    side='ask',
                    order_type='limit'   
                )
        elif (position_a + position_b) < -50:
            if (position_a < 0):
                exchange.insert_order(
                    instrument_id=STOCK_A_ID,
                    price=order_book_a.bids[0].price + 0.1,
                    volume=abs(position_a + position_b),
                    side='bid',
                    order_type='limit'   
                )
        else:
            volume = min(10, 200 - abs(position_a))
            exchange.insert_order(
                instrument_id=STOCK_A_ID,
                price=order_book_a.asks[0].price - 0.1,
                volume=volume,
                side='ask',
                order_type='limit'   
            )
            exchange.insert_order(
                instrument_id=STOCK_A_ID,
                price=order_book_a.bids[0].price + 0.1,
                volume=volume,
                side='bid',
                order_type='limit'   
            )
    # Market marking b
    order_book_a = exchange.get_last_price_book(STOCK_A_ID)
    order_book_b = exchange.get_last_price_book(STOCK_B_ID)
    positions = exchange.get_positions()
    position_a = positions[STOCK_A_ID]
    position_b = positions[STOCK_B_ID]
    if order_book_b.asks[0].price - order_book_b.bids[0].price > 0.25:
        if (position_a + position_b) > 50:
            if (position_b > 0):
                exchange.insert_order(
                    instrument_id=STOCK_B_ID,
                    price=order_book_b.asks[0].price - 0.1,
                    volume=abs(position_a + position_b),
                    side='ask',
                    order_type='limit'   
                )
        elif (position_a + position_b) < -50:
            if (position_a < 0):
                exchange.insert_order(
                    instrument_id=STOCK_B_ID,
                    price=order_book_b.bids[0].price + 0.1,
                    volume=abs(position_a + position_b),
                    side='bid',
                    order_type='limit'   
                )
        else:
            volume = min(10, 200 - abs(position_b))
            exchange.insert_order(
                instrument_id=STOCK_B_ID,
                price=order_book_b.asks[0].price - 0.1,
                volume=volume,
                side='ask',
                order_type='limit'   
            )
            exchange.insert_order(
                instrument_id=STOCK_B_ID,
                price=order_book_b.bids[0].price + 0.1,
                volume=volume,
                side='bid',
                order_type='limit'   
            )
    time.sleep(0.5)