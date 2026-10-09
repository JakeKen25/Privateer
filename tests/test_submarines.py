from pathlib import Path
import pytest
from privateer.document import TextDocument
from privateer.save import RTW3Save
from privateer.submarines import submarine_roster


def save(body):
    return RTW3Save(Path('.'), {'test.bcs':TextDocument.parse('[Nation0]\nName=Test\n'+body)}, 'test.bcs')


def test_history_wins_over_inplay_and_positive_build_time():
    s=save('[Nation0Submarines]\nSubCount=3\nSub0Name=Same\nSub0Sunk=1\nSub0InPlay=1\nSub0RemainingBuildTime=10\nSub1Name=Same\nSub1Sunk=0\nSub1InPlay=0\nSub1Halted=0\nSub1SubType=3\nSub2Sunk=0\nSub2InPlay=1\nSub2Active=0\nSub2Extra=keep\n')
    before=s.documents['test.bcs'].render()
    rows,warnings=submarine_roster(s,0)
    assert not warnings
    assert [r.status for r in rows]==['Sunk','Under construction','In service']
    assert rows[0].slot!=rows[1].slot
    assert rows[1].type_label=='SSL — Long range submarine'
    assert rows[1].value('LocationAreaName')==''
    assert rows[2].fields['Extra']=='keep'
    assert before==s.documents['test.bcs'].render() and not s.modified


def test_missing_empty_and_mismatched_rosters_are_distinct():
    assert submarine_roster(save(''),0)[1]
    assert submarine_roster(save('[Nation0Submarines]\nSubCount=0\n'),0)==((),())
    rows,warnings=submarine_roster(save('[Nation0Submarines]\nSubCount=1\nSub3Name=A\n'),0)
    assert warnings and rows[0].slot==3 and rows[0].status=='Unknown'


@pytest.mark.parametrize('body',[
    '[Nation0Submarines]\nSubCount=0\n[Nation0Submarines]\nSubCount=0\n',
    '[Nation0Submarines]\nSubCount=1\nSub0Name=A\nSub0Name=B\n'])
def test_ambiguity_is_reported(body):
    with pytest.raises(ValueError,match='Duplicate'):
        submarine_roster(save(body),0)


def test_halted_and_unknown_type_and_fate():
    rows,_=submarine_roster(save('[Nation0Submarines]\nSubCount=2\nSub0Sunk=0\nSub0InPlay=0\nSub0Halted=1\nSub0SubType=4\nSub1Sunk=0\nSub1Fate=Scrapped\nSub1InPlay=1\n'),0)
    assert rows[0].status=='Construction halted'
    assert rows[0].type_label=='SSG — Missile submarine'
    assert rows[1].status=='Historical'


from privateer.submarines import create_submarine, SUBMARINE_TYPES


def construction_save(kind='0'):
    s = save('SubNumber=126\n[Nation0Submarines]\nSubCount=1\n'
                'Sub0Name=Template\nSub0Sunk=0\nSub0InPlay=1\nSub0Halted=0\n'
                f'Sub0SubType={kind}\nSub0Availability=135\nSub0Accuracy=1\n'
                'Sub0RemainingBuildTime=12\nSub0Fate=\nSub0YearBuilt=0\n'
                'Sub0Active=0\nSub0DestinationAreaName=XXX\nSub0OrderedAreaName=XXX\n'
                'Sub0UnknownField=preserve\n[Nation1]\nName=Other\nSubNumber=5\n')
    doc=s.documents['test.bcs']
    from privateer.document import Section
    doc.add_section(Section('General','[General]\n',['Year=1968\n']))
    section=next(x for x in doc.sections if x.name=='Nation0Submarines')
    for k,v in {'Name':'Service boat','InPlay':'1','Sunk':'0','Fate':'',
                'LocationAreaName':'Home','SubType':'0','Availability':'135','Accuracy':'0'}.items():
        section.set('Sub1'+k,v)
    section.set('SubCount',2)
    return s


@pytest.mark.parametrize('kind', SUBMARINE_TYPES)
def test_create_preserves_template_and_appends_valid_construction(kind):
    s=construction_save(kind)
    before=submarine_roster(s,0)[0][0].fields.copy()
    a=create_submarine(s,0,template_slot=0,location='Home',name='New boat')
    b=create_submarine(s,0,template_slot=0,location='Home',name='Second boat')
    assert (a.slot,b.slot)==(2,3)
    assert a.type_label==SUBMARINE_TYPES[kind] and a.status=='In service'
    assert a.fields['UnknownField']=='preserve' and a.fields['Accuracy']=='1'
    assert a.fields['YearBuilt']=='1968' and a.fields['RemainingBuildTime']=='0'
    assert a.fields['LocationAreaName']=='Home'
    doc=s.documents['test.bcs']
    restored=RTW3Save(Path('.'),{'test.bcs':TextDocument.parse(doc.render())},'test.bcs')
    rows,warnings=submarine_roster(restored,0)
    assert not warnings and len(rows)==4 and rows[0].fields==before
    assert restored.nation(0).section.fields()['SubNumber']=='128'
    assert restored.nation(1).section.fields()['SubNumber']=='5'
    assert s.modified and len(s.audit)==2


@pytest.mark.parametrize('name',['','Template','template','bad\nname','bad=name'])
def test_invalid_names_do_not_mutate(name):
    s=construction_save(); before=s.documents['test.bcs'].render()
    with pytest.raises(ValueError):
        create_submarine(s,0,template_slot=0,location='Home',name=name)
    assert s.documents['test.bcs'].render()==before and not s.modified


@pytest.mark.parametrize('old,new', [('SubCount=2','SubCount=3'),
    ('Sub0Sunk=0','Sub0Sunk=1'),
    ('Sub0InPlay=1','Sub0InPlay=0'),('SubNumber=126','SubNumber=bad'),
    ('Year=1968','Year=bad')])
def test_unsafe_templates_and_counts_rejected(old,new):
    base=construction_save(); body=base.documents['test.bcs'].render().replace(old,new)
    s=RTW3Save(Path('.'),{'test.bcs':TextDocument.parse(body)},'test.bcs')
    with pytest.raises(ValueError):
        create_submarine(s,0,template_slot=0,location='Home',name='New')
    assert s.documents['test.bcs'].render()==body and not s.modified


def test_spawn_rejects_unknown_location_without_mutation():
    s=construction_save(); before=s.documents['test.bcs'].render()
    with pytest.raises(ValueError,match='location'):
        create_submarine(s,0,template_slot=0,name='New',location='Unknown')
    assert s.documents['test.bcs'].render()==before


def test_in_service_template_can_spawn():
    s=construction_save()
    r=create_submarine(s,0,template_slot=1,name='New',location='Home')
    assert r.status=='In service' and r.fields['RemainingBuildTime']=='0'
