"""
/*********************************************************************
* Copyright (c) 2023 the Qrisp Authors
*
* This program and the accompanying materials are made
* available under the terms of the Eclipse Public License 2.0
* which is available at https://www.eclipse.org/legal/epl-2.0/
*
* SPDX-License-Identifier: EPL-2.0
**********************************************************************/
"""

"""
    Cyqlone-Backend Interface

    An API specification for interfacing the high-level language Cyqlone to backend providers.  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


import sys
import unittest

import openapi_client
from openapi_client.model.clbit import Clbit
from openapi_client.model.instruction import Instruction
from openapi_client.model.qubit import Qubit

globals()["Clbit"] = Clbit
globals()["Instruction"] = Instruction
globals()["Qubit"] = Qubit
from openapi_client.model.quantum_circuit import QuantumCircuit


class TestQuantumCircuit(unittest.TestCase):
    """QuantumCircuit unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testQuantumCircuit(self):
        """Test QuantumCircuit"""
        # FIXME: construct object with mandatory attributes with example values
        # model = QuantumCircuit()  # noqa: E501
        pass


if __name__ == "__main__":
    unittest.main()