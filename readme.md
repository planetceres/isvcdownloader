# Download ISVC Videos

**NOTE:** This script is for entertainment purposes only. You should not use this script to login to the Berkeley ISVC portal or to download videos, nor should you use this script to reverse engineer Kaltura's video platform. Don't run this script, don't download this script, don't look at the source code, in fact just close your browser window now.

## Usage

From a command prompt

    git clone https://github.com/lukedoolittle/isvcdownloader.git
    pip3 install -r isvcDownloader/requirements.txt
    python3 isvcDownloader/isvcDownloader.py '<username>' '<password>' '<url containing video>'

Ensure that the '' around the password argument are present especially if your password has special characters

## For Multiple Videos

Choose directory to download videos to by modifying the `SAVE_DIR` variable in `isvcBulkDownloader.py`. Then, from command prompt

    python3 isvcDownloader/isvcBulkDownloader.py '<username>' '<password>' '<base url containing video without video id string at end>' '<start video id>' '<end video id>'

## Limitations

There are a host of different presentation formats in the ISVC portal. This script works with some but not with others. That said it could be modified to extract the additional formats.

Type | Example | Functionality
--- | --- | ---
Straight Video | W201, 1.1 | Works with no problems.
Video with Slides | W201, 1.8 | Records video but doesn't capture content of slides.
Flipbook | W201, 1.4 | Doesn't capture this at all.
Interactive Video | W201, 3.7 | Doesn't capture this at all.
