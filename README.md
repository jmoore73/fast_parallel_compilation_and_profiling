## Fast Parallel SWAP Insertion in Qiskit
Set up a Conda environemt  with Python 3.10.

Install required modules:
```
qiskit==1.1.0
qiskit[qasm3-import]
pytket
```

Run via:
```
bash local_pytket_run.sh
```
The circuit and corresponding variables can be edited in the shell script.


## Random Benchmark Suite

Run from:
```
random_generator/main.py
```

A broad random benchmark suite. Circuits will range in terms of depth, width and density. The gate sets the original random circuit can consist of may also be defined in ```GATE_SET```.

### Definition Variables
The parameters of the random benchmark circuit to be generated are defined by the following global parameters ```GATE_SET, MIN_WIDTH, MAX_WIDTH, WIDTH_STEP, MIN_DEPTH, MAX_DEPTH, DEPTH_STEP, MIN_DENSITY, DENSITY_STEP, COMBINE``` and ```DRAW```.

Var | Type   | Default Value              | Argument
--- |--------|----------------------------| ---
```GATE_SET``` | string | ["H", "S", "X", "T", "CX"] | ```gate_set```
```COMBINE``` | bool   | False                      | ```combine```
```DRAW``` | bool   | False                      | ```draw```
```MIN_WIDTH``` | int    | 10                         | ```min_width```
```MAX_WIDTH``` | int    | 16                         | ```max_width```
```WIDTH_STEP``` | int    | 2                          | ```width_step```
```MIN_DEPTH``` | int    | 100                        | ```min_depth```
```MAX_DEPTH``` | int    | 500                        | ```max_depth```
```DEPTH_STEP``` | int    | 100                        | ```depth_step```
```MIN_DENSITY``` | float    | 0.5                        | ```min_density```
```MAX_DENSITY``` | float    | 1.0                        | ```max_density```
```DENSITY_STEP``` | float  | 0.1                        | ```density_step```

```COMBINE``` determines if the produced qasm files are saved in a collated folder as well as in the organised file layout. ```DRAW``` determines if the circuit diagrams are saved, note that this fails if there are to many requests or the circuit is too large. The rest of the variables names are self-explanatory.

These variables may be set in the ```helper.py``` file or can be passed as command line arguments e.g.

```
python3 main.py --min_depth 5000 --max_depth 50000 --depth_step 5000 --min_width 4 --max_width 50 --min_density 0.1 --combine True --draw False
```

There are 2 additional variables that cannot be set via the command line. ```MEASURE``` (bool) determine if the final measurements are to be inserted and ```SEED``` (int) is the seed for the ```random_circuit``` method.

