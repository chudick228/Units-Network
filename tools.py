from web3 import AsyncWeb3
import asyncio
import random
import time
from loguru import logger


def wallet_maker(

) -> str:
    """
    :return:
    """
    web3 = AsyncWeb3()
    acc = web3.eth.account.create()
    pk = web3.to_hex(acc.key)
    wallet = AsyncWeb3.to_checksum_address(web3.eth.account.from_key(private_key=pk).address)
    return wallet


def blockchain_connect() -> AsyncWeb3:
    web3 = AsyncWeb3(AsyncWeb3.HTTPProvider('https://rpc-testnet.unit0.dev'))
    return web3


async def sleeping(time=30) -> None:
    await asyncio.sleep(time)


async def wait_until_tx_finished(
        tx_hash,
        web3,
        wait_time=180
) -> bool:
    """
    :param tx_hash:
    :param web3:
    :param wait_time:
    :return:
    """
    start_time = time.time()
    while True:
        try:
            receipts = await web3.eth.get_transaction_receipt(tx_hash)
            status = receipts.get("status")
            if status == 1:
                return True
            elif status is None:
                await asyncio.sleep(1)
            else:
                logger.warning(f'failed tx: {tx_hash}')
                return False
        except:
            if time.time() - start_time > wait_time:
                logger.warning(f'FAILED TX: {tx_hash}')
                return False
            await asyncio.sleep(5)


async def sign_and_send_transaction(
        transaction,
        private_key,
        web3: AsyncWeb3
) -> str:
    """
    :param transaction:
    :param private_key:
    :param web3:
    :return transaction_hash, status:
    """
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    transaction_hash = await web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    return transaction_hash.hex()


async def get_transaction_params(
        web3: AsyncWeb3,
        wallet
) -> dict:
    """
    :param web3:
    :param wallet:
    :return:
    """
    params = await asyncio.gather(
        asyncio.create_task(web3.eth.chain_id),                         # 0 chain id
        asyncio.create_task(web3.eth.max_priority_fee),                 # 1 priority fee
        asyncio.create_task(web3.eth.get_block('latest')),              # 2 latest block
        asyncio.create_task(web3.eth.get_transaction_count(wallet))     # 3 nonce
    )
    base_fee = int(params[2]['baseFeePerGas'] * 1.3)
    all_fee = base_fee + params[1]
    # amount = random.randint(1, 1 * 10 ** 4) * 1 * 10 ** 6
    tx_data = {
        'chainId': params[0],
        'maxPriorityFeePerGas': int(params[1]),
        'maxFeePerGas': int(all_fee),
        'from': wallet,
        # 'to': wallet_maker(),
        'gas': 21000,
        'nonce': params[3] - 1,
        # 'value': amount
    }
    return tx_data


async def find_dif(
        web3: AsyncWeb3
) -> int:
    """
    :param web3:
    :return:
    """
    st = time.time()
    block = await web3.eth.get_block('latest')
    block_time = block['timestamp']
    return int(st - block_time)


async def vacation(
        wallet,
        multiplier=1
) -> None:
    """
    :param wallet:
    :param multiplier:
    :return:
    """
    rng = random.randint(1, 20)
    if rng == 10:
        logger.info(f'{wallet} is resting..')
        await asyncio.sleep(random.randint(60, 90) * multiplier)


