#!/usr/bin/env python3

import datetime
import decimal
import sys
import time
import traceback

from argparse import ArgumentParser, RawTextHelpFormatter
from multiprocessing import TimeoutError
from multiprocessing.dummy import Pool as ThreadPool

from lib.config.exchanges import max as _max
from lib.helpers import convert_to_time, get_readable_timestamp, get_truncated_value
from lib.vendors.DEPRECATED.max.client import Client
from lib.vendors.DEPRECATED.max.constants import *

_dry = True
_pow = 10 ** 8


def _round(v, d):
    # Python如何将17.955四舍五入保留两位小数？
    # https://www.zhihu.com/question/31156619

    decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    return float(decimal.Decimal(v, decimal.getcontext()).__round__(d + 1).__round__(d))


if __name__ == '__main__':
    helps = [
        'pyCryptoTrader: MAX Grid Trading (Maker)\n'
        'v1.0.1 (2019-08-20 15:17) by Chris Lin <chris#kulisu.me>',
        'the pair you want to trade with',
        'maximum price for placing orders',
        'minimum price for placing orders',
        'difference price between each orders',
        'base price to place versus orders',
        'rate * base to place versus orders',
        'the amount to place in each orders',
        'manually fixed the level1 ask price',
        'manually fixed the level1 bid price',
    ]

    # 這邊設定執行時所需要的參數
    parser = ArgumentParser(description=helps[0], formatter_class=RawTextHelpFormatter)
    parser.add_argument('-p', '--pair', help=helps[1], required=True)
    parser.add_argument('-M', '--maximum', help=helps[2], required=True, type=float)
    parser.add_argument('-m', '--minimum', help=helps[3], required=True, type=float)
    parser.add_argument('-d', '--diff', help=helps[4], required=True, type=float)
    parser.add_argument('-b', '--base', help=helps[5], required=True, type=float)
    parser.add_argument('-r', '--rate', help=helps[6], required=True, type=float)
    parser.add_argument('-a', '--amount', help=helps[7], required=True, type=float)
    parser.add_argument('-A1', '--asks1', help=helps[8], default=-1, type=float)
    parser.add_argument('-B1', '--bids1', help=helps[9], default=-1, type=float)

    # 預設為不輸出任何的除錯資訊
    args = parser.parse_args()

    client = Client(_max.key, _max.secret)
    thread = ThreadPool(processes=2)

    asks, bids = {}, {}
    decimals, paddings = 0, '.0f'

    # Start: 要先處理使用者傳進來的參數
    args.pair = args.pair.lower().replace('.', '').replace('/', '')
    args.maximum = args.minimum if args.minimum > args.maximum else args.maximum
    args.minimum = args.maximum if args.maximum < args.minimum else args.minimum

    prices = client.get_public_pair_depth(args.pair, 1)
    quotes = client.get_public_all_markets()

    for quote in quotes:
        if quote[COMMON_KEY_ID].lower() == args.pair:
            args.amount = get_truncated_value(str(args.amount), int(quote[PRECISION_UNIT_BASE]))

            decimals = int(quote[PRECISION_UNIT_QUOTE])
            paddings = f".{decimals}f"

            break

    args.diff = _round(args.diff, decimals)
    args.base = _round(args.base, decimals)
    # End

    prices[COMMON_KEY_ASKS][-1][DEPTHS_KEY_PRICE] = float(prices[COMMON_KEY_ASKS][-1][DEPTHS_KEY_PRICE])
    prices[COMMON_KEY_BIDS][0][DEPTHS_KEY_PRICE] = float(prices[COMMON_KEY_BIDS][0][DEPTHS_KEY_PRICE])

    if args.asks1 > -1:
        prices[COMMON_KEY_ASKS][-1][DEPTHS_KEY_PRICE] = float(get_truncated_value(args.asks1, decimals))
    if args.bids1 > -1:
        prices[COMMON_KEY_BIDS][0][DEPTHS_KEY_PRICE] = float(get_truncated_value(args.bids1, decimals))

    # 四捨五入買賣單簿上的平均價
    weight = _round(
        (prices[COMMON_KEY_ASKS][-1][DEPTHS_KEY_PRICE] + prices[COMMON_KEY_BIDS][0][DEPTHS_KEY_PRICE]) / 2,
        decimals
    )

    print(
        f"賣單簿價格: {prices[COMMON_KEY_ASKS][-1][DEPTHS_KEY_PRICE]:{paddings}}\n"
        f"買單簿價格: {prices[COMMON_KEY_BIDS][0][DEPTHS_KEY_PRICE]:{paddings}}\n\n"
        f"  掛單簿均價: {weight:{paddings}}\n"
        f"  買賣單價差: {args.base:{paddings}}\n"
        f"  價差的倍數: {args.rate}\n\n"
        f"  掛單的間隔: {args.diff:{paddings}}\n"
        f"  掛單的顆數: {args.amount}\n\n"
        f"掛單上限價: {args.maximum:{paddings}}\n"
        f"掛單下限價: {args.minimum:{paddings}}\n"
    )

    print('依序掛賣單: ')
    ask_prices = range(
        int((weight + args.base) * _pow),
        int(args.maximum * _pow + args.diff * _pow),
        int(args.diff * _pow)
    )

    for p in reversed(ask_prices):
        if _dry:
            print(f"Test Order -> {_round(p / _pow, decimals):{paddings}} * {args.amount}")
            continue

        try:
            _result = thread.apply_async(
                client.set_private_create_order,
                [args.pair, COMMON_KEY_SELL, args.amount, _round(p / _pow, decimals)]
            )

            # 儲存已掛出的賣單號碼與價格
            asks[_round(p / _pow, decimals)] = [_result.get(timeout=10)[ORDER_ID_PLACED]]

            print(
                f"  {_result.get(timeout=10)[ORDER_ID_PLACED]:8} -> "
                f"{_round(p / _pow, decimals):{paddings}} * {args.amount}"
            )
        except Exception as error:
            response = getattr(error, 'read', None)

            print(
                f"    Caught a problem, the error is:\n"
                f"    {str(error)} ({get_readable_timestamp()})"
            )

            if callable(response):
                print(f"    {response()}\n")

            client.set_private_cancel_orders(args.pair)
            sys.exit(1)

    print("\n依序掛買單: ")
    bid_prices = range(
        int((weight - args.base) * _pow),
        int(args.minimum * _pow - args.diff * _pow),
        int(args.diff * _pow * -1)
    )

    for p in bid_prices:
        if _dry:
            print(f"Test Order -> {_round(p / _pow, decimals):{paddings}} * {args.amount}")
            continue

        try:
            _result = thread.apply_async(
                client.set_private_create_order,
                [args.pair, COMMON_KEY_BUY, args.amount, _round(p / _pow, decimals)]
            )

            # 儲存已掛出的買單號碼與價格
            bids[_round(p / _pow, decimals)] = [_result.get(timeout=10)[ORDER_ID_PLACED]]

            print(
                f"  {_result.get(timeout=10)[ORDER_ID_PLACED]:8} -> "
                f"{_round(p / _pow, decimals):{paddings}} * {args.amount}"
            )
        except Exception as error:
            response = getattr(error, 'read', None)

            print(
                f"    Caught a problem, the error is:\n"
                f"    {str(error)} ({get_readable_timestamp()})"
            )

            if callable(response):
                print(f"    {response()}\n")

            client.set_private_cancel_orders(args.pair)
            sys.exit(1)

    if _dry:
        sys.exit(0)
    print()

    while 1:
        try:
            orders = []
            level1 = {'asks': [], 'bids': []}

            # 先取得第一賣價的訂單號
            if len(sorted(asks)) > 0 and len(asks[sorted(asks)[0]]) > 0:
                level1['asks'] = asks[sorted(asks)[0]]
            # 再取得第一買價的訂單號
            if len(sorted(bids)) > 0 and len(bids[sorted(bids)[-1]]) > 0:
                level1['bids'] = bids[sorted(bids)[-1]]

            # 開始檢查買賣單成交狀況
            for s in level1:
                for _id in level1[s]:
                    _result = thread.apply_async(client.get_private_order_detail, [_id])
                    details = _result.get(timeout=10)

                    if details[COMMON_KEY_STATUS] == ORDER_STATUS_COMPLETED:
                        orders.append(details)

                        if s == 'asks':
                            asks[sorted(asks)[0]].remove(_id)
                        else:
                            bids[sorted(bids)[-1]].remove(_id)
                    else:
                        print(
                            f"訂單編號: {_id:8}; 掛單方向: {details[COMMON_KEY_ACTION].upper():4}; "
                            f"掛單金額: {float(details[ORDER_PRICE_PLACED]):{paddings}}; "
                            f"掛單數量: {details[ORDER_AMOUNT_REMAINING]}; 查詢時間: {get_readable_timestamp()}"
                        )

            # 刪除第一賣價的索引值
            if len(sorted(asks)) > 0 and len(asks[sorted(asks)[0]]) == 0:
                asks.pop(sorted(asks)[0], None)
            # 刪除第一買價的索引值
            if len(sorted(bids)) > 0 and len(bids[sorted(bids)[-1]]) == 0:
                bids.pop(sorted(bids)[-1], None)

            for order in orders[:]:
                print(
                    f"\n訂單編號: {order[COMMON_KEY_ID]:8}; "
                    f"成交方向: {order[COMMON_KEY_ACTION].upper():4}; "
                    f"成交金額: {float(order[ORDER_PRICE_AVERAGE]):{paddings}}; "
                    f"成交數量: {order[ORDER_AMOUNT_EXECUTED]}; "
                    f"完全成交: {order[COMMON_KEY_STATUS] == ORDER_STATUS_COMPLETED}"
                )

                side = 'buy' if order[COMMON_KEY_ACTION].lower() == COMMON_KEY_SELL else 'sell'
                price = args.base * args.rate if side == 'sell' else args.base * args.rate * -1
                price = float(order[ORDER_PRICE_PLACED]) + price
                price = _round(price, decimals)

                details = {}

                while 1:
                    try:
                        _result = thread.apply_async(
                            client.set_private_create_order, [args.pair, side, args.amount, price]
                        )
                        details = _result.get(timeout=10)
                    except KeyboardInterrupt:
                        break
                    except TimeoutError:
                        continue
                    except Exception:
                        traceback.print_exc()
                        continue
                    else:
                        break

                if side == 'buy':
                    bids.setdefault(price, [])
                    bids[price].append(details[ORDER_ID_PLACED])
                else:
                    asks.setdefault(price, [])
                    asks[price].append(details[ORDER_ID_PLACED])

                # 移除已處理完的舊單
                orders.remove(order)

                print(
                    f"訂單編號: {details[ORDER_ID_PLACED]:8}; "
                    f"掛單方向: {side:4}; "
                    f"掛單金額: {float(details[ORDER_PRICE_PLACED]):{paddings}}; "
                    f"掛單數量: {details[ORDER_AMOUNT_REMAINING]}; "
                    f"掛單時間: {convert_to_time(details[COMMON_KEY_TIMESTAMP])}\n"
                )

            time.sleep(1)
        except KeyboardInterrupt:
            print("\n開始取消所有未成交的賣單 ..")
            client.set_private_cancel_orders(args.pair, COMMON_KEY_SELL)

            print("\n開始取消所有未成交的買單 ..")
            client.set_private_cancel_orders(args.pair, COMMON_KEY_BUY)

            print("\n已取消所有的掛單！\n記得到網頁上檢查餘額哦哦")
            sys.exit(0)
        except TimeoutError:
            continue
        except Exception as error:
            detail = True

            for fatal in ['Error 502', 'Error 503']:
                if fatal in str(error):
                    traceback.print_exc()
                    continue

            # 403 Forbidden
            # 429 Too Many Requests
            for rps in ['Error 403', 'Error 429']:
                if rps in str(error):
                    print(
                        f"Temporarily blocked, try again in {60 - int(datetime.datetime.now().strftime('%S'))} "
                        f"seconds ..\n"
                    )

                    time.sleep(60 - int(datetime.datetime.now().strftime('%S')))
                    detail = False

            if detail:
                traceback.print_exc()
