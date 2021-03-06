#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.core.params import ParlaiParser
from parlai.core.agents import create_agent
from parlai.core.worlds import create_task
from parlai.utils.logging import logger, ERROR
import parlai.utils.testing as testing_utils

import os
import unittest

SKIP_TESTS = False
try:
    from parlai.agents.tfidf_retriever.tfidf_retriever import (  # noqa: F401
        TfidfRetrieverAgent,
    )
except ImportError:
    SKIP_TESTS = True


class TestTfidfRetriever(unittest.TestCase):
    """
    Basic tests on the display_data.py example.
    """

    @unittest.skipIf(SKIP_TESTS, "Missing  Tfidf dependencies.")
    def test_sparse_tfidf_retriever(self):
        with testing_utils.tempdir() as tmpdir:
            MODEL_FILE = os.path.join(tmpdir, 'tmp_test_babi')
            # keep things quiet
            logger.setLevel(ERROR)
            parser = ParlaiParser(True, True)
            parser.set_defaults(
                model='tfidf_retriever',
                task='babi:task1k:1',
                model_file=MODEL_FILE,
                retriever_numworkers=4,
                retriever_hashsize=2 ** 8,
                datatype='train:ordered',
                num_epochs=1,
            )
            opt = parser.parse_args([])
            agent = create_agent(opt)
            train_world = create_task(opt, agent)
            # pass examples to dictionary
            while not train_world.epoch_done():
                train_world.parley()

            obs = {
                'text': (
                    'Mary moved to the bathroom. John went to the hallway. '
                    'Where is Mary?'
                ),
                'episode_done': True,
            }
            agent.observe(obs)
            reply = agent.act()
            assert reply['text'] == 'bathroom'

            ANS = 'The one true label.'
            new_example = {
                'text': 'A bunch of new words that are not in the other task, '
                'which the model should be able to use to identify '
                'this label.',
                'labels': [ANS],
                'episode_done': True,
            }
            agent.observe(new_example)
            reply = agent.act()
            assert 'text' in reply and reply['text'] == ANS

            new_example.pop('labels')
            agent.observe(new_example)
            reply = agent.act()
            assert reply['text'] == ANS


if __name__ == '__main__':
    unittest.main()
