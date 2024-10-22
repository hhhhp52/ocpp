import time
from typing import Text
from ocpp.v16.enums import RegistrationStatus
import logging

from ocpp.v16 import call
from ocpp.v16 import ChargePoint as cp

class ChargePoint(cp):

    async def send_boot_notification(self, charge_point_model, charge_point_vendor):
        request = call.BootNotification(
            charge_point_model=charge_point_model,
            charge_point_vendor=charge_point_vendor,
        )
        response = await self.call(request)
        try:
            if response.status == RegistrationStatus.accepted:
                logging.info("Connected to central system.")
        except AttributeError:
            logging.info("Central system has rejected boot notification.")

        return

    async def send_authorize_request(self, id_tag: Text):
        request = call.Authorize(id_tag=id_tag)
        response = await self.call(request)
        return response

    async def send_hearbeat(self):
        count = 0
        max_count = 10

        while count < max_count:
            time.sleep(1)
            request = call.Heartbeat()
            response = await self.call(request)
            count += 1
            print(f'Heartbeat count: {count}')
            print(response)
