import asyncio
import framework


async def main1():
    # web3 = Web3()
    txt = 'privates.txt'
    with open(txt, 'r', encoding='utf-8') as keys_file:
        accounts = [line.replace('\n', '') for line in keys_file.readlines()]
    # addresses = [web3.eth.account.from_key(pk).address for pk in accounts]
    tasks = []
    for pk in accounts:
        tasks.append(asyncio.create_task(framework.transaction_send(pk)))
    try:
        await asyncio.wait(tasks)
    finally:
        print('all done')

if __name__ == '__main__':
    asyncio.run(main1())
    