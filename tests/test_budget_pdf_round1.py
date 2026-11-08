import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from privateer.document import TextDocument
from privateer.economy import BudgetContext, budget_context, project_budget, _possession_income
from privateer.save import RTW3Save


def campaign(fleet=8, targets=''):
    text = (f'[General]\nYear=1971\nFleetSize={fleet}\nWar=-50\n'
            '[Nation0]\nName=USA\nBaseResources=139707\nBudgetModifier=18\n'
            'GovernmentType=0\nResearchPct=10\nFunds=101244\nNavalAcademy=1\n'
            '[Nation0Submarines]\nSubCount=0\n'
            '[Nation0CoastalArtillery]\nCACount=0\n' + targets)
    return RTW3Save(Path('.'), {'example.bcs': TextDocument.parse(text)}, 'example.bcs')


class BudgetFormulaTests(unittest.TestCase):
    def test_usa_income_research_and_academy(self):
        save = campaign()
        c = BudgetContext(fleet_size=8, intelligence=0, possession_income=1236,
                          income_multipliers=(Decimal('.97'),), year=1971)
        p = project_budget(save.nation(0), context=c)
        self.assertEqual((p.yearly_budget, p.monthly_budget, p.research),
                         (1949230, 162436, 16244))
        self.assertEqual(p.extra_training, 1710)
        changed = project_budget(save.nation(0), context=c, base_resources=139807)
        self.assertNotEqual(changed.yearly_budget, p.yearly_budget)

    def test_intelligence_scales_with_fleet_size(self):
        save = campaign(2, '[Nation1]\nName=Target\nIntelligenceSpending=3\n')
        self.assertEqual(budget_context(save, save.nation(0)).intelligence, 60)

    def test_minimum_budget_modifier_and_rounding(self):
        save = campaign()
        save.nation(0).section.set('BudgetModifier', 1)
        c = BudgetContext(fleet_size=8, intelligence=0, possession_income=300)
        p = project_budget(save.nation(0), context=c, base_resources=36000)
        self.assertEqual(p.yearly_budget, 86240)

    def test_possession_matching_uses_area_and_name_when_slots_differ(self):
        owned = [SimpleNamespace(area=1, index=0, name='Home', owner='USA', value='200'),
                 SimpleNamespace(area=2, index=0, name='Colony', owner='USA', value='4')]
        map_data = (b'[MapArea2]\nMapArea2Possession0Name=Other\n'
                    b'MapArea2Possession0NaturalOwnerName=USA\n'
                    b'MapArea2Possession1Name=Colony\n'
                    b'MapArea2Possession1NaturalOwnerName=Other\n')
        with patch('privateer.colonies.possessions', return_value=owned), \
             patch.object(Path, 'read_bytes', return_value=map_data):
            self.assertEqual(_possession_income(None, SimpleNamespace(name='USA'), 1971, 'game'), 16)

    def test_dock_expansion_uses_fleet_size_and_industry(self):
        save = campaign(2)
        nation = save.nation(0)
        for key, value in {'DockBuilding': 15, 'DockSize': 12000,
                           'UndevelopedShipbuildingIndustry': 1}.items():
            nation.section.set(key, value)
        self.assertEqual(budget_context(save, nation).additional_construction, 324)


if __name__ == '__main__':
    unittest.main()

