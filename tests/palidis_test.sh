#/bin/bash

in_dir=data/input
out_dir=data/output

SUDO_OPT=
while getopts ":s" opt; do
  case ${opt} in
    s ) SUDO_OPT="sudo "
      ;;
    \? ) echo "Usage: $0 [-s to run with sudo]"
         exit 1
      ;;
  esac
done

function file_diff {
    local test=${1}
    local reference=${2}

    diff ${test} ${reference} > /dev/null 2>&1
    status=$?

    # If files different then warning
    if [[ ${status} -gt 0 ]]; then
        if [[ ${status} -eq 1 ]]; then
            echo ""
            echo "Test failed. The contents of ${test}.cached is not expected."
        elif [[ ${status} -eq 2 ]]; then
            echo ""
            echo "Test failed. Unable to perform differences check."
            if [[ ! -f $test ]]; then
                echo "Test failed. Expected output ${test}.cached is missing."
            fi
        fi
        return 1
    else
        echo ""
        echo "Test passed! Contents of ${test}.cached as expected."
        return 0
    fi
}

# Run workflows on test input data
echo "Starting nextflow pipeline tests..."
echo ""
${SUDO_OPT}nextflow -log palmem_test.log run palmem_test.nf --sample_id "test" --fasta1 "$in_dir/reference_1.fasta" --fasta2 "$in_dir/reference_2.fasta" --output_dir "$out_dir" --min_itr_length 25 --kmer_length 15 -profile standard

# Check for outputs
error_status=0
file_diff "${out_dir}/test_IR_1.fasta" "${out_dir}/reference_IR_1.fasta"
out=$?
error_status=$(($error_status | $out))
mv "${out_dir}/test_IR_1.fasta" "${out_dir}/test_IR_1.fasta.cached"

file_diff "${out_dir}/test_IR_2.fasta" "${out_dir}/reference_IR_2.fasta"
out=$?
error_status=$(($error_status | $out))
mv "${out_dir}/test_IR_2.fasta" "${out_dir}/test_IR_2.fasta.cached"

file_diff "${out_dir}/test_paired_to_IR_2.fasta" "${out_dir}/reference_paired_to_IR_2.fasta"
out=$?
error_status=$(($error_status | $out))
mv "${out_dir}/test_paired_to_IR_2.fasta" "${out_dir}/test_paired_to_IR_2.fasta.cached"

file_diff "${out_dir}/test_paired_to_IR_1.fasta" "${out_dir}/reference_paired_to_IR_1.fasta"
out=$?
error_status=$(($error_status | $out))
mv "${out_dir}/test_paired_to_IR_1.fasta" "${out_dir}/test_paired_to_IR_1.fasta.cached"

file_diff "${out_dir}/test_IR.tab" "${out_dir}/reference_IR.tab"
out=$?
error_status=$(($error_status | $out))
mv "${out_dir}/test_IR.tab" "${out_dir}/test_IR.tab.cached"


# Remove work directory
# rm -r work