''' Colection if Provider which deal with HTTP. '''
import os
from abc import abstractmethod

import requests

from .provider import Provider


class HTTPProvider(Provider):
    ''' Abstract class as a foundation how HTTPProvider should work'''
    protocol = 'http'

    @classmethod
    @abstractmethod
    def can_open(cls, url: str) -> bool:
        return cls.identifier in url and url.startswith(cls.protocol)

    @classmethod
    @abstractmethod
    def _pre_url_modify(cls, url: str) -> str:
        return url

    @classmethod
    @abstractmethod
    def _get_page_unauthorized(cls, url: str):
        return requests.get(url)

    @classmethod
    @abstractmethod
    def _get_page_authorized(cls, url: str):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_page(cls, url: str) -> str:
        url = cls._pre_url_modify(url)

        respons = cls._get_page_unauthorized(url)
        if respons.status_code == requests.codes.unauthorized:
            respons = cls._get_page_authorized(url)

        if respons.status_code != requests.codes.ok:
            logger.error(f"Could not download {url}")
            raise SystemExit(f"Could not download {url}")

        return respons.text


class GenericHTTPProvider(HTTPProvider):
    ''' Generic Provider which can get all http without authentication'''
    @classmethod
    def can_open(cls, url):
        return url.startswith(cls.protocol)


class GitHubHTTPProvider(HTTPProvider):
    ''' Provider which can get pages from GitHub'''
    identifier = "github.com"

    @classmethod
    def _pre_url_modify(cls, url):
        url = url.replace("/blob/", "/")
        url = url.replace("/raw/", "/")
        url = url.replace("github.com/", "raw.githubusercontent.com/")
        return url

    @classmethod
    def _get_page_authorized(cls, url):
        token = os.getenv('GITHUB_TOKEN', '...')
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3.raw'}
        return requests.get(url, headers=headers)


class BitBucketHTTPProvider(HTTPProvider):
    ''' Provider which can get pages from BitBucket'''
    identifier = "bitbucket.org"

    @classmethod
    def _pre_url_modify(cls, url):
        return url.replace(
            "bitbucket.org/",
            "api.bitbucket.org/2.0/repositories/"
        )

    @classmethod
    def _get_page_authorized(cls, url):
        username = os.getenv('BITBUCKET_USERNAME', '...')
        password = os.getenv('BITBUCKET_APP_PASSWORD', '...')
        return requests.get(url, auth=(username, password))


class GitlabHTTPProvider(HTTPProvider):
    ''' Provider which can get pages from GitLab'''
    identifier = "gitlab.com"

    # todo: complete the private section with help of below link
    # https://docs.gitlab.com/ee/api/repository_files.html#get-raw-file-from-repository

    @classmethod
    def _pre_url_modify(cls, url):
        return url.replace("blob", "raw")

    @classmethod
    def _get_page_authorized(cls, url):
        token = os.getenv('GITLAB_TOKEN', '...')
        headers = {'PRIVATE-TOKEN': token}
        return requests.get(url, headers=headers)
