#!/usr/bin/env python

'''
unit tests for intersect.py
'''

from SmileTrain.test import fake_fh
import unittest, tempfile, subprocess, os, shutil, StringIO
from Bio import SeqIO, Seq

from SmileTrain import util, intersect


class TestFastqIDToReadID(unittest.TestCase):
    def test_correct(self):
        self.assertEqual(intersect.fastq_id_to_read_id("@MISEQ578:1:1101:17145:1691#TTCAGA/1"), "@MISEQ578:1:1101:17145:1691#TTCAGA")
        
    def test_error(self):
        self.assertRaises(RuntimeError, intersect.fastq_id_to_read_id, "@MISEQ:crap")


class TestWithFastqs(unittest.TestCase):
    def setUp(self):
        self.fq_for = fake_fh('''@MISEQ578:1:1101:17145:1691#TTCAGA/1\nNTCACCTTCTTGAAGGCTTCCCATTCATTCAGGAACCGCCTTCTGGTGATTTGCAAGAACGCGTACTTATTCGCCACCATGATTATGACCAGTGTTTCCAGTCCGTTCAGTTGTTGCAGTGGAATAGTCAGGTTAAATTTAATGTGACCGTTTATCGCAATCTGCCGACCACTCGCGATTCAATCATGACTTCGTGATCAAAGATTGAGTGTGAGGTTATAACGCCGAAGCGGTAACAACTGTAAGAACTG\n+MISEQ578:1:1101:17145:1691#TTCAGA/1\nB]]P]Pab_cePRPPP`efdde`efeRfgeeRPeeeeb`fffgfadfaeefeeedeabfeddbddfggggfcgfbddeggeggfggeggaeeegggggfgdgggfggeaeaddcfgedePdaddPdffeefeaPPeeefPffgeedaecb[^bfggdbedbggPac^Nb^_gfaMLLb`facgeegeafe[bBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\n@MISEQ578:1:1101:18716:1699#CCTGAG/1\nNCAGCGTCATAAGAGGTTTTACCTCCAAATGAAGAAATAACATCATGGTAACGCTGCATGAAGTAATCACGTTCTTGGTCAGTATGCAAATTAGCATAAGCAGCTTGCAGACCCATAATGTCAATAGATGTGGTAGAAGTCGTCATTTGGCGAGAAAGCTCAGTCTCAGGAGGAAGCGGAGCAGTCCAAATGTTTTTGAGATGGCAGCAACGGAAACCATAACGAGCATCATCTTAGATCGGAAGAGAGGT\n+MISEQ578:1:1101:18716:1699#CCTGAG/1\nBPPP]P]]PbRRcPabffffefefedaPffbPeeegggeggggegfegecfefffffgggacedggggggfgggfffgggggggggfgggggfgfgdgeggggggegdeecffdgafefggegfgQefgeafegeaPeggdfffg`edcga_b^aePfgggfggefeaeOPNNNe[N]LL_LefgeacccaOO\ON[LM[fbbNbb`bMYMZLZMLXMXOZZNXM`__eeaaOOZOXZbBBBBBBBBBBBB\n@MISEQ578:1:1101:16445:1701#CCTGAG/1\nNCGCTCAAAGTCAAAATAATCAGCGTGACATTCAGAAGGGTAATAAGAACGAACCATAAAAAAGCCTCCAAGATTTGGAGGCATGAAAACATACAATTGGGAGGGTGTCAATCCTGACGGTTATTTCCTAGACAAATTAGAGCCAATACCATCAGCTTTACCGTCTTTCCAGAAATTGTTCCAAGTATCGGCAACAGCTTTATCAATACCATGACAAATATCAACCACACCAGAAGCAGCATCAGTGACGA\n+MISEQ578:1:1101:16445:1701#CCTGAG/1\nBPPP]]PPPPa_RRaPecPefaPeOdO`eRdfeaeaab`dfeeecePP`dd`eddefPfaea^NeggggeafdeefPPPeddefefadebfegefggeded``_d`efggggggggeaddd`dggggfeeeePaOecefPPeeeabegPeggeafeefeefdffbfeggedaP[PePP]ecOO\cO\ccM[LLLYMbMYYOOZbfbegefeeOXXZZNOXaBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\n@MISEQ578:1:1101:12954:1727#AATGTC/1\nNGTGGTGCCAGCAGCCGCGGTAATACGGAGGATCCAAGCGTTATCCGGAATTATTGGGTTTAAAGGGTCCGCAGGCTGTTTGTTAAGTCAGGGGTGAAATCCTACCGCTCAACGGTAGAACTGCCTTTGATACTGGCAAACTTGAGTTATTGTGAAGTAGTTAGAATGTGTAGTGTAGCGGTGAAATGCATAGATATTACACAGAATACCGATTGCGAAAGCAGATTACTAACAATATACTGACGATGAGG\n+MISEQ578:1:1101:12954:1727#AATGTC/1\nBP]PP]P_]aPPP``e^dd^ddfgefebdbbffeggfgffffegggffNdefgggggfdeebceeefgggffffffgggggggegeggggeaedddggggggfggdfffffgedf^fbeggggggggfgffgggeeefggggggggfecfceafaegcef\[\OcgeaObbeegggegfLbbLdefffaeaeefedeaeOOaO`bNZeead^ZXdfeLZL`aaaNXNaXNZNNNNXNXaaaXeBBBBBBBB\n''')
        self.fq_rev = fake_fh('''@MISEQ578:1:1101:17145:1691#TTCAGA/2\nNTCACCTTCTTGAAGGCTTCCCATTCATTCAGGAACCGCCTTCTGGTGATTTGCAAGAACGCGTACTTATTCGCCACCATGATTATGACCAGTGTTTCCAGTCCGTTCAGTTGTTGCAGTGGAATAGTCAGGTTAAATTTAATGTGACCGTTTATCGCAATCTGCCGACCACTCGCGATTCAATCATGACTTCGTGATCAAAGATTGAGTGTGAGGTTATAACGCCGAAGCGGTAACAACTGTAAGAACTG\n+MISEQ578:1:1101:17145:1691#TTCAGA/2\nB]]P]Pab_cePRPPP`efdde`efeRfgeeRPeeeeb`fffgfadfaeefeeedeabfeddbddfggggfcgfbddeggeggfggeggaeeegggggfgdgggfggeaeaddcfgedePdaddPdffeefeaPPeeefPffgeedaecb[^bfggdbedbggPac^Nb^_gfaMLLb`facgeegeafe[bBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\n@MISEQ578:1:1101:16445:1701#CCTGAG/2\nNCGCTCAAAGTCAAAATAATCAGCGTGACATTCAGAAGGGTAATAAGAACGAACCATAAAAAAGCCTCCAAGATTTGGAGGCATGAAAACATACAATTGGGAGGGTGTCAATCCTGACGGTTATTTCCTAGACAAATTAGAGCCAATACCATCAGCTTTACCGTCTTTCCAGAAATTGTTCCAAGTATCGGCAACAGCTTTATCAATACCATGACAAATATCAACCACACCAGAAGCAGCATCAGTGACGA\n+MISEQ578:1:1101:16445:1701#CCTGAG/2\nBPPP]]PPPPa_RRaPecPefaPeOdO`eRdfeaeaab`dfeeecePP`dd`eddefPfaea^NeggggeafdeefPPPeddefefadebfegefggeded``_d`efggggggggeaddd`dggggfeeeePaOecefPPeeeabegPeggeafeefeefdffbfeggedaP[PePP]ecOO\cO\ccM[LLLYMbMYYOOZbfbegefeeOXXZZNOXaBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB\n@MISEQ578:1:1101:12954:1727#AATGTC/2\nNGTGGTGCCAGCAGCCGCGGTAATACGGAGGATCCAAGCGTTATCCGGAATTATTGGGTTTAAAGGGTCCGCAGGCTGTTTGTTAAGTCAGGGGTGAAATCCTACCGCTCAACGGTAGAACTGCCTTTGATACTGGCAAACTTGAGTTATTGTGAAGTAGTTAGAATGTGTAGTGTAGCGGTGAAATGCATAGATATTACACAGAATACCGATTGCGAAAGCAGATTACTAACAATATACTGACGATGAGG\n+MISEQ578:1:1101:12954:1727#AATGTC/2\nBP]PP]P_]aPPP``e^dd^ddfgefebdbbffeggfgffffegggffNdefgggggfdeebceeefgggffffffgggggggegeggggeaedddggggggfggdfffffgedf^fbeggggggggfgffgggeeefggggggggfecfceafaegcef\[\OcgeaObbeegggegfLbbLdefffaeaeefedeaeOOaO`bNZeead^ZXdfeLZL`aaaNXNaXNZNNNNXNXaaaXeBBBBBBBB\n''')


class TestFastqIDs(TestWithFastqs):
    def test_correct(self):
        self.assertEqual(intersect.fastq_ids(self.fq_for), ['MISEQ578:1:1101:17145:1691#TTCAGA', 'MISEQ578:1:1101:18716:1699#CCTGAG', 'MISEQ578:1:1101:16445:1701#CCTGAG', 'MISEQ578:1:1101:12954:1727#AATGTC'])


class TestCommonIDs(TestWithFastqs):
    def test_correct(self):
        self.assertEqual(intersect.common_ids(self.fq_for, self.fq_rev), set(['MISEQ578:1:1101:17145:1691#TTCAGA', 'MISEQ578:1:1101:16445:1701#CCTGAG', 'MISEQ578:1:1101:12954:1727#AATGTC']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
