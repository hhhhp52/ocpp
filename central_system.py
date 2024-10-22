import asyncio
import logging
from multiprocessing.connection import Connection

import websockets
import datetime

from ocpp.routing import on, after
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16 import enums
from websockets import ConnectionClosedError, ConnectionClosedOK

from config import CP_NAME, SERVER_HOST, SERVER_PORT

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on(enums.Action.boot_notification)
    async def on_boot_notification(self, **kwargs):
        print(f'charge_point_model: {kwargs["charge_point_model"]}')
        print(f'charge_point_vendor: {kwargs["charge_point_vendor"]}')
        return call_result.BootNotification(
            current_time=datetime.datetime.now(datetime.UTC).isoformat(),
            interval=10,
            status=enums.RegistrationStatus.accepted
        )

    @after(enums.Action.boot_notification)
    async def after_boot_notification(self, **kwargs):
        print('Boot notification has been sent')


    @on(enums.Action.authorize)
    async def on_authorize(self, **kwargs):
        print(f'id_tag: {kwargs["id_tag"]}')
        return call_result.Authorize(
            id_tag_info=call_result.IdTagInfo(
                expiry_date=datetime.datetime.now(datetime.UTC).isoformat(),
                parent_id_tag="123456789",
                status=enums.AuthorizationStatus.accepted
            )
        )

    @on(enums.Action.cancel_reservation)
    async def on_cancel_reservation(self, **kwargs):
        print(f'reservation_id: {kwargs["reservation_id"]}')
        return call_result.CancelReservation(
            status=enums.CancelReservationStatus.accepted
        )

    @on(enums.Action.change_availability)
    async def on_change_availability(self, **kwargs):
        print(f'connector_id: {kwargs["connector_id"]}')
        print(f'type: {kwargs["type"]}')
        return call_result.ChangeAvailability(
            status=enums.AvailabilityStatus.accepted
        )

    @on(enums.Action.start_transaction)
    async def on_start_transaction(self, **kwargs):
        print(f'connector_id: {kwargs["connector_id"]}')
        print(f'id_tag: {kwargs["id_tag"]}')
        print(f'meter_start: {kwargs["meter_start"]}')
        print(f'timestamp: {kwargs["timestamp"]}')
        return call_result.StartTransaction(
            transaction_id=123,
            id_tag_info=call_result.IdTagInfo(
                expiry_date=datetime.datetime.now(datetime.UTC).isoformat(),
                parent_id_tag="123456789",
                status=enums.AuthorizationStatus.accepted
            )
        )

    @on(enums.Action.stop_transaction)
    async def on_stop_transaction(self, **kwargs):
        print(f'id_tag: {kwargs["id_tag"]}')
        print(f'meter_stop: {kwargs["meter_stop"]}')
        print(f'timestamp: {kwargs["timestamp"]}')
        print(f'transaction_id: {kwargs["transaction_id"]}')
        print(f'reason: {kwargs["reason"]}')
        return call_result.StopTransaction(
            id_tag_info=call_result.IdTagInfo(
                expiry_date=datetime.datetime.now(datetime.UTC).isoformat(),
                parent_id_tag="123456789",
                status=enums.AuthorizationStatus.accepted
            )
        )

    @on(enums.Action.heartbeat)
    async def on_hearbeat(self, **kwargs):
        print(f'heartbeat')
        return call_result.Heartbeat(
            current_time=datetime.datetime.now(datetime.UTC).isoformat()
        )

async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. "
                 "Closing Connection")
        return await websocket.close()

    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')

    if charge_point_id not in CP_NAME:
        logging.error("Unknown charge point %s", charge_point_id)
        return await websocket.close()

    charge_point = ChargePoint(charge_point_id, websocket)

    try:
        await charge_point.start()
    except ConnectionClosedOK:
        print("ConnectionClosedOK exception")


async def main():
    server = await websockets.serve(
        on_connect,
        SERVER_HOST,
        SERVER_PORT,
        subprotocols=['ocpp1.6']
    )
    logging.info("WebSocket Server Started")
    await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())