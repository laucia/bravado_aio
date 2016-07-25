import asyncio
import atexit
import logging
from concurrent.futures import ThreadPoolExecutor

import uvloop
import simplejson
from aiohttp import ClientSession
from bravado_core.response import IncomingResponse
from bravado.http_client import HttpClient
from bravado.http_future import HttpFuture


log = logging.getLogger(__name__)


def _run_offloaded(loop):
    """ Make current and run the event loop until stopped.
    This function is made to run in a separate thread.

    :param loop: asyncio EventLoop implemtation
    :type loop: :class:`asyncio.AbstractEventLoop`
    """
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    finally:
        loop.run_until_completed(cancel_all(asyncio.Task.all_tasks(loop=loop)))
        loop.close()


async def request_coroutine(url, method,* , headers=None, data=None, params=None):
    """ Make the network calls, in a coroutine """
    async with ClientSession() as session:
        async with session.request(
            method,
            url,
            headers=headers,
            data=data,
            params=params,
        ) as response:
            r = await response.text()
            return response, r


class AIOResponseAdapter(IncomingResponse):
    """ Wraps a ClientResponse object to provide a uniform interface
    to the response innards.
    :type aio_response: :class:`aiohttp.ClientResponse`
    """
    def __init__(self, aio_response):
        self._response, self._content = aio_response

    @property
    def status_code(self):
        return self._response.status

    @property
    def text(self):
        return self._content

    @property
    def reason(self):
        return self._response.reason

    @property
    def headers(self):
        return self._response.headers

    def json(self, **_):
        return simplejson.loads(self._content)


class AIOClient(HttpClient):
    """ Offloaded asyncio loop HTTPClient implementation """

    def __init__(self):
        self.loop = uvloop.new_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.offloaded_loop_future = self.executor.submit(_run_offloaded, self.loop)

        async def clean_up_coro():
            self.loop.stop()

        def clean_up_threadsafe():
            asyncio.run_coroutine_threadsafe(
                clean_up_coro(),
                self.loop,
            )
        atexit.register(clean_up_threadsafe)

    def request(self, request_params, operation=None, response_callbacks=None,
                also_return_response=False):
        """
        :param request_params: complete request data. e.g. url, method,
            headers, body, params, connect_timeout, timeout, etc.
        :type request_params: dict
        :param operation: operation that this http request is for. Defaults
            to None - in which case, we're obviously just retrieving a Swagger
            Spec.
        :type operation: :class:`bravado_core.operation.Operation`
        :param response_callbacks: List of callables to post-process the
            incoming response. Expects args incoming_response and operation.
        :param also_return_response: Consult the constructor documentation for
            :class:`bravado.http_future.HttpFuture`.
        :returns: HTTP Future object
        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """

        future = asyncio.run_coroutine_threadsafe(
            request_coroutine(
                request_params.get('url'),
                request_params.get('method') or 'GET',
                headers=request_params.get('headers'),
                params=request_params.get('params'),
                data=request_params.get('data'),
            ),
            self.loop
        )
        return HttpFuture(
            future,
            AIOResponseAdapter,
            operation,
            response_callbacks,
            also_return_response,
        )


