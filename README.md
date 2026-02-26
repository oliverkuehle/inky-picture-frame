# E-Ink Display

A Flask web app for pushing images and text to an **Inky Impression 7.3"** e-ink display via a Raspberry Pi.

## Features

- Upload images or write text (or both) to display on the e-ink screen
- History timeline of all past frames, re-sendable with one tap
- Single shared password, works on desktop and mobile

## Setup

1. Clone the repo onto the Raspberry Pi
2. Create `config.py` (see `CLAUDE.md` for the template)
3. Activate the virtualenv and run:

```bash
source ~/.virtualenvs/pimoroni/bin/activate
python app.py
```

## Preview

<table>
<tr>
<td><img src="https://github.com/oliverkuehle/inky-picture-frame/blob/master/preview-image.jpg?raw=true" width=400></td>
<td><img src="https://github.com/oliverkuehle/inky-picture-frame/blob/master/preview-image-outside.jpg?raw=true" width=400></td>
</tr>
</table>