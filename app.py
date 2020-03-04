import subprocess
from typing import Callable, Dict, List

import pendulum
from flask import Flask, render_template, request, send_file

from preview import preview


app = Flask(__name__)
app.register_blueprint(preview)

PREVIEW_CMD = ['scanimage']


@app.route('/')
def main() -> Callable[..., str]:
    """Returns the main page. Provided that PRINTERS were found, they
    will be used in the dropdown in the template.

    Returns:
        Callable[..., str]: the template, rendered

    """
    return render_template(
        'index.html',
        scanners=SCANNERS,
        preview=PREVIEW_EXISTS,
        )


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
        return render_template(
            'scan.html',
            image=None,
            preview=PREVIEW_EXISTS,
            )
    else:
        scanner = request.form['scanner'].split('`')[1].split("'")[0]
        name = str(pendulum.now())
        if 'scan' in request.form:
            options = request.form.to_dict()
            options['format'] = options['format'].lower()
            command = process_options(scanner, options)
            run_command(command, 'scans', name, options['format'])
            return send_file(
                file,
                as_attachment=True,
                attachment_filename=file,
                )
        else:
            run_command(PREVIEW_CMD, 'previews', name, 'jpg')
            return render_template(
                'scan.html',
                image=name,
                preview=PREVIEW_EXISTS,
                )


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
    # The default for `scanimage` is B&W
    if options['format'] == 'color':
        args.append('--mode')
        args.append('Color')
    args.append('--resolution')
    args.append(options['dpi'].split('_')[1])
    return args


def run_command(command: List[str], target: str, file: str, fmt: str) -> None:
    """Run the command defined as a list of strings. Both "Preview"
    and "Scan" use this. Outputs the file name of the created scan.

    Because ".pnm" files cannot be used as previews, previews will
    be outputted as ".jpg". See the function call in `scan()`.

    Args:
        command (List[str]): the command in list form
        target (str): target directory, i.e. scans, previews
        file (str): where the resulting scan will be stored, without
            the desired extension (`fmt`)
        fmt (str): image format, i.e. pnm, jpg, tiff

    """
    out = f'{target}/{file}.{fmt}'

    if fmt == 'pnm':
        with open(out, 'w') as f:
            command = subprocess.Popen(command, stdout=f)
    else:
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE)
        pipe.wait()
        command = subprocess.Popen(['convert', '-', out], stdin=pipe)

    command.wait()


SCANNERS = get_scanners()
try:
    PREVIEW_EXISTS = subprocess.check_output(['convert', '-version'])
except FileNotFoundError:
    PREVIEW_EXISTS = False


if __name__ == "__main__":
    app.run()
