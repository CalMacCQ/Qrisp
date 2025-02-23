from qrisp import QuantumCircuit
from qrisp.core import QuantumVariable, cx , x, rz
from qrisp import ControlledOperation
from qrisp.interface import BackendClient
import numpy as np
import types
    
import pennylane as qml 

"""
TODO: 
-- clbit interaction with measurements 
-- conditional environment, i.e. mid-circuit measurement is possible, have to create this
    --> otherwise no clbit interaction?

BUGS:

"""


def create_qml_instruction(op):

    #create basic, straight forward instructions
    if op.name == "rxx":
        qml_ins = qml.IsingXX
    elif op.name == "ryy":
        qml_ins = qml.IsingYY
    elif op.name == "rzz":
        qml_ins = qml.IsingZZ

    elif op.name == "p":
        qml_ins =  qml.RZ
    elif op.name == "rx":
        qml_ins = qml.RX
    elif op.name == "ry":
        qml_ins = qml.RY
    elif op.name == "rz":
        qml_ins = qml.RZ
    elif op.name == "u1":
        qml_ins = qml.U1  

    elif op.name == "u3":
        qml_ins = qml.U3
    elif op.name == "xxyy":
        qml_ins = qml.IsingXY
    elif op.name == "swap":
        qml_ins = qml.SWAP
    elif op.name == "h":
        qml_ins = qml.Hadamard
    elif op.name == "x":
        qml_ins = qml.PauliX
    elif op.name == "y":
        qml_ins = qml.PauliY
    elif op.name == "z":
        qml_ins = qml.PauliZ
    elif op.name == "s" or  op.name =="s_dg":
        qml_ins = qml.S
    elif op.name == "t" or op.name =="t_dg":
        qml_ins = qml.T
    elif op.name == "sx" or op.name == "sx_dg":
        qml_ins = qml.SX

    #complex gate, with subcircuit definition we create a representative subcircuit
    elif op.definition:
        circ = qml_converter(op.definition , circ = True)
        return circ
    else:
        Exception("Cannot convert")
    return qml_ins



def qml_converter(qc,circ= False):

    def circuit():

        circFlag = False

        qbit_dic = {}
        # add qubits
        for qubit in qc.qubits:
            qbit_dic[qubit.identifier] = qubit.identifier
        #save measurements
        measurelist = []

        for index in range(len(qc.data)):
            
            op = qc.data[index].op
            params = list(op.params)


            qubit_list = [qbit_dic[qubit.identifier] for qubit in qc.data[index].qubits]
            op_qubits = qc.data[index].qubits
            

            if op.name in ["qb_alloc", "qb_dealloc"]:
                continue

            if op.name == "measure":
                ### below: possible implementation for nested circuit measurments
                #if circ == True:
                #   Exception("Measurements in nested circuits not supported (yet)")
                measurelist.append(*qubit_list)
                continue

            ###### BugCatcher + special gates ######
            if op.name in ["sx", "sx_dg" , "id","t","t_dg","s","s_dg"]:
                #bugged -> params empty
                params = []
            if op.name == "xxyy":
                # deffed as RXXYY with angle pi 
                params = [np.pi]

            if op.name == "cx":
                    # maybe adjustment necessary here
                    if hasattr(op, "ctrl_state"):
                        qml_ins = qml.CNOT([qubit_list[0], qubit_list[1]])
                    else:
                        qml_ins = qml.CNOT([qubit_list[0], qubit_list[1]])
            
            elif op.name == "cy":
                if hasattr(op, "ctrl_state"):
                    qml_ins = qml.CY([qubit_list[0], qubit_list[1]])
                else:
                    qml_ins = qml.CY([qubit_list[0], qubit_list[1]])

            elif op.name == "cz":
                if hasattr(op, "ctrl_state"):
                    qml_ins = qml.CZ([qubit_list[0], qubit_list[1]])
                else:
                    qml_ins = qml.CZ([qubit_list[0], qubit_list[1]])
            
            elif op.name == "cp":
                if hasattr(op, "ctrl_state"):
                    qml_ins = qml.ControlledPhaseShift(*params, [qubit_list[0], qubit_list[1]])
                else:
                    qml_ins = qml.ControlledPhaseShift(*params, [qubit_list[0], qubit_list[1]])

            # return the controlled instruction or the nested circuit
            elif isinstance(op, ControlledOperation):
                qml_trafo = create_qml_instruction(op)
                if isinstance( qml_trafo  , types.FunctionType):
                    circFlag = True
                    wire_map = dict()
                    for i in range(len(op_qubits)):
                        #wire_map[i] = op_qubits[i].identifier
                        wire_map[op.definition.qubits[i].identifier]  = op_qubits[i].identifier 
                    mapped_quantum_function = qml.map_wires(qml_trafo, wire_map)
                    qml_ins = qml.ctrl(mapped_quantum_function, control= op.ctrl_state[::-1])
                else:
                    qml_ins = qml.ctrl(qml_trafo, control= op.ctrl_state[::-1])

            # return the instruction or the nested circuit
            else: 
                qml_trafo = create_qml_instruction(op)
                if isinstance(qml_trafo, types.FunctionType):
                    circFlag = True
                    wire_map = dict()
                    for i in range(len(op_qubits)):
                        #map the wires as given for the nested circuit
                        wire_map[op.definition.qubits[i].identifier]  = op_qubits[i].identifier 
                    mapped_quantum_function = qml.map_wires(qml_trafo, wire_map)

                else:
                    if "_dg" in op.name:
                        qml_ins = qml.adjoint(qml_trafo( *params, wires = qubit_list))
                    else:
                        qml_ins = qml_trafo( *params, wires = qubit_list)
            

            if not isinstance(circ, bool):
                circ()
            elif not circFlag:
                qml_ins
            else: 
                mapped_quantum_function()
        
        #add measurements at the end, i.e. return a count object
        if len(measurelist):
            return qml.counts(wires=measurelist)


    return circuit