import subprocess
from pathlib import Path
from typing import Callable, Dict, List

import pendulum
from flask import Flask, render_template, request


app = Flask(__name__)

PREVIEW = ['scanimage']


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
    """Scans an image, if requested with POST. If a "Preview" scan was
    requested, the scan will start with default options on the selected
    scanner: black & white, PNM file format, and 72 DPI. Once the scan
    finishes, the scanned image is shown in the iframe. If "Scan" was
    chosen, no preview will be generated; the scan will start with all
    chosen options. Upon completion, the image will be uploaded to the
    user. If requested with GET, nothing is shown.

    Returns:
        Callable[..., str]: a template containing a preview scan,
            or a blank page

    """
    if request.method != 'POST':
        return render_template('scan.html', image=None)
    else:
        scanner = request.form['scanner'].split('`')[1].split("'")[0]
        name = f"{pendulum.now()}.{options['format']}"
        if 'scan' in request.form:
            options = request.form.to_dict()
            options['format'] = options['format'].lower()
            command = process_options(scanner, options)
            file = Path(f"scans/{name}")
            run_command(command, file)
            return app.send_file(
                file,
                as_attachment=True,
                attachment_filename=name,
                )
        else:
            file = Path(f"static/{name}")
            run_command(PREVIEW, file)
            return render_template('scan.html', image=file)


def get_scanners() -> List[str]:
    """Get scanners as a list of strings. Call `scanimage -L`.
    The initial output from s`ubprocess.check_output` should look like
    "device `vendor:port:x:y' is a ... device" with newlines separating
    each device.

    Returns:
        List[str]: list of scanners by description

    Raises:
        FileNotFoundError: if `scanimage` is not installed

    """
    scanners = subprocess.check_output(['scanimage', '-L'])
    return scanners.decode('utf-8').rstrip().split('\n')


def process_options(scanner: str, options: Dict[str, str]) -> List[str]:
    """Process options retrieved from the web UI.

    Args:
        scanner (str): the device address of the scanner to use
        options (Dict[str, str]): options chosen to scan; see below:
            - color: 'bw', 'color'
            - format: 'pnm', 'tiff'
            - dpi: 'dpi_72', 'dpi_96', 'dpi_150', 'dpi_300'

    Returns:
        List[str]: the final command in a list of the arguments

    """
    args = ['scanimage']
    args.append('--device-name')
    args.append(scanner)
    args.append('--format')
    args.append(options['format'])
    args.append('--mode')
    if options['format'] == 'color':
        args.append('Color')
    args.append('resolution')
    args.append(options['dpi'].split('_')[1])
    return args


def run_command(command: List[str], file: Path) -> None:
    """Run the command defined as a list of strings. Both "Preview"
    and "Scan" use this. Outputs the file name of the created scan.

    Args:
        command (List[str]): the command in list form
        file (Path): where the resulting scan will be stored

    """
    subprocess.Popen(command, stdout=file)


SCANNERS = get_scanners()


if __name__ == "__main__":
    app.run()
