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



from privateer.submarines import create_submarine, SUBMARINE_REFERENCES, next_submarine_name


def empty_save(roster=True):
    return save('SubNumber=1\nBuildAreaName=Home\n[General]\nYear=1900\n'
                + ('[Nation0Submarines]\nSubCount=0\n' if roster else ''))


@pytest.mark.parametrize('kind', SUBMARINE_REFERENCES)
@pytest.mark.parametrize('roster',[True,False])
def test_spawn_reference_without_existing_submarines(kind,roster):
    s=empty_save(roster)
    r=create_submarine(s,0,submarine_type=kind,name=next_submarine_name(s,0),location='Home')
    expected=SUBMARINE_REFERENCES[kind]
    assert r.fields['SubType']==expected[0]
    assert r.fields['Availability']==expected[1] and r.fields['Accuracy']==expected[2]
    assert r.status=='In service' and r.fields['RemainingBuildTime']=='0'
    assert r.fields['YearBuilt']=='1900' and r.fields['LocationAreaName']=='Home'
    assert s.nation(0).section.fields()['SubNumber']=='2'
    restored=RTW3Save(Path('.'),{'test.bcs':TextDocument.parse(s.documents['test.bcs'].render())},'test.bcs')
    rows,warnings=submarine_roster(restored,0)
    assert not warnings and len(rows)==1 and rows[0].fields==r.fields
    assert next_submarine_name(restored,0)=='Privateer 2'


@pytest.mark.parametrize('kwargs',[
    {'submarine_type':'bad'}, {'name':''}, {'name':'bad\nname'},
    {'name':'bad=name'}, {'location':'Unknown'}])
def test_invalid_request_is_atomic(kwargs):
    s=empty_save(); before=s.documents['test.bcs'].render()
    args=dict(submarine_type='SS',name='Privateer 1',location='Home');args.update(kwargs)
    with pytest.raises(ValueError): create_submarine(s,0,**args)
    assert not s.modified and s.documents['test.bcs'].render()==before


def test_sequential_names_and_duplicate_rejection():
    s=empty_save()
    for name in ['Privateer 1','PRIVATEER 3','Privateer 2']:
        create_submarine(s,0,submarine_type='SS',name=name,location='Home')
    assert next_submarine_name(s,0)=='Privateer 4'
    before=s.documents['test.bcs'].render()
    with pytest.raises(ValueError):
        create_submarine(s,0,submarine_type='SS',name='privateer 1',location='Home')
    assert s.documents['test.bcs'].render()==before


@pytest.mark.parametrize('old,new', [('SubCount=0','SubCount=1'),
 ('SubNumber=1','SubNumber=bad'),('Year=1900','Year=bad')])
def test_invalid_metadata_is_atomic(old,new):
    base=empty_save(); body=base.documents['test.bcs'].render().replace(old,new)
    s=RTW3Save(Path('.'),{'test.bcs':TextDocument.parse(body)},'test.bcs')
    with pytest.raises(ValueError):
        create_submarine(s,0,submarine_type='SS',name='Privateer 1',location='Home')
    assert s.documents['test.bcs'].render()==body


from privateer.submarines import SubmarineDraft, edit_submarine


def test_draft_isolation_apply_and_reindex():
    s=empty_save()
    for name in ['One','Two','Three']:
        create_submarine(s,0,submarine_type='SS',name=name,location='Home')
    before=s.documents['test.bcs'].render()
    draft=SubmarineDraft(s,0)
    edit_submarine(draft.save,0,0,'delete')
    edit_submarine(draft.save,0,0,'rename','Renamed')
    edit_submarine(draft.save,0,1,'repair')
    assert s.documents['test.bcs'].render()==before
    s.nation(0).section.set('Funds','123')
    assert draft.apply()
    rows,warnings=submarine_roster(s,0)
    assert not warnings and [r.fields['Name'] for r in rows]==['Renamed','Three']
    assert rows[1].fields['Availability']=='135'
    assert s.nation(0).section.fields()['Funds']=='123'
    assert s.nation(0).section.fields()['SubNumber']=='4'


def test_cancel_draft_and_noop_do_not_change_original():
    s=empty_save(False); before=s.documents['test.bcs'].render()
    d=SubmarineDraft(s,0)
    create_submarine(d.save,0,submarine_type='SS',name='Pending',location='Home')
    del d
    assert not s.modified and s.documents['test.bcs'].render()==before
    assert not SubmarineDraft(s,0).apply()


def test_draft_conflict_rejects_without_lost_update():
    s=empty_save();d=SubmarineDraft(s,0)
    create_submarine(d.save,0,submarine_type='SS',name='Pending',location='Home')
    create_submarine(s,0,submarine_type='SS',name='Outside',location='Home')
    with pytest.raises(ValueError,match='outside'):d.apply()
    assert submarine_roster(s,0)[0][0].fields['Name']=='Outside'


def test_repair_only_changes_availability_and_rename_rejects_duplicate():
    s=empty_save()
    for name in ['One','Two']:
        create_submarine(s,0,submarine_type='SS',name=name,location='Home')
    section=next(x for x in s.documents['test.bcs'].sections if x.name=='Nation0Submarines')
    section.set('Sub0Availability',42)
    before=submarine_roster(s,0)[0][0].fields.copy()
    edit_submarine(s,0,0,'repair')
    assert submarine_roster(s,0)[0][0].fields==dict(before,Availability='135')
    with pytest.raises(ValueError):edit_submarine(s,0,0,'rename','Two')
    assert submarine_roster(s,0)[0][0].fields['Name']=='One'
