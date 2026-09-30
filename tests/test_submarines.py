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
    assert rows[1].type_label=='Long range (3)'
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
    assert rows[0].type_label=='Unverified type (4)'
    assert rows[1].status=='Historical'
