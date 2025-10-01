#!/bin/bash

CIRCUIT_NAME="ae_indep_qiskit_6"
DEPTH="d"
WIDTH="w"
DENSITY="dens"
DEBUG="False"
CORES=2
QISKIT_DIR="../qasm"
TIME_DIR="time/"$CORES"cores"

TIMESTAMP_SUBFILE=$TIME_DIR"/"$CIRCUIT_NAME"_timestamps"
TIMESTAMP_FILE=$TIMESTAMP_SUBFILE".csv"
QASM_DIR=$QISKIT_DIR"/"$CORES"cores"
CIRC_FILENAME=$QISKIT_DIR"/"$CIRCUIT_NAME".qasm"
SUBCIRC_BASE=$QASM_DIR"/"$CIRCUIT_NAME"_subcirc_"
TRANSPILED_CIRC=$QASM_DIR"/"$CIRCUIT_NAME"_transpiled.qasm"

mkdir -p $QISKIT_DIR $QASM_DIR $TIME_DIR

### PARALLEL TRANSPILATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo "*** I am starting the parallel transpilation! $TIMESTAMP_FILE ***"
echo 'Column, Value' > $TIMESTAMP_FILE
echo 'Name, '$CIRCUIT_NAME >> $TIMESTAMP_FILE
echo 'Depth, '$DEPTH >> $TIMESTAMP_FILE
echo 'Density, '$DENSITY >> $TIMESTAMP_FILE
echo 'Width, '$WIDTH >> $TIMESTAMP_FILE

echo 'Chopping Start Time, '$(date +%s%N) >> $TIMESTAMP_FILE
python3 chop.py --circuit $CIRC_FILENAME --cores $CORES --subcirc $SUBCIRC_BASE
exit_status=$?
if [ "${exit_status}" -ne 0 ]; then
      echo "Issue in chop phase"
      exit 1
fi
echo 'Chopping End Time, '$(date +%s%N) >> $TIMESTAMP_FILE

for i in $(seq 1 $CORES)
do
  SUBCIRC_NAME=$CIRCUIT_NAME"_subcirc_"$i
  (
  python3 parallel_create_transpile_permute.py --qasm_file $SUBCIRC_NAME --qasm_dir $QASM_DIR --num_cores $CORES --debug $DEBUG > $TIMESTAMP_SUBFILE"_"$i".csv"
  exit_status=$?
  if [ "${exit_status}" -ne 0 ]; then
      echo "Issue in parallel_create_transpile_permute phase"
      exit 1
  fi
  ) &
done
wait

echo 'Concatenate Start Time, '$(date +%s%N) >> $TIMESTAMP_FILE
python3 merge.py --t_circ $TRANSPILED_CIRC --sc_base $SUBCIRC_BASE --cores $CORES
exit_status=$?
if [ "${exit_status}" -ne 0 ]; then
      echo "Issue in merge phase"
      exit 1
fi
echo 'Concatenate End Time, '$(date +%s%N) >> $TIMESTAMP_FILE
echo "*** I have finished the parallel transpilation! ***"

### CLEANUP
for i in $(seq 1 $CORES)
do
  cat "${TIMESTAMP_SUBFILE}_${i}.csv" >> $TIMESTAMP_FILE
  rm "${TIMESTAMP_SUBFILE}_${i}.csv"
  echo "*** Removed "${TIMESTAMP_SUBFILE}_${i}.csv
  rm $QASM_DIR"/"$CIRCUIT_NAME"_subcirc_"$i".qasm"
  rm $QASM_DIR"/"$CIRCUIT_NAME"_subcirc_"$i"_transpiled.qasm"
  echo "*** Removed "$QASM_DIR"/"$CIRCUIT_NAME"_subcirc_"$i"_transpiled.qasm"
done

### QISKIT
echo 'Qiskit Start Time, '$(date +%s%N) >> $TIMESTAMP_FILE
python3 qiskit_run.py --circ_name $CIRCUIT_NAME --qasm_dir $QISKIT_DIR --num_cores $CORES --debug $DEBUG >> $TIMESTAMP_FILE
exit_status=$?
if [ "${exit_status}" -ne 0 ]; then
    echo "Issue in qiskit_run phase"
    exit 1
fi
echo 'Qiskit End Time, '$(date +%s%N) >> $TIMESTAMP_FILE
echo "*** I have finished the qiskit transpilation! ***"

### OVERHEAD STATS
echo "--base_name ${QASM_DIR}"/"${CIRCUIT_NAME}"
python3 record_overheads.py --base_name $QASM_DIR"/"$CIRCUIT_NAME >> $TIMESTAMP_FILE
exit_status=$?
if [ "${exit_status}" -ne 0 ]; then
    echo "Issue in record_overheads phase"
    exit 1
fi

exit 0