import asyncio
import logging
import websockets

import charge_point
from config import CP_NAME_2, PRODUCTION, WEBS_SOCKET_SERVER, WEB_SOCKET_SERVER, SERVER_HOST, SERVER_PORT

logging.basicConfig(level=logging.INFO)


async def main():
    env = 'development'
    if env == PRODUCTION:
        uri = f'{WEBS_SOCKET_SERVER}://{SERVER_HOST}:{SERVER_PORT}/{CP_NAME_2}'
    else:
        uri = f'{WEB_SOCKET_SERVER}://{SERVER_HOST}:{SERVER_PORT}/{CP_NAME_2}'
    async with websockets.connect(
            uri,
            subprotocols=['ocpp1.6']
    ) as ws:
        cp = charge_point.ChargePoint(f'{CP_NAME_2}', ws)
        await asyncio.gather(cp.start(), cp.send_boot_notification(), cp.send_authorize_request('123456789'))



if __name__ == '__main__':
    asyncio.run(main())