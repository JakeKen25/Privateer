import tempfile
import unittest
from pathlib import Path
from privateer.save import RTW3Save
from privateer.diplomacy import Diplomacy


def fixture(folder, player='Italy'):
    text = '[General]\r\nWar=1\r\n'
    for i in range(10):
        text += f'[Nation{i}]\r\nName={player if i == 0 else "Country " + str(i)}\r\nNationNumber={9-i}\r\nTension = {50 if i==2 else 3}  \r\nAllied=2\r\n'
        for j in range(1,9):
            text += f'AITension{j}={0 if i in (0,9) or i==j else 4}\r\nAIAlliance{j}=16\r\n'
    (folder/'game.bcs').write_bytes(text.encode())
    (folder/'other.sta').write_bytes(b'opaque')
    return text.encode()


class TensionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)/'source'; self.folder.mkdir()
        self.before=fixture(self.folder)
        self.save=RTW3Save.load(self.folder)

    def test_dynamic_player_and_ai_targets(self):
        for player in ('Italy','Great Britain','Austria-Hungary'):
            fixture(self.folder,player); save=RTW3Save.load(self.folder)
            save.set_tensions({(0,7):2,(6,7):8})
            self.assertEqual(Diplomacy(save).values(0,7),(2,))
            self.assertEqual(Diplomacy(save).values(6,7),(8,8))
            self.assertEqual(save.nation(0).section.fields()['Tension'],'3')
            self.assertEqual(save.nation(9).section.fields()['Tension'],'3')
            self.assertEqual(save.nation(7).section.fields()['AIAlliance6'],'16')

    def test_minimal_roundtrip_backup_and_external_change(self):
        self.save.set_tensions({(0,1):2})
        expected=self.before.replace(b'Tension = 3  ',b'Tension = 2  ',2)
        # First occurrence is Nation0 and must stay unchanged.
        expected=expected.replace(b'Tension = 2  ',b'Tension = 3  ',1)
        backup=self.save.save()
        self.assertEqual((backup/'game.bcs').read_bytes(),self.before)
        self.assertEqual((self.folder/'game.bcs').read_bytes(),expected)
        self.assertEqual(Diplomacy(RTW3Save.load(self.folder)).values(0,1),(2,))
        self.save.set_tensions({(0,1):1})
        (self.folder/'other.sta').write_bytes(b'changed by game')
        with self.assertRaisesRegex(ValueError,'changed on disk'):
            self.save.save()
        with self.assertRaisesRegex(ValueError,'changed on disk'):
            self.save.save_as(Path(self.tmp.name)/'copy')

    def test_noop_and_war_preserved(self):
        self.save.set_tensions({(0,1):3})
        self.assertFalse(self.save.modified)
        self.assertEqual(self.save.documents['game.bcs'].to_bytes(),self.before)
        self.save.set_tensions({(1,7):5})
        self.assertEqual(Diplomacy(self.save).values(0,2),(50,))
        self.assertIn('wartime pattern',Diplomacy(self.save).description(0,2))

    def test_reject_invalid_self_extra_war_and_partial_batch(self):
        for changes in ({(0,1):2,(0,2):3},{(0,1):50},{(1,1):3},{(0,9):3},
                        {(0,1):True},{(1,7):2,(7,1):3}):
            with self.assertRaises(ValueError): self.save.set_tensions(changes)
            self.assertEqual(self.save.documents['game.bcs'].to_bytes(),self.before)

    def test_duplicates_missing_and_unsupported_layout(self):
        variants=[self.before.replace(b'Tension = 3  ',b'Tension=3\r\nTension=3',2),
                  self.before+b'[Nation1]\r\nName=Duplicate\r\n',
                  self.before.replace(b'AITension8=4\r\n',b'',1),
                  self.before.replace(b'Name=Country 1',b'IsPlayer=1\r\nName=Country 1')]
        for raw in variants:
            (self.folder/'game.bcs').write_bytes(raw)
            save=RTW3Save.load(self.folder)
            with self.assertRaises(ValueError): save.set_tensions({(0,1):2})
            self.assertEqual(save.documents['game.bcs'].to_bytes(),raw)

    def test_asymmetric_pair_only_normalized_on_explicit_edit(self):
        self.save.nation(7).section.set('AITension6',9)
        self.assertEqual(Diplomacy(self.save).values(6,7),(4,9))
        self.save.set_tensions({(0,1):2})
        self.assertEqual(Diplomacy(self.save).values(6,7),(4,9))
        self.save.set_tensions({(6,7):5})
        self.assertEqual(Diplomacy(self.save).values(6,7),(5,5))

if __name__=='__main__': unittest.main()
