import contextlib

import difflib
import os
import re
import sys
import urllib.parse
from io import StringIO


def multiple_replace(repl, text, *flags):
    # Create a regular expression  from the dictionary keys
    regex = re.compile(r"(%s)" % "|".join(repl.keys()), *flags)
    return regex.sub(
        lambda mo: repl[
            [k for k in repl if re.search(k, mo.string[mo.start() : mo.end()], *flags)][
                0
            ]
        ],
        text,
    )


@contextlib.contextmanager
def stdout_io(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def string_similarity(user_input, compare_to) -> float:
    compare_to = compare_to.lower()
    user_input = user_input.lower()

    add = 0
    if user_input in compare_to or compare_to in user_input:
        add = 0.15

    return min(1, difflib.SequenceMatcher(None, user_input, compare_to).ratio() + add)


def urlencode(text):
    return urllib.parse.quote(text)


def make_sticker(filename, out_file, max_height=512, transparent=True):
    image = Image.open(filename)

    # resize sticker to match new max height
    # optimize image dimensions for stickers
    if max_height == 512:
        resize_ratio = min(512 / image.width, 512 / image.height)
        image = image.resize(
            (int(image.width * resize_ratio), int(image.height * resize_ratio))
        )
    else:
        image.thumbnail((512, max_height), Image.ANTIALIAS)

    if transparent:
        canvas = Image.new("RGBA", (512, image.height))
    else:
        canvas = Image.new("RGB", (512, image.height), color="white")

    pos = (0, 0)
    try:
        canvas.paste(image, pos, mask=image)
    except ValueError:
        canvas.paste(image, pos)

    canvas.process_messages(out_file)
    return out_file


def _trim(im, add_to_diff=(2.0, -100)):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add_for_current_client(diff, diff, *add_to_diff)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def trim_image(filename, out_file, exact_background=False):
    im = Image.open(filename)
    result = _trim(im, (1.0, 0) if exact_background else (2.0, -100))
    result.save(out_file)
    return out_file


def get_image_dimensions(filename):
    im = Image.open(filename)
    return im.width, im.height


def create_chrome_driver(download_dir, headless=True):
    chrome_path = "/usr/bin/google-chrome-beta"
    chromedriver_path = "/usr/bin/chromedriver"
    window_size = "1920,1080"

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % window_size)
    chrome_options.binary_location = chrome_path

    prefs = {
        "browser.helperApps.alwaysAsk.force": False,
        "browser.helperApps.neverAsk.saveToDisk": "application/octet-stream",
        "profile.default_content_settings.popups": 0,
        "download.default_directory": download_dir,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        executable_path=chromedriver_path, chrome_options=chrome_options
    )

    if headless:
        # Workaround to enable file downloads in headless browser.
        # Many issues are floating around to get this integrated, but for now this hack will do.
        params = {
            "cmd": "Page.setDownloadBehavior",
            "params": {"behavior": "allow", "downloadPath": download_dir},
        }
        data = utils.dump_json(params)
        path = f"/session/" + driver.session_id + "/chromium/send_command"
        url = "%s%s" % (driver.command_executor._url, path)
        driver.command_executor._request("POST", url, body=data)

    return driver


def chunks(iterable, chunk_size):
    """Yield successive group-sized chunks from l."""
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i : i + chunk_size]


NOTSET = object()
