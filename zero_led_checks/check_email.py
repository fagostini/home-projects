import imaplib
import logging
import secrets
import time
import urllib.request
from pathlib import Path

import blinkt

script_path = Path(__file__).parent.resolve()

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("email_application")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(script_path.joinpath(f'check_email_{time.strftime("%Y-%m-%d", time.gmtime())}.log'))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

blinkt.set_clear_on_exit()
blinkt.set_brightness(0.1)


def check_url_status(address: str) -> int:
    if not address.startswith(("http:", "https:")):
        raise ValueError("URL must start with 'http:' or 'https:'")
    return urllib.request.urlopen(address).status


def get_num_msgs(user: str, password: str, limit: int = 6) -> int:
    obj = imaplib.IMAP4_SSL("imap.gmail.com", "993")
    obj.login(user, password)
    obj.select()
    msgs = obj.search(None, "UnSeen")
    msgs = msgs[1][0].decode("utf-8")
    num_msgs = len(msgs.split(" ")) if msgs != "" else 0
    return num_msgs if num_msgs < limit else limit


def assign_colour_email(n: int) -> tuple:
    if n == 0:
        return (0, 102, 204)
    elif n == 1:
        return (0, 204, 204)
    elif n == 2:
        return (0, 204, 102)
    elif n == 3:
        return (0, 204, 0)
    elif n == 4:
        return (102, 204, 0)
    elif n == 5:
        return (204, 204, 0)
    elif n == 6:
        return (204, 102, 0)
    elif n == 7:
        return (204, 0, 0)


if __name__ == "__main__":
    logger.info("Starting...")

    while True:
        try:
            num_msgs = get_num_msgs(secrets.EMAIL_USER, secrets.EMAIL_PASSWORD)
        except Exception as e:
            logger.exception(e)
            num_msgs = 0

        blinkt.clear()
        for i in range(blinkt.NUM_PIXELS):
            if i < num_msgs:
                # print(i, assign_colour_email(i))
                r, g, b = assign_colour_email(i)
                blinkt.set_pixel(i, r, g, b)
            else:
                # print("b", i, (0, 0, 0))
                blinkt.set_pixel(i, 0, 0, 0)

        for i, x in enumerate([check_url_status(secrets.NEXTCLOUD), check_url_status(secrets.PIHOLE)]):
            if x < 200:
                logger.info("Informational response")
                blinkt.set_pixel(i + 6, 0, 102, 204)
            elif x < 300:
                blinkt.set_pixel(i + 6, 0, 204, 0)
            elif x < 400:
                logger.warning("Redirection response")
                blinkt.set_pixel(i + 6, 204, 204, 0)
            elif x < 500:
                logger.error("Client error response")
                blinkt.set_pixel(i + 6, 204, 102, 0)
            else:
                logger.error("Server error response")
                blinkt.set_pixel(i + 6, 204, 0, 0)

        blinkt.show()

        for i in range(6):
            # for x in range(blinkt.NUM_PIXELS):
            #     print(blinkt.get_pixel(x))
            time.sleep(10)
