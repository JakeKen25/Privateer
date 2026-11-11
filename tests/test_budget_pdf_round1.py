import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from privateer.document import TextDocument
from privateer.economy import BudgetContext, budget_context, project_budget, _possession_income, _submarine_cost, _aircraft_cost
from privateer.maintenance import MaintenanceModel, ship_maintenance, fleet_maintenance
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

    def test_maintenance_era_multiplier_depends_on_government_and_war(self):
        save = campaign()
        self.assertEqual(budget_context(save, save.nation(0)).maintenance_multiplier, Decimal('1.25'))
        save.nation(0).section.set('GovernmentType', 3)
        self.assertEqual(budget_context(save, save.nation(0)).maintenance_multiplier, Decimal(1))
        save.nation(0).section.set('GovernmentType', 0)
        next(s for s in save.documents['example.bcs'].sections if s.name == 'General').set('War', 1)
        self.assertEqual(budget_context(save, save.nation(0)).maintenance_multiplier, Decimal(1))

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

    def test_submarine_cost_by_type_year_and_war(self):
        boat = {'SubType': '3'}
        self.assertEqual(_submarine_cost(boat, 1938, {}), 55)
        self.assertEqual(_submarine_cost(boat, 1945, {'PoorEducation': '1'}, construction=True), 295)
        self.assertEqual(_submarine_cost(boat, 1971, {}, at_war=True), 102)
        self.assertIsNone(_submarine_cost({'SubType': '999'}, 1971, {}))

    def test_base_expansion_uses_fleet_and_base_size(self):
        save = campaign()
        p = SimpleNamespace(owner='USA', area=2, index=3, base='20')
        section = SimpleNamespace(fields=lambda: {'MapArea2Possession3BuildingBase': '1'})
        with patch('privateer.colonies.possessions', return_value=[p]), \
             patch('privateer.colonies.map_document', return_value=('', None, section)):
            self.assertEqual(budget_context(save, save.nation(0)).additional_construction, 1350)

    def test_invasion_is_added_to_total(self):
        save = campaign()
        c = BudgetContext(fleet_size=8, intelligence=0, possession_income=1236,
                          income_multipliers=(Decimal('.97'),), year=1971,
                          invasion_active=True)
        p = project_budget(save.nation(0), context=c)
        self.assertEqual(p.invasion, 6597)
        self.assertEqual(p.total_expenses, p.maintenance + p.construction + p.naval_aircraft +
                         p.research + p.extra_training + p.intelligence + p.invasion)

    def test_aircraft_unit_modifiers_and_reserve(self):
        units = [{'Nation':'0', 'Role':'10', 'AircraftNumber':'10', 'CarrierCapable':'1',
                  'NightCapable':'1', 'HomeBase':'7'}]
        ships = [{'Id':'7', 'Status':'1', 'InPlay':'1', 'ShipType':'CV', 'AircraftCapacity':'30'}]
        self.assertEqual(_aircraft_cost(units, ships, (), 0, {}, 1971, False), 129)
        self.assertIsNone(_aircraft_cost([{'Nation':'0', 'Role':'99'}], (), (), 0, {}, 1971, False))
        self.assertIsNone(_aircraft_cost(units, (), (), 0, {}, 1971, False))

    def test_ship_age_radar_status_and_all_active(self):
        f = {'Maintenance':'100', 'RepairTime':'0', 'Status':'1', 'ShipType':'DD',
             'LocationAreaName':'Northeast Asia', 'YearBuilt':'1920', 'SearchRadarClass':'2',
             'CommanderId':'-1'}
        args = dict(year=1945, month=12, day=1, at_war=False,
                    home_areas={'northeast asia'}, possession_areas={}, officers={})
        self.assertEqual(ship_maintenance(f, **args), 56)
        self.assertEqual(ship_maintenance(f, all_active=True, **args), 113)

    def test_repairs_replace_commander_modifier(self):
        f = {'Maintenance':'100', 'RepairTime':'2', 'Status':'0', 'ShipType':'DD',
             'LocationAreaName':'Northeast Asia', 'YearBuilt':'1940', 'SearchRadarClass':'0',
             'CommanderId':'5'}
        args = dict(year=1945, month=12, day=1, at_war=False,
                    home_areas={'northeast asia'}, possession_areas={},
                    officers={5:{'Special':'17','Special2':'0'}})
        self.assertEqual(ship_maintenance(f, **args), 200)

    def test_foreign_airship_base_receives_airbase_modifier(self):
        f = {'Maintenance':'43', 'RepairTime':'0', 'Status':'0', 'ShipType':'LT',
             'Classname':'Airship base', 'LocationAreaName':'Fiji', 'CommanderId':'-1'}
        args = dict(year=1926, month=12, day=1, at_war=False,
                    home_areas={'northeast asia'}, possession_areas={'fiji':'south pacific'}, officers={})
        self.assertEqual(ship_maintenance(f, installation=True, **args), 46)

    def test_maintenance_and_training_share_eligible_ship_costs(self):
        save = campaign()
        nation = save.nation(0)
        nation.base_resources = 30162
        nation.section.set('BudgetModifier', 16)
        nation.section.set('ResearchPct', 12)
        model = MaintenanceModel(3445, 3531, 2214, 3424, 4, Decimal('.08'))
        c = BudgetContext(fleet_size=8, intelligence=0, possession_income=1050,
                          additional_maintenance=2599, year=1945, maintenance_model=model)
        p = project_budget(nation, context=c)
        self.assertEqual((p.maintenance, p.all_active_maintenance, p.extra_training), (6044, 6130, 1436))

    def test_pending_training_excludes_repairs_and_status_seven(self):
        def vessel(maintenance, repair, status):
            values = {'InPlay':'1', 'Maintenance':str(maintenance), 'RepairTime':str(repair),
                      'Status':str(status), 'ShipType':'DD', 'LocationAreaName':'Northeast Asia',
                      'YearBuilt':'1940', 'CommanderId':'-1'}
            return SimpleNamespace(section=SimpleNamespace(fields=lambda: values))
        fields = {'PendingGunneryTraining':'1', 'NightFighting':'1', 'PendingNightFighting':'1'}
        nation = SimpleNamespace(index=0, name='USA', section=SimpleNamespace(fields=lambda: fields),
                                 ships=[vessel(100,0,0), vessel(20,1,0), vessel(30,0,7)])
        doc = TextDocument.parse('[Officers]\nOfficerNo=0\n')
        save = SimpleNamespace(main_file='RTWGame1.bcs', documents={'RTWGame1.off':doc})
        sections = {'nation0coastalartillery':TextDocument.parse('[Nation0CoastalArtillery]\n').sections[0]}
        home = SimpleNamespace(area=5, owner='USA', value='200', name='Home')
        game = {'Year':'1945', 'Month':'12', 'Day':'1', 'War':'-20'}
        with patch('privateer.maintenance.possessions', return_value=[home]):
            model = fleet_maintenance(save, nation, game, sections)
        self.assertEqual((model.surface, model.surface_all_active, model.training_base, model.training_points),
                         (155, 170, 100, 5))
        self.assertEqual(model.training_rate, Decimal('.08'))
        fields['SurpriseAttack'] = '1'
        game['War'] = '1'
        with patch('privateer.maintenance.possessions', return_value=[home]):
            self.assertEqual(fleet_maintenance(save, nation, game, sections).training_rate, Decimal('.06'))
            fields['PoorEducation'] = '1'
            self.assertEqual(fleet_maintenance(save, nation, game, sections).training_rate, Decimal('.05'))

    def test_ke_date_boundary_uses_fallback_instead_of_guessing(self):
        f = {'Maintenance':'100', 'RepairTime':'0', 'Status':'0', 'ShipType':'KE',
             'LocationAreaName':'Northeast Asia', 'YearBuilt':'1940', 'CommanderId':'-1',
             'ObsoleteDate':str((1945-1900)*365 + 11*30)}
        with self.assertRaisesRegex(ValueError, 'date boundary'):
            ship_maintenance(f, year=1945, month=12, day=1, at_war=False,
                             home_areas={'northeast asia'}, possession_areas={}, officers={})


if __name__ == '__main__':
    unittest.main()

