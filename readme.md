# Download ISVC Videos

**NOTE:** This script is for entertainment purposes only. You should not use this script to login to the Berkeley ISVC portal or to download videos, nor should you use this script to reverse engineer Kaltura's video platform. Don't run this script, don't download this script, don't look at the source code, in fact just close your browser window now.

## Usage
 
From a command prompt

```git clone https://github.com/lukedoolittle/isvcdownloader.git```
```pip install -r isvcDownloader/requirements.txt```
```python isvcDownloader/isvcDownloader <username> <password> <url containing video>```

## Limitations

There are a host of different formats in the portal. This script works with some but not with others.

Type | Example | Functionality
--- | --- | ---
Straight Video | W201, 1.1 | Works with no problems.
Video with Slides | W201, 1.8 | Records video but doesn't capture content of slides.
Flipbook | W201, 1.4 | Doesn't capture this at all.
Interactive Video | W201, 3.7 | Doesn't capture this at all.