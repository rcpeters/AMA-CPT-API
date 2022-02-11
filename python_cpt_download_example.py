import os, json, requests, datetime
import re
import zipfile

from email.utils import parsedate_to_datetime
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import InvalidClientError
from requests_oauthlib import OAuth2Session


client_id = os.environ["CLIENT_KEY"]
client_secret = os.environ["CLIENT_SECRET"]


def catch_exception_decorator(func):
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except requests.exceptions.HTTPError as err:
            print(f"HTTPError code {err.response.status_code}")
            print(f"HTTPError reason {err.response.reason}")
            print(f"HTTPError text {err.response.text}")
            raise
        except InvalidClientError as err:
            print(f"HTTPError code {err.status_code}")
            print(f"URL encoded {err.urlencoded}")
            raise

    return inner_function


class CptClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = BackendApplicationClient(client_id=self.client_id)
        self.oauth = OAuth2Session(client=self.client)

    def __header_last_mod(self, response):
        return parsedate_to_datetime(response.headers["Last-Modified"]).timestamp()

    def __correct_last_mod(self, filepath, lastMod):
        now = datetime.datetime.now().timestamp()
        # write last modifed
        os.utime(filepath, (now, lastMod))

    # terrible hack to deal with missmatches in the first
    # version of the API
    def __cpt_pub_date(self, zippath):
        file = zipfile.ZipFile(zippath, "r")
        r = re.compile("AMA/CPT/\d{8}/")
        first = list(filter(r.match, file.namelist()))[0]
        pub_date = first.split("/")[2]
        file.close()
        return pub_date

    @catch_exception_decorator
    def get_auth(self):
        return self.oauth.fetch_token(
            token_url="https://api-platform.ama-assn.org/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    @catch_exception_decorator
    def get_releases(self, dnldDdir):
        filepath = dnldDdir + "release.txt"
        self.get_auth()
        response = self.oauth.get(
            "https://api-platform.ama-assn.org/cpt-zip/1.0.0/releases"
        )
        response.raise_for_status()
        release_json = json.loads(response.content)
        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(release_json, indent=4))
            outfile.close()
        # self.__correct_last_mod(filepath, response)
        return response.content

    @catch_exception_decorator
    def get_files(self, dnldDdir):
        tempFilePath = dnldDdir + "ama_cpt_temp.zip"
        latestFilePath = dnldDdir + "ama_cpt_latest.zip"

        self.get_auth()
        response = self.oauth.get(
            "https://api-platform.ama-assn.org/cpt-zip/1.0.0/files", stream=True
        )
        response.raise_for_status()

        hLastMod = self.__header_last_mod(response)
        fLastMod = file_exists = (
            os.path.getmtime(latestFilePath) if os.path.exists(latestFilePath) else 0
        )

        # write content if newer content is available
        if hLastMod > fLastMod:
            tempzip = open(tempFilePath, "wb")
            tempzip.write(response.content)
            tempzip.close()

            # keep last mod from server
            self.__correct_last_mod(tempFilePath, hLastMod)

            # create file names with pub date extracted from file
            cpt_pub_date = self.__cpt_pub_date(tempFilePath)
            filePath = dnldDdir + "ama_cpt_" + cpt_pub_date + ".zip"
            os.replace(tempFilePath, filePath)

            # create a easy to reference symlink
            # also hack for atom file symlinking
            # https://stackoverflow.com/questions/8299386/modifying-a-symlink-in-python
            tempSymFilePath = latestFilePath + "_tmp"
            os.link(filePath, tempSymFilePath)
            os.replace(tempSymFilePath, latestFilePath)

        return latestFilePath


cptClient = CptClient(client_id, client_secret)

# releases_response = cptClient.get_releases(dnldDdir="downloads/")

releases_files_loc = cptClient.get_files(dnldDdir="downloads/")
print(releases_files_loc)
