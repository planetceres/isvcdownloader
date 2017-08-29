import requests
import sys
import re
import json
from abc import ABC, abstractmethod
from urllib.parse import urlparse, urljoin, parse_qs
from tqdm import tqdm
import os.path

SAVE_DIR = "./downloads/course/unit"

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

            if not os.path.exists(SAVE_DIR):
                os.makedirs(SAVE_DIR)

            with open(SAVE_DIR + '/' + outputFileName + '.mp4', 'wb') as videoFile:
                for data in tqdm(response.iter_content(1024), total=int(total_size/(1024)), unit='KB'):
                    videoFile.write(data)

class VideoUrlBase(ABC):
    @abstractmethod
    def getDownloadEndpoint(
        self,
        videoRefUrl):
        pass

class KalturaVideoUrl(VideoUrlBase):


    def __init__(
        self,
        quality):
            self.MANIFEST_URL_FORMAT = ("https://www.kaltura.com/api_v3/index.php/?"
                                "service=multirequest&format=9&1:service=session"
                                "&1:action=startWidgetSession&1:widgetId=_{0}"
                                "&2:service=flavorasset&2:action=getByEntryId"
                                "&2:ks=%7B1%3Aresult%3Aks%7D&2:entryId={1}"
                                "&callback=Callback") #"&callback=?")
            self.FINAL_URL_FORMAT = ("https://cdnsecakmi.kaltura.com/p/{0}/sp/{1}/"
                               "playManifest/entryId/{2}/flavorId/{3}/format/"
                               "url/protocol/https/a.mp4")
            self._quality = quality

    def getDownloadEndpoint(
        self,
        videoRefUrl):
            print(str(self.MANIFEST_URL_FORMAT.format(
                videoRefUrl.netloc,
                videoRefUrl.path.split('/')[1])))
            response = requests.get(
                    self.MANIFEST_URL_FORMAT.format(
                        videoRefUrl.netloc,
                        videoRefUrl.path.split('/')[1]))

            manifest = json.loads(
                #response.text.strip('?').strip(';').strip('(').strip(')'))[1]
                response.text.strip('Callback').strip(';').strip('(').strip(')'))[1]

            #should search for either high or low bitrate depending on quality
            kalturaAsset = [x for x in manifest if x['fileExt'] == 'mp4'][0]
            return self.FINAL_URL_FORMAT.format(
                kalturaAsset['partnerId'],
                str(kalturaAsset['partnerId']) + '00',
                kalturaAsset['entryId'],
                kalturaAsset['id'])

class AmazonVideoUrl(VideoUrlBase):


    def __init__(
        self,
        quality):
            self.FILENAME_FORMAT = 'mp4_{0}.mp4'
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


    def __init__(
        self,
        username,
        password):
            self._session = requests.Session()
            self.LOGIN_URL = 'https://learn.datascience.berkeley.edu/local/login/index.php'
            self.VIDEO_REF_REGULAR_EXPRESSION = 'videoRef: "(\S+)"'
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

if len(sys.argv) < 6:
    raise ValueError('Usage: python isvcDownloader.py USERNAME PASSWORD VIDEO_URL START_IDX END_IDX');

if len(sys.argv) == 7:
    quality = sys.argv[6]
else:
    quality = 'low'

print('Parsing page to extract video url...')

start_idx = int(sys.argv[4])
end_idx = int(sys.argv[5])
baseUrl = str(sys.argv[3])
idx = start_idx
idxRange = end_idx - start_idx
for i in range(idxRange + 1):
    videoUrlId = baseUrl + str(idx)

    try:
        print("Trying: {0}".format(videoUrlId))
        videoRefUrl = (IsvcSession(
                            sys.argv[1],
                            sys.argv[2])
                        .getVideoRefUrlFromPage(
                            videoUrlId))

        downloadEndpoint = (VideoUrlFactory()
                            .generateVideoUrl(
                                videoRefUrl.scheme,
                                quality)
                            .getDownloadEndpoint(
                                videoRefUrl))

        if not debug:
            print('Downloading from ' + downloadEndpoint)
            videoFileName = parse_qs(urlparse(videoUrlId).query)['id'][0]
            RemoteVideo(downloadEndpoint).downloadVideo(videoFileName)
        else:
            print(downloadEndpoint)

    except Exception as e:
        print("Error retrieving {0}\nurl may not contain downloadable media ".format(videoUrlId))
        print(e)
    idx += 1
