import unittest,tempfile
from pathlib import Path
from test_diplomacy import fixture
from privateer.save import RTW3Save
from privateer.diplomacy import apply_relations,Diplomacy,unique_section
class RelationActionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name);fixture(self.path);self.s=RTW3Save.load(self.path)
  unique_section(self.s,'General').set('EnemyVP',90);self.s.nation(0).section.set('VP',80)
 def test_alliance_mapping_and_break(self):
  apply_relations(self.s,{}, {(0,1):'Create Alliance',(5,6):'Create Alliance'})
  d=Diplomacy(self.s);self.assertEqual(d.values(0,1,True),(60,));self.assertEqual(d.values(5,6,True),(60,60));self.assertEqual(d.values(5,6),(4,4))
  apply_relations(self.s,{}, {(0,1):'Break Treaty',(5,6):'Break Treaty'})
  self.assertEqual(Diplomacy(self.s).values(5,6,True),(0,0))
 def test_ceasefire_start_roundtrip(self):
  apply_relations(self.s,{}, {(0,2):'Ceasefire'})
  self.assertEqual(unique_section(self.s,'General').fields()['War'],'-1');self.assertEqual(self.s.nation(0).section.fields()['VP'],'0');self.assertEqual(Diplomacy(self.s).values(0,2),(3,))
  apply_relations(self.s,{}, {(0,2):'Break Treaty'})
  apply_relations(self.s,{}, {(0,2):'Start War'})
  out=self.s.save_as(self.path/'copy');r=RTW3Save.load(out);self.assertEqual(Diplomacy(r).values(0,2),(50,));self.assertEqual(unique_section(r,'General').fields()['War'],'1')
 def test_batch_failure_is_atomic(self):
  before=self.s.documents[self.s.main_file].to_bytes()
  with self.assertRaises(ValueError):apply_relations(self.s,{}, {(0,1):'Create Alliance',(0,3):'Start War'})
  self.assertEqual(before,self.s.documents[self.s.main_file].to_bytes());self.assertFalse(self.s.modified)
 def test_reset_and_conflicts(self):
  apply_relations(self.s,{}, {(5,6):'Reset Tension to 0'});self.assertEqual(Diplomacy(self.s).values(5,6),(0,0))
  for a in ['Reset Tension to 0','Create Alliance']:
   with self.assertRaises(ValueError):apply_relations(self.s,{}, {(0,2):a})
  with self.assertRaises(ValueError):apply_relations(self.s,{(0,1):3},{(1,0):'Break Treaty'})
 def test_ai_war_and_missing_fields_rejected(self):
  for a in ['Start War','Ceasefire']:
   with self.assertRaises(ValueError):apply_relations(self.s,{}, {(5,6):a})
  self.s.nation(0).section.set('VP','unknown')
  with self.assertRaises(ValueError):apply_relations(self.s,{}, {(0,2):'Ceasefire'})
 def test_status_and_matrix_preserve_direction(self):
  d=Diplomacy(self.s)
  self.s.nation(2).section.set('Allied',0)
  unique_section(self.s,'General').set('War',6)
  self.assertEqual(d.status(0,2),'War')
  self.assertEqual(d.matrix_cell(0,2),'50 · War')
  self.assertEqual(d.matrix_cell(2,0),'50 · War')
  self.assertEqual(d.matrix_cell(2,2),'—')
  self.assertEqual(d.status(0,1),'Allied')
  self.s.nation(5).section.set('AITension6',8)
  self.assertEqual(d.status(5,6),'Mixed relations')
  self.assertEqual(d.matrix_cell(5,6),'8 · Allied')
  self.assertEqual(d.matrix_cell(6,5),'4 · Allied')
  self.s.nation(5).section.set('AIAlliance6','bad')
  self.assertEqual(d.matrix_cell(5,6),'Unknown')
 def test_status_follows_actions(self):
  apply_relations(self.s,{}, {(0,2):'Ceasefire',(0,1):'Break Treaty'})
  self.assertEqual(Diplomacy(self.s).status(0,1),'Peace')
  apply_relations(self.s,{}, {(0,1):'Start War'})
  self.assertEqual(Diplomacy(self.s).status(0,1),'War')
if __name__=='__main__':unittest.main()
