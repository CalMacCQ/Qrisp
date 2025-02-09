"""
\********************************************************************************
* Copyright (c) 2023 the Qrisp authors
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* This Source Code may also be made available under the following Secondary
* Licenses when the conditions for such availability set forth in the Eclipse
* Public License, v. 2.0 are satisfied: GNU General Public License, version 2
* with the GNU Classpath Exception which is
* available at https://www.gnu.org/software/classpath/license.html.
*
* SPDX-License-Identifier: EPL-2.0 OR GPL-2.0 WITH Classpath-exception-2.0
********************************************************************************/
"""

import numpy as np
from scipy.optimize import minimize
from sympy import Symbol

from qrisp import QuantumVariable, h, barrier, rz, rx , cx, QuantumArray, xxyy, p, invert, conjugate, mcp

def RX_mixer(qv, beta):
    """
    Applies an RX gate to each qubit in ``qv``.

    The RX gate is a single-qubit rotation about the x-axis. It is used as a mixer in QAOA to drive transitions between different states.

    Parameters
    ----------
    qv : QuantumVariable
        The quantum variable to which the RX gate is applied.
    beta : float or sympy.Symbol
        The phase shift value for the RX gate.

    Returns
    -------
    qv : QuantumVariable
        The quantum variable after applying the RX gate.
    """
    for i in range(qv.size):
        rx(2 * beta, qv[i])
    return qv


def XY_mixer(qv, beta):
    """
    Applies multiple XX+YY gates to ``qv`` such that each qubit has interacted with it's neighbour atleast once.

    The XX+YY gate is a two-qubit gate that performs rotations around the XY plane. It is used as a mixer in QAOA to drive transitions between different states.
    
    A defining feature of this mixer is the fact, that it keeps the number of ones (or equivalently zeros) in the binary representation of the state invariant.

    Parameters
    ----------
    qv : QuantumVariable
        The quantum variable to which the XY gate is applied.
    beta : float or sympy.Symbol
        The phase shift value for the XY gate.

    Returns
    -------
    qv : QuantumVariable
        The quantum variable after applying the XY gate.
    """
    N = qv.size
    
    for i in range(1, N-2, 2):
        xxyy(4*beta, 0, qv[N-2-i], qv[N-1-i])
    
    for i in range(0, N-1, 2):
        xxyy(4*beta, 0, qv[N-2-i], qv[N-1-i])
        
    xxyy(4*beta, 0, qv[N-1], qv[0])

    return qv


def apply_XY_mixer(quantumcolor_array, beta):
    for qcolor in quantumcolor_array:
       XY_mixer(qcolor, beta)
    return quantumcolor_array


def RZ_mixer(qv, beta):
    """
    This function applies an RZ gate with a negative phase shift to a given quantum variable.

    Parameters
    ----------
    qv : QuantumVariable
        The quantum variable to which the RZ gate is applied.
    beta : float or sympy.Symbol
        The phase shift value for the RZ gate.

    """
    rz(-beta, qv)
    
def grover_mixer(qv, beta):
    """
    Performs the parametrized Grover diffuser.

    Parameters
    ----------
    qv : QuantumVariable
        The QuantumVariable to be mixed.
    beta : float or sympy.Symbol
        The mixing parameter.

    """
    
    
    from qrisp.grover import diffuser
    diffuser(qv, phase = beta)
    
def constrained_mixer_gen(constraint_oracle, winner_state_amount):
    r"""
    Generates a customized mixer function that leaves arbitrary constraints intact. 
    The constraints are specified via a ``constraint_oracle`` function, which
    is taking a :ref:`QuantumVariable` or :ref:`QuantumArray` and apply a phase $\phi$
    (specified by the keyword argument ``phase``) to the states that are allowed
    by the constraints.
    
    Additionally the amount of winner states needs to be known. For this the user
    needs to provide the function ``winner_state_amount``, that returns the number
    of winner states for a given qubit amount. This number can be an approximation,
    however faulty values can cause leakage into the state-space that is forbidden
    by the constraints.
    
    For more details regarding implementation specifics please check the 
    corresponding :ref:`tutorial <ConstrainedMixers>`.

    Parameters
    ----------
    constraint_oracle : function
        A function of a :ref:`QuantumVariable` or :ref:`QuantumArray. Also needs to
        support the keyword argument ``phase``. This function should apply the phase
        specified by the keyword argument to the allowed states.
    winner_state_amount : function
        A function of a QuantumVariable or QuantumArray, that returns the amount 
        of winner states for that QuantumVariable.


    Returns
    -------
    constrained_mixer : function
        A mixer function that does not leave the allowed space specified by the oracle.
        
    Examples
    --------
    
    We create a mixer function that only mixes among the states where the first and the
    last qubit disagree. In more mathematical terms - they satisfy the following 
    constraint function.
    
        
    .. math::

        f: \mathbb{F}_2^n \rightarrow \mathbb{F}_2, x \rightarrow (x_{n-1} \neq x_0)
        
    ::
        
        from qrisp.qaoa import constrained_mixer_gen
        from qrisp import QuantumVariable, auto_uncompute, cx, p

        @auto_uncompute
        def constraint_oracle(qarg, phase):
        
            predicate = QuantumBool()        
            
            cx(qarg[0], predicate)
            cx(qarg[-1], predicate)
            p(phase, predicate)
          
        def winner_state_amount(qarg):
            return 2**(len(qarg) - 1)
          
        mixer = constrained_mixer_gen(constraint_oracle, winner_state_amount)
        
    To test the mixer, we create a :ref:`QuantumVariable`:
        
    ::
        
        import numpy as np
        beta = np.pi
        
        qv = QuantumVariable(3)
        qv[:] = "101"
        mixer(qv, beta)
        print(qv)
        #Yields: {'101': 1.0} 
        #Leaves forbidden states invariant
        
        qv = QuantumVariable(3)
        qv[:] = "100"
        mixer(qv, beta)
        print(qv)
        #Yields: {'100': 0.25, '110': 0.25, '001': 0.25, '011': 0.25}
        #Only mixes among allowed states


    """
    
    from qrisp.grover import grovers_alg
    
    def prep_psi(qarg):
        
        if isinstance(qarg, QuantumVariable):
            qubit_amount = len(qarg)
        elif isinstance(qarg, QuantumArray):
            qubit_amount = len(qarg.qtype)*len(qarg.flatten())
        else:
            raise Exception(f"Argument type {type(qarg)} not supported for constrained mixer")
        
        grovers_alg(qarg,
                    constraint_oracle,
                    exact = True,
                    winner_state_amount = winner_state_amount(qarg))
        
        
    def inv_prep_psi(qarg):

        with invert():
            prep_psi(qarg)
            
    def constrained_mixer(qarg, beta):

        with conjugate(inv_prep_psi)(qarg):
            mcp(beta, qarg, ctrl_state = 0)
    
    return constrained_mixer
    

