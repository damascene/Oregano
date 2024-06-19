from .util import poll_for_answer, get_bitcoind_rpc_connection, EC_DAEMON_RPC_URL, docker_compose_file, fulcrum_service, SUPPORTED_PLATFORM

import pytest
from typing import Any

from jsonrpcclient import request

@pytest.mark.skipif(not SUPPORTED_PLATFORM, reason="Unsupported platform")
def test_getunusedaddress(fulcrum_service: Any) -> None:
    """ Verify the `getunusedaddress` RPC """
    address = poll_for_answer(EC_DAEMON_RPC_URL, request('getunusedaddress'))

    # The daemon does not return a prefix.
    # Check that the length is 42 and starts with 'q'
    assert len(address) == 42
    assert address[0] == 'q'
    same_address = poll_for_answer(EC_DAEMON_RPC_URL, request('getunusedaddress'))
    assert address == same_address

@pytest.mark.skipif(not SUPPORTED_PLATFORM, reason="Unsupported platform")
def test_getservers(fulcrum_service: Any) -> None:
    """ Verify the `getservers` RPC """
    result = poll_for_answer(EC_DAEMON_RPC_URL, request('getservers'))

    # Only one server in this setup
    assert len(result) == 1

@pytest.mark.skipif(not SUPPORTED_PLATFORM, reason="Unsupported platform")
def test_balance(fulcrum_service: Any) -> None:
    """ Verify the `getbalance` RPC """
    addr = poll_for_answer(EC_DAEMON_RPC_URL, request('getunusedaddress'))

    bitcoind = get_bitcoind_rpc_connection()

    bitcoind.generatetoaddress(1, addr)
    result = poll_for_answer(EC_DAEMON_RPC_URL, request('getbalance'), expected_answer=('unmatured', '50'))
    assert result['unmatured'] == '50'

    bitcoind.sendtoaddress(addr, 10)
    result = poll_for_answer(EC_DAEMON_RPC_URL, request('getbalance'), expected_answer=('unconfirmed', '10'))
    assert result['unmatured'] == '50' and result['unconfirmed'] == '10'

    bitcoind.generate(1)
    result = poll_for_answer(EC_DAEMON_RPC_URL, request('getbalance'), expected_answer=('confirmed', '10'))
    assert result['unmatured'] == '50' and result['confirmed'] == '10'

    bitcoind.generate(97)
    bitcoind.sendtoaddress(addr, 10)
    result = poll_for_answer(EC_DAEMON_RPC_URL, request('getbalance'), expected_answer=('unconfirmed', '10'))
    assert result['unmatured'] == '50' and result['confirmed'] == '10' and result['unconfirmed'] == '10'

    bitcoind.generate(1)
    result = poll_for_answer(EC_DAEMON_RPC_URL, request('getbalance'), expected_answer=('confirmed', '70'))
    assert result['confirmed'] == '70'
