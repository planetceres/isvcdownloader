import requests
import sys
import re
import json
from abc import ABC, abstractmethod
from urllib.parse import urlparse, urljoin, parse_qs
from tqdm import tqdm

class RemoteVideo():
    def __init__(
        self, 
        videoUrl):
            self._videoUrl = videoUrl

    def downloadVideo(
        self, 
        outputFileName):
            response = requests.get(
                downloadEndpoint, 
                stream=True)

            total_size = int(response.headers.get('Content-Length', 0)); 

            with open(outputFileName + '.mp4', 'wb') as videoFile:
                for data in tqdm(response.iter_content(1024), total=int(total_size/(1024)), unit='KB'):
                    videoFile.write(data)

class VideoUrlBase(ABC):
    @abstractmethod
    def getDownloadEndpoint(
        self, 
        videoRefUrl):
        pass

class KalturaVideoUrl(VideoUrlBase):
    MANIFEST_URL_FORMAT = ("https://www.kaltura.com/api_v3/index.php/?" 
                        "service=multirequest&format=9&1:service=session"
                        "&1:action=startWidgetSession&1:widgetId=_{0}"
                        "&2:service=flavorasset&2:action=getByEntryId"
                        "&2:ks=%7B1%3Aresult%3Aks%7D&2:entryId={1}"
                        "&callback=?")
    FINAL_URL_FORMAT = ("https://cdnsecakmi.kaltura.com/p/{0}/sp/{1}/"
                       "playManifest/entryId/{2}/flavorId/{3}/format/"
                       "url/protocol/https/a.mp4")

    def __init__(
        self, 
        quality):
            self._quality = quality

    def getDownloadEndpoint(
        self, 
        videoRefUrl):
            response = requests.get(
                    self.MANIFEST_URL_FORMAT.format(
                        videoRefUrl.netloc, 
                        videoRefUrl.path.split('/')[1]))
            manifest = json.loads(
                response.text.strip('?').strip(';').strip('(').strip(')'))[1]

            #should search for either high or low bitrate depending on quality
            kalturaAsset = [x for x in manifest if x['fileExt'] == 'mp4'][0]
            return self.FINAL_URL_FORMAT.format(
                kalturaAsset['partnerId'], 
                str(kalturaAsset['partnerId']) + '00',
                kalturaAsset['entryId'],
                kalturaAsset['id'])

class AmazonVideoUrl(VideoUrlBase):
    FILENAME_FORMAT = 'mp4_{0}.mp4'

    def __init__(
        self, 
        quality):
            self._quality = quality

    def getDownloadEndpoint(
        self, 
        videoRefUrl):
            return urljoin(
                videoRefUrl.geturl(), 
                self.FILENAME_FORMAT.format(self._quality))

class VideoUrlFactory:
    def generateVideoUrl(
        self, 
        scheme,
        quality):
            if scheme == 'https':
                return AmazonVideoUrl(quality)
            if scheme == 'kaltura':
                return KalturaVideoUrl(quality)
            else:
                raise TypeError(scheme + ' is not supported')

class IsvcSession:
    _session = requests.Session()
    LOGIN_URL = 'https://learn.datascience.berkeley.edu/local/login/index.php'
    VIDEO_REF_REGULAR_EXPRESSION = 'videoRef: "(\S+)"'

    def __init__(
        self, 
        username, 
        password):
            payload={
                'username' : username, 
                'password' : password, 
                'testcookies':'1'
                }

            self._session.post(
                self.LOGIN_URL, 
                data = payload)

    def getVideoRefUrlFromPage(
        self, 
        url):
            response = self._session.get(url)
            matches = re.search(
                self.VIDEO_REF_REGULAR_EXPRESSION, 
                response.text)
            if matches is None:
                raise ValueError('Could not find video reference in page ' + url)
            return urlparse(matches.group(1))


##############################################################################
#
# Main
#
##############################################################################
debug = False

if len(sys.argv) < 4:
    raise ValueError('Usage: python isvcDownloader.py USERNAME PASSWORD VIDEO_URL');

if len(sys.argv) == 5:
    quality = sys.argv[4]
else:
    quality = 'low'

print('Parsing page to extract video url...')

videoRefUrl = (IsvcSession(
                    sys.argv[1], 
                    sys.argv[2])
                .getVideoRefUrlFromPage(
                    sys.argv[3]))

downloadEndpoint = (VideoUrlFactory()
                    .generateVideoUrl(
                        videoRefUrl.scheme, 
                        quality)
                    .getDownloadEndpoint(
                        videoRefUrl))

if not debug:
    print('Downloading from ' + downloadEndpoint)
    videoFileName = parse_qs(urlparse(sys.argv[3]).query)['id'][0]
    RemoteVideo(downloadEndpoint).downloadVideo(videoFileName)
else:
    print(downloadEndpoint)

    