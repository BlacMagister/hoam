def test_genesis_block(test_chain):
    assert len(test_chain.chain) == 1
    assert test_chain.last_block.header.difficulty == 0

def test_add_block(test_chain):
    new_block = Block(
        BlockHeader(
            version=1,
            previous_hash=test_chain.last_block.hash,
            merkle_root=b'\x00'*32,
            timestamp=time.time(),
            difficulty=4,
            nonce=0
        ),
        transactions=[]
    )
    test_chain.chain.append(new_block)
    assert len(test_chain.chain) == 2
