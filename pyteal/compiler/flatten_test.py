from .. import *

from .flatten import flattenBlocks

def test_flatten_none():
    blocks = []

    expected = []
    actual = flattenBlocks(blocks)

    assert actual == expected

def test_flatten_single_empty():
    blocks = [
        TealSimpleBlock([])
    ]

    expected = []
    actual = flattenBlocks(blocks)

    assert actual == expected

def test_flatten_single_one():
    blocks = [
        TealSimpleBlock([TealOp(None, Op.int, 1)])
    ]

    expected = [TealOp(None, Op.int, 1)]
    actual = flattenBlocks(blocks)

    assert actual == expected

def test_flatten_single_many():
    blocks = [
        TealSimpleBlock([
            TealOp(None, Op.int, 1),
            TealOp(None, Op.int, 2),
            TealOp(None, Op.int, 3),
            TealOp(None, Op.add),
            TealOp(None, Op.add)
        ])
    ]

    expected = [
        TealOp(None, Op.int, 1),
        TealOp(None, Op.int, 2),
        TealOp(None, Op.int, 3),
        TealOp(None, Op.add),
        TealOp(None, Op.add)
    ]
    actual = flattenBlocks(blocks)

    assert actual == expected

def test_flatten_sequence():
    block5 = TealSimpleBlock([TealOp(None, Op.int, 5)])
    block4 = TealSimpleBlock([TealOp(None, Op.int, 4)])
    block4.setNextBlock(block5)
    block3 = TealSimpleBlock([TealOp(None, Op.int, 3)])
    block3.setNextBlock(block4)
    block2 = TealSimpleBlock([TealOp(None, Op.int, 2)])
    block2.setNextBlock(block3)
    block1 = TealSimpleBlock([TealOp(None, Op.int, 1)])
    block1.setNextBlock(block2)
    block1.addIncoming()
    block1.validateTree()
    blocks = [block1, block2, block3, block4, block5]

    expected = [
        TealOp(None, Op.int, 1),
        TealOp(None, Op.int, 2),
        TealOp(None, Op.int, 3),
        TealOp(None, Op.int, 4),
        TealOp(None, Op.int, 5)
    ]
    actual = flattenBlocks(blocks)

    assert actual == expected

def test_flatten_branch():
    blockTrue = TealSimpleBlock([TealOp(None, Op.byte, "\"true\""), TealOp(None, Op.return_)])
    blockFalse = TealSimpleBlock([TealOp(None, Op.byte, "\"false\""), TealOp(None, Op.return_)])
    block = TealConditionalBlock([TealOp(None, Op.int, 1)])
    block.setTrueBlock(blockTrue)
    block.setFalseBlock(blockFalse)
    block.addIncoming()
    block.validateTree()
    blocks = [block, blockFalse, blockTrue]

    expected = [
        TealOp(None, Op.int, 1),
        TealOp(None, Op.bnz, "l2"),
        TealOp(None, Op.byte, "\"false\""),
        TealOp(None, Op.return_),
        TealLabel(None, "l2"),
        TealOp(None, Op.byte, "\"true\""),
        TealOp(None, Op.return_)
    ]
    actual = flattenBlocks(blocks)

    assert actual == expected

def test_flatten_branch_converge():
    blockEnd = TealSimpleBlock([TealOp(None, Op.return_)])
    blockTrue = TealSimpleBlock([TealOp(None, Op.byte, "\"true\"")])
    blockTrue.setNextBlock(blockEnd)
    blockFalse = TealSimpleBlock([TealOp(None, Op.byte, "\"false\"")])
    blockFalse.setNextBlock(blockEnd)
    block = TealConditionalBlock([TealOp(None, Op.int, 1)])
    block.setTrueBlock(blockTrue)
    block.setFalseBlock(blockFalse)
    block.addIncoming()
    block.validateTree()
    blocks = [block, blockFalse, blockTrue, blockEnd]

    expected = [
        TealOp(None, Op.int, 1),
        TealOp(None, Op.bnz, "l2"),
        TealOp(None, Op.byte, "\"false\""),
        TealOp(None, Op.b, "l3"),
        TealLabel(None, "l2"),
        TealOp(None, Op.byte, "\"true\""),
        TealLabel(None, "l3"),
        TealOp(None, Op.return_)
    ]
    actual = flattenBlocks(blocks)

    assert actual == expected

