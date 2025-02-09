Backend Interface
=================

.. toctree::
   :maxdepth: 2
   :hidden:

   BackendServer
   BackendClient

   VirtualBackend
   VirtualQiskitBackend
   
The backend interface contains a minimal set of features that apply to every gate-based quantum computer.
The main motivation in designing the interface, is to provide a convenient setup for both clients and providers of physical quantum
backends. To ensure compatibility to existing network architectures, the interface is realized as REST-based interface.
Also available is a Thrift implementation of the same interface.

:ref:`BackendServer`
--------------------

This class is a wrapper for convenient setup of a server, capable of processing quantum circuits. Backend providers
simply have to create a Python function called ``run_func`` which receives a :ref:`QuantumCircuit`, an integer called ``shots`` and
optionally a string called ``token``. The return value should be the measurement results as a dictionary of bitstrings.

.. code-block:: python

   from qrisp.interface import BackendServer
   from backend_provider import run_func, ping_func
   
   server = BackendServer( run_func,
                           ping_func,
                           port = 8080)
                           
   server.start()


:ref:`BackendClient`
--------------------

This class can be used to connect to :ref:`BackendServers <BackendServer>` in order to send out requests for processing quantum circuits.

.. code-block:: python

   from qrisp.interface import BackendClient
   backend = BackendClient(server_ip, port)
   
   from some_library import some_quantum_algorithm
   
   qv = some_quantum_algorithm()
   
   res = qv.get_measurement(backend = backend)

In this code snippet, we create connect a BackendClient, to the BackendServer running under the ip ``server_ip`` and ``port``. Subsequently, we run some quantum algorithm returing a :ref:`QuantumVariable` and call the :meth:`qrisp.QuantumVariable.get_measurement` method, to query the remote backend.


:ref:`VirtualBackend`
---------------------

The VirtualBackend class allows to run external circuit dispatching code locally and
having adherence to the Qrisp interface at the same time. Using this class it is possible
to use the (Python) infrastructure of any backend provider as a Qrisp backend.

:ref:`VirtualQiskitBackend`
---------------------------

This class is a wrapper for the VirtualBackend to quickly integrate Qiskit backend instances.

::

   from qiskit import Aer
   from qrisp.interface import VirtualQiskitBackend
   qiskit_backend = Aer.get_backend('qasm_simulator')
   vrtl_qasm_sim = VirtualQiskitBackend(qiskit_backend)

Naturally, this also works for non-simulator Qiskit backends.
