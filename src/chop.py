import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--circuit', type=str, default=None)
    parser.add_argument('--subcirc', type=str, default=None)
    parser.add_argument('--cores', type=int, default=1)
    args = parser.parse_args()
    CIRCUIT = args.circuit
    SUBCIRCUIT = args.subcirc
    CORES = args.cores
    header = []
    body = []

    # Read file and separate header and body
    with open(CIRCUIT, 'r') as f:
        for line in f:
            if line.startswith(('OPENQASM', 'include', 'qubit', 'bit', 'qreg', 'creg')):
                header.append(line)
            elif not line.startswith(('//', 'measure', 'barrier')) and line.strip():
                body.append(line)

    # Calculate lines per file
    total_lines = len(body)
    lines_per_file = total_lines // CORES  # Base split
    remainder_start = lines_per_file * (CORES - 1)  # Remainder starts from here

    # Create output files
    start = 0
    for i in range(CORES):
        output_file = f"{SUBCIRCUIT}{i + 1}.qasm"
        print(f"Writing {output_file}")
        with open(output_file, "w") as out:
            out.writelines(header)  # Write header

            if i < CORES - 1:
                end = start + lines_per_file  # Regular split
            else:
                end = total_lines  # Last file gets all remaining lines

            out.writelines(body[start:end])  # Write body part
            start = end  # Move to the next batch

