import click
import requests
from typing import Optional
from .blockchain.core.chain import Blockchain
from .blockchain.network.p2p import P2PNetwork
from .blockchain.wallet.keystore import SecureKeystore

@click.group()
@click.option('--node', default='http://localhost:8080', help='Node RPC endpoint')
@click.pass_context
def cli(ctx, node):
    """
    CLI entry point for the blockchain application.
    """
    ctx.obj = {
        'blockchain': Blockchain(),
        'network': P2PNetwork(config={}),
        'keystore': SecureKeystore(),
        'node': node  # Store node URL in context object
    }

@cli.command()
@click.option('--password', prompt=True, hide_input=True)
@click.pass_context
def init(ctx, password):
    """
    Initialize the wallet with a password.
    """
    try:
        ctx.obj['keystore'].initialize(password)
        click.echo("Wallet initialized successfully")
    except Exception as e:
        click.echo(f"Error initializing wallet: {e}")

@cli.command()
@click.argument('receiver')
@click.argument('amount', type=float)
@click.pass_context
def send(ctx, receiver, amount):
    """
    Send a transaction to the specified receiver.
    """
    try:
        tx = create_transaction(receiver, amount)
        response = requests.post(f"{ctx.obj['node']}/api/v1/transactions", json=tx)
        response.raise_for_status()  # Check for HTTP request errors
        click.echo(f"Transaction submitted: {response.json()}")
    except requests.RequestException as e:
        click.echo(f"Error submitting transaction: {e}")

@cli.command()
@click.pass_context
def mine(ctx):
    """
    Start mining a new block.
    """
    try:
        result = requests.post(f"{ctx.obj['node']}/api/v1/mine")
        result.raise_for_status()  # Check for HTTP request errors
        click.echo(f"Mined block: {result.json()}")
    except requests.RequestException as e:
        click.echo(f"Error mining block: {e}")

def create_transaction(receiver, amount):
    """
    Helper function to create a transaction.
    """
    # Placeholder function: replace with actual transaction creation logic
    return {
        'receiver': receiver,
        'amount': amount,
        'sender': 'your_address_here',
        'signature': 'your_signature_here'
    }

if __name__ == '__main__':
    cli()
