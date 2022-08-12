import argparse, os
import unittest
from unittest.mock import patch, call, ANY
from pathlib import Path

from bin.get_IS_info import *

class TestGetISInfo(unittest.TestCase):
    TEST_COBS_TABLE = 'tests/data/input/test_insertion_sequences.fasta_1_results_table.txt'
    TEST_FFQ_JSON_LOC = 'tests/data/input'
    TEST_TAB_FILE = 'tests/data/input/test_insertion_sequence_annotations.tab'
    TEST_AA_FASTA = 'tests/data/input/test_insertion_sequences.faa'
    TEST_INTERPROSCAN_OUT = 'tests/data/input/test_insertion_sequences.faa.tsv'
    TEST_FASTA = 'tests/data/input/test_candidate_insertion_sequences.fasta'
    TEST_OUTPUT_PREFIX = 'tests/data/output/test'

    def test_get_cobs_info(self):
        actual = get_cobs_info(self.TEST_COBS_TABLE, self.TEST_FFQ_JSON_LOC)

        self.maxDiff = None
        self.assertEqual(actual,
        {'IS_cluster_115105_length_655': [('SAMN07658209', 'Mycobacterium tuberculosis')],
        'IS_cluster_2614_length_1455': [('SAMN07658618', 'Mycobacterium tuberculosis')]})

    def test_get_prodigal_info(self):
        actual = get_prodigal_info(self.TEST_AA_FASTA)

        self.assertEqual(actual['IS_cluster_21476_length_1873'], {'IS_cluster_21476_length_1873_1': (157, 1773)})
        self.assertEqual(actual['IS_cluster_10977_length_2384'], {'IS_cluster_10977_length_2384_1': (36, 593), 'IS_cluster_10977_length_2384_2': (662, 2272)})

    def test_get_interproscan_info(self):
        actual = get_interproscan_info(self.TEST_INTERPROSCAN_OUT)

        self.assertEqual(actual['IS_cluster_17448_length_1504_1'], {'IPR002560': ['Transposase IS204/IS1001/IS1096/IS1165, DDE domain', (495, 693)]})
        self.assertEqual(actual['IS_cluster_134947_length_1460_1'], {'IPR012337': ['Ribonuclease H-like superfamily', (333, 828)], 'IPR036397': ['Ribonuclease H superfamily', (345, 828)], 'PTHR35004': ['TRANSPOSASE RV3428C-RELATED', (18, 1110)]})
        self.assertEqual(actual['IS_cluster_562609_length_2857_1'], {'IPR013762': ['Integrase-like, catalytic domain superfamily', (0, 231)]})

    def test_write_info(self):
        prodigal_info = get_prodigal_info(self.TEST_AA_FASTA)
        interpro_info = get_interproscan_info(self.TEST_INTERPROSCAN_OUT)
        cobs_info = get_cobs_info(self.TEST_COBS_TABLE, self.TEST_FFQ_JSON_LOC)

        output = write_info(self.TEST_TAB_FILE, prodigal_info, interpro_info, cobs_info, self.TEST_OUTPUT_PREFIX)

        tab_name = self.TEST_OUTPUT_PREFIX + '_insertion_sequences_info.txt'
        tab = open(tab_name, "r")
        actual = "".join(tab.readlines())
        os.remove(tab_name)
        self.maxDiff = None
        self.assertEqual(actual, """IS_name\tsample_id\tcontig\titr1_start_position\titr1_end_position\titr2_start_position\titr2_end_position\titr_cluster\tinterpro_or_panther_accession\tCOBS_index_biosample_id\tCOBS_index_origin\nIS_length_655_Transposase_IS200_like_148-565_Transposase_IS200_like_superfamily_124-580_REP_ASSOCIATED_TYROSINE_TRANSPOSASE_133-625\tSRS013170\tNODE_18_length_76504_cov_9.77495\t74408\t74436\t75032\t75062\t115105\tIPR002686;IPR036515;PTHR36966\tSAMN07658209\tMycobacterium tuberculosis\nIS_length_1455_Integrase_like_catalytic_domain_superfamily_1393-1918\tSRS013170\tNODE_31_length_64375_cov_7.58579\t10034\t10063\t11459\t11488\t2614\tIPR013762\tSAMN07658618\tMycobacterium tuberculosis\n""")

        self.assertEqual(output, {'IS_cluster_115105_length_655': 'IS_length_655_Transposase_IS200_like_148-565_Transposase_IS200_like_superfamily_124-580_REP_ASSOCIATED_TYROSINE_TRANSPOSASE_133-625', 'IS_cluster_2614_length_1455': 'IS_length_1455_Integrase_like_catalytic_domain_superfamily_1393-1918'})

    def test_write_fasta_file(self):

        write_fasta_file(self.TEST_FASTA, {'IS_cluster_115105_length_655': 'IS_length_655_Transposase_IS200_like_148-565_Transposase_IS200_like_superfamily_124-580_REP_ASSOCIATED_TYROSINE_TRANSPOSASE_133-625', 'IS_cluster_2614_length_1455': 'IS_length_1455_Integrase_like_catalytic_domain_superfamily_1393-1918'}, self.TEST_OUTPUT_PREFIX)


    def test_arguments(self):
        actual = get_arguments().parse_args(
            ['--tab_file', 'tab_file', '--cobs_search_out', 'cobs_search_out',
            '--ffq_json', 'ffq_json', '--aa_fasta', 'aa_fasta',
            '--interproscan_out', 'interproscan_out',
            '--fasta_file', 'fasta_file',
            '--output_prefix', 'output_prefix'])
        self.assertEqual(actual, argparse.Namespace(tab_file='tab_file',
        aa_fasta='aa_fasta', interproscan_out='interproscan_out',
        ffq_json='ffq_json', cobs_table='cobs_search_out', fasta_file='fasta_file',
        output_prefix='output_prefix'))

    @patch('bin.get_IS_info.get_prodigal_info')
    @patch('bin.get_IS_info.get_interproscan_info')
    @patch('bin.get_IS_info.get_cobs_info')
    @patch('bin.get_IS_info.write_info')
    @patch('bin.get_IS_info.write_fasta_file')
    def test_main(self, mock_write_fasta_file, mock_write_info, mock_get_cobs_info, mock_get_interproscan_info, mock_get_prodigal_info):
        args = get_arguments().parse_args(
            ['--tab_file', 'tab_file',
            '--cobs_search_out', 'cobs_search_out',
            '--ffq_json', 'ffq_json', '--aa_fasta', 'aa_fasta',
            '--interproscan_out', 'interproscan_out',
            '--fasta_file', 'fasta_file',
            '--output_prefix', 'output_prefix'])
        mock_get_prodigal_info.return_value = {'a dictionary'}
        mock_get_interproscan_info.return_value = {'another dictionary'}
        mock_get_cobs_info.return_value = {'final dictionary'}
        mock_write_info.return_value = {'last dictionary'}

        main(args)

        self.assertEqual(mock_get_prodigal_info.call_args_list, [call('aa_fasta')])
        self.assertEqual(mock_get_interproscan_info.call_args_list, [call('interproscan_out')])
        self.assertEqual(mock_get_cobs_info.call_args_list, [call('cobs_search_out', 'ffq_json')])
        self.assertEqual(mock_write_info.call_args_list, [call('tab_file', {'a dictionary'}, {'another dictionary'}, {'final dictionary'}, 'output_prefix')])
        self.assertEqual(mock_write_fasta_file.call_args_list, [call('fasta_file', {'last dictionary'}, 'output_prefix')])
