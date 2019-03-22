# TODO: Check without node installed
# cfscrape is a necessery dependency
import cfscrape
import logging
from bs4 import BeautifulSoup
import tempfile
import os
import requests

from anime_downloader import session
from anime_downloader.const import get_random_header

__all__ = [
    'get',
    'post',
    'soupify',
]

logger = logging.getLogger(__name__)

req_session = session.get_session()
cf_session = cfscrape.create_scraper(sess=req_session)
default_headers = get_random_header()
temp_dir = tempfile.mkdtemp(prefix='animedl')


def setup(func):
    """
    setup is a decorator which takes a function
    and converts it into a request method
    """
    def setup_func(url: str,
                   cf: bool = True,
                   referer: str = None,
                   headers=None,
                   **kwargs):
        '''
        {0} performs a {0} request

        Parameters
        ----------
        url : str
            url is the url of the request to be performed
        cf : bool
            cf if True performs the request through cfscrape.
            For cloudflare protected sites.
        referer : str
            a url sent as referer in request headers
        '''
        sess = cf_session if cf else req_session
        if headers:
            default_headers.update(headers)
        if referer:
            default_headers['Referer'] = referer

        logger.debug('-----')
        logger.debug('{} {}'.format(func.__name__.upper(), url))
        logger.debug(kwargs)
        logger.debug(default_headers)
        logger.debug('-----')

        res = sess.request(func.__name__.upper(),
                           url,
                           headers=default_headers,
                           **kwargs)
        res.raise_for_status()
        # logger.debug(res.text)
        if logger.getEffectiveLevel() == logging.DEBUG:
            _log_response_body(res)
        return res
    setup_func.__doc__ = setup_func.__doc__.format(func.__name__)
    return setup_func


@setup
def get(url: str,
        cf: bool = True,
        referer: str = None,
        headers=None,
        **kwargs):
    '''
    get performs a get request

    Parameters
    ----------
    url : str
        url is the url of the request to be performed
    cf : bool
        cf if True performs the request through cfscrape.
        For cloudflare protected sites.
    referer : str
        a url sent as referer in request headers
    '''


@setup
def post(url: str,
         cf: bool = True,
         referer: str = None,
         headers=None,
         **kwargs):
    '''
    post performs a post request

    Parameters
    ----------
    url : str
        url is the url of the request to be performed
    cf : bool
        cf if True performs the request through cfscrape.
        For cloudflare protected sites.
    referer : str
        a url sent as referer in request headers
    '''


def soupify(res):
    # TODO: res datatype
    """soupify Beautiful soups response object of request

    Parameters
    ----------
    res :
        res is `request.response`

    Returns
    -------
    BeautifulSoup.Soup
    """
    if isinstance(res, requests.Response):
        res = res.text
    soup = BeautifulSoup(res, 'html.parser')
    return soup


def _log_response_body(res):
    import json
    file = tempfile.mktemp(dir=temp_dir)
    logger.debug(file)
    with open(file, 'w') as f:
        f.write(res.text)

    data_file = temp_dir + '/data.json'
    if not os.path.exists(data_file):
        with open(data_file, 'w') as f:
            json.dump([], f)
    data = None
    with open(data_file, 'r') as f:
        data = json.load(f)
        data.append({
            'method': res.request.method,
            'url': res.url,
            'file': '/' + file.split('/')[-1],
        })
    with open(data_file, 'w') as f:
        json.dump(data, f)
