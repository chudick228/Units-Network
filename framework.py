from web3 import AsyncWeb3, Web3
import time
import random
import tools
from loguru import logger
import sys


async def transaction_send(pk):
    w3 = Web3()
    wallet = w3.eth.account.from_key(private_key=pk).address
    cnt, ind = 1000, 0
    logger.remove()
    logger.add(sink=sys.stderr,
               format="<green>{time: hh:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>")
    flag = True
    while flag:
        # ind = 0
        try:
            await tools.sleeping(random.randint(20, 100))
            web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider('https://rpc-testnet.unit0.dev'))
            status = await web3.is_connected()

            if not status:
                logger.error('RPC bad gateway. 10 seconds sleep')
                time.sleep(10)
                continue
            tx_data = await tools.get_transaction_params(web3, wallet)

        except BaseException:
            logger.error('Network ERROR, Reconnecting..')
            time.sleep(20)
            continue

        while ind < cnt:
            try:
                dif = await tools.find_dif(web3)

                if dif > 31:
                    logger.error('blockchain malfunctioning... 30 seconds sleep')
                    time.sleep(30)
                    break

                await tools.vacation(wallet)

                ind += 1
                await tools.sleeping(random.random())
                tx_data['to'] = tools.wallet_maker()
                tx_data['nonce'] = tx_data.get('nonce') + 1
                tx_data['value'] = tx_data.setdefault('value', random.randint(1, 1 * 10 ** 4) * 1 * 10 ** 6)
                try:
                    tx_hash = await tools.sign_and_send_transaction(tx_data, pk, web3)
                    logger.success(f'{tx_hash}, {wallet[-5:]}, {tx_data["nonce"]}')
                    await tools.wait_until_tx_finished(tx_hash, web3)
                    # if not indicator:
                    #     raise BaseException
                    await tools.sleeping(random.randint(2, 10) + random.randint(3, 10))
                except ValueError:
                    balance = await web3.eth.get_balance(wallet)
                    if balance < 4 * 10**13:
                        ind = 1 * 10 ** 10
                        logger.warning(f'Balance of {wallet} is too low.')
                        flag = False
                        break
                    elif tx_data['nonce'] != await web3.eth.get_transaction_count(wallet):
                        logger.warning(f'Nonce too low, retrying... {wallet}')
                        break
                except Exception:
                    logger.warning(f'Transaction Failed. {wallet}')
                    break
            except Exception:
                await tools.sleeping(10)
                break

    logger.critical(f'{wallet} stopped working')