def test_flatten_multiple_branch():
    blockTrueTrue = TealSimpleBlock([TealOp(None, Op.byte, "\"true true\""), TealOp(None, Op.return_)])
    blockTrueFalse = TealSimpleBlock([TealOp(None, Op.byte, "\"true false\""), TealOp(None, Op.err)])
    blockTrueBranch = TealConditionalBlock([])
    blockTrueBranch.setTrueBlock(blockTrueTrue)
    blockTrueBranch.setFalseBlock(blockTrueFalse)
    blockTrue = TealSimpleBlock([TealOp(None, Op.byte, "\"true\"")])
    blockTrue.setNextBlock(blockTrueBranch)
    blockFalse = TealSimpleBlock([TealOp(None, Op.byte, "\"false\""), TealOp(None, Op.return_)])
    block = TealConditionalBlock([TealOp(None, Op.int, 1)])
    block.setTrueBlock(blockTrue)
    block.setFalseBlock(blockFalse)
    block.addIncoming()
    block.validateTree()
    blocks = [block, blockFalse, blockTrue, blockTrueBranch, blockTrueFalse, blockTrueTrue]
    
    expected = [
        TealOp(None, Op.int, 1),
        TealOp(None, Op.bnz, "l2"),
        TealOp(None, Op.byte, "\"false\""),
        TealOp(None, Op.return_),
        TealLabel(None, "l2"),
        TealOp(None, Op.byte, "\"true\""),
        TealOp(None, Op.bnz, "l5"),
        TealOp(None, Op.byte, "\"true false\""),
        TealOp(None, Op.err),
        TealLabel(None, "l5"),
        TealOp(None, Op.byte, "\"true true\""),
        TealOp(None, Op.return_)
    ]
    actual = flattenBlocks(blocks)

    assert actual == expected

def test_flatten_multiple_branch_converge():
    blockEnd = TealSimpleBlock([TealOp(None, Op.return_)])
    blockTrueTrue = TealSimpleBlock([TealOp(None, Op.byte, "\"true true\"")])
    blockTrueTrue.setNextBlock(blockEnd)
    blockTrueFalse = TealSimpleBlock([TealOp(None, Op.byte, "\"true false\""), TealOp(None, Op.err)])
    blockTrueBranch = TealConditionalBlock([])
    blockTrueBranch.setTrueBlock(blockTrueTrue)
    blockTrueBranch.setFalseBlock(blockTrueFalse)
    blockTrue = TealSimpleBlock([TealOp(None, Op.byte, "\"true\"")])
    blockTrue.setNextBlock(blockTrueBranch)
    blockFalse = TealSimpleBlock([TealOp(None, Op.byte, "\"false\"")])
    blockFalse.setNextBlock(blockEnd)
    block = TealConditionalBlock([TealOp(None, Op.int, 1)])
    block.setTrueBlock(blockTrue)
    block.setFalseBlock(blockFalse)
    block.addIncoming()
    block.validateTree()
    blocks = [block, blockFalse, blockTrue, blockTrueBranch, blockTrueFalse, blockTrueTrue, blockEnd]
    
    expected = [
        TealOp(None, Op.int, 1),
        TealOp(None, Op.bnz, "l2"),
        TealOp(None, Op.byte, "\"false\""),
        TealOp(None, Op.b, "l6"),
        TealLabel(None, "l2"),
        TealOp(None, Op.byte, "\"true\""),
        TealOp(None, Op.bnz, "l5"),
        TealOp(None, Op.byte, "\"true false\""),
        TealOp(None, Op.err),
        TealLabel(None, "l5"),
        TealOp(None, Op.byte, "\"true true\""),
        TealLabel(None, "l6"),
        TealOp(None, Op.return_)
    ]
    actual = flattenBlocks(blocks)

    assert actual == expected
