import subprocess
from typing import Callable, List

from flask import Flask, render_template, request


app = Flask(__name__)


@app.route('/')
def main() -> Callable[..., str]:
    """Returns the main page. Provided that PRINTERS were found, they
    will be used in the dropdown in the template.

    Returns:
        Callable[..., str]: the template, rendered

    """
    return render_template('index.html', scanners=SCANNERS)


@app.route('/scan.html', methods=['GET', 'POST'])
def scan() -> Callable[..., str]:
    """Scans an image, if requested with POST. Once the scan finishes,
    opens the scanned image in the iframe. If requested with GET, on

    Returns:
        Callable[..., str]: a template containing a scan,
            or a blank page

    """
    if request.method != 'POST':
        image = None
    else:
        pass

    return render_template('scan.html', image=image)


def get_scanners() -> List[str]:
    """Get scanners as a list of strings. Call `scanimage -L`.
    The initial output from s`ubprocess.check_output` should look like
    "device `vendor:port:x:y' is a ... device" with newlines separating
    each device.

    Returns:
        List[str]: list of scanners by description

    """
    scanners = subprocess.check_output(["scanimage", "-L"])
    return scanners.decode('utf-8').split('\n')


if __name__ == "__main__":
    SCANNERS = get_scanners()
    app.run()
