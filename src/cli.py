import click
from typing import Optional
from .blockchain.core.chain import Blockchain
from .blockchain.network.p2p import P2PNetwork
from .blockchain.wallet.keystore import SecureKeystore

@click.group()
@click.option('--node', default='http://localhost:8080', help='Node RPC endpoint')
@click.pass_context
def cli(ctx, node):
    ctx.obj = {
        'blockchain': Blockchain(),
        'network': P2PNetwork(config={}),
        'keystore': SecureKeystore()
    }

@cli.command()
@click.option('--password', prompt=True, hide_input=True)
def init(password):
    ctx.obj['keystore'].initialize(password)
    click.echo("Wallet initialized successfully")

@cli.command()
@click.argument('receiver')
@click.argument('amount', type=float)
def send(receiver, amount):
    tx = create_transaction(receiver, amount)
    response = requests.post(f"{ctx.obj['node']}/api/v1/transactions", json=tx)
    click.echo(f"Transaction submitted: {response.json()}")

@cli.command()
def mine():
    result = requests.post(f"{ctx.obj['node']}/api/v1/mine")
    click.echo(f"Mined block: {result.json()}")

if __name__ == '__main__':
    cli()
