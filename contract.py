#! /usr/bin/env python

import click
from web3 import Web3


@click.group()
def cli():
    pass


@cli.command()
@click.option('--gas', type=int)
@click.option('--gas-price', type=int, default=None)
@click.argument('private_key')
@click.argument('abi', type=click.File())
@click.argument('bytecode', type=click.File())
@click.argument('args', nargs=-1)
def deploy(abi, bytecode, private_key, gas, gas_price, args):
    w3 = Web3()
    contract = w3.eth.contract(
        abi=abi.read(),
        bytecode=bytecode.read())
    account = w3.eth.account.from_key(private_key)

    cc = contract.constructor(*map(eval, args))
    tx = build_transaction(cc, account, w3, gas, gas_price)
    signed = w3.eth.account.sign_transaction(tx, account.key)
    txn = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(w3.toHex(txn))


@cli.command()
@click.option('--private-key')
@click.option('--gas', type=int)
@click.option('--gas-price', type=int, default=None)
@click.option('--value', type=int)
@click.argument('address')
@click.argument('abi', type=click.File())
@click.argument('method')
@click.argument('args', nargs=-1)
def invoke(private_key, gas, gas_price, value, address, abi, method, args):
    w3 = Web3()
    contract = w3.eth.contract(address, abi=abi.read())
    fn = contract.functions[method](*map(eval, args))

    if private_key is None:
        print(fn.call())
        return

    account = w3.eth.account.from_key(private_key)
    tx = build_transaction(fn, account, w3, gas, gas_price, value)
    signed = w3.eth.account.sign_transaction(tx, account.key)
    txn = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(w3.toHex(txn))


def build_transaction(fn, account, web3, gas=None, gas_price=None, value=None):
    return fn.buildTransaction({
        **({} if value is None else {'value': value}),
        'gas': gas or fn.estimateGas(),
        'gasPrice': gas_price or web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(account.address),
    })


if __name__ == '__main__':
    cli()
