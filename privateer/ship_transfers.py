"""Transactional flattened-roster transfers for positional v10139 libraries."""
from copy import deepcopy
from pathlib import Path
import re
from .document import FIELD, TextDocument
from .diplomacy import unique_section, unique_integer
from .ship_status import final_fate_transfer_block_reason

SHIP_KEY = re.compile(r'^Ship(\d+)(.+)$')


def replace_line_value(line, value):
    m = FIELD.match(line)
    raw = m.group(4)
    leading = raw[:len(raw)-len(raw.lstrip())]
    trailing = raw[len(raw.rstrip()):]
    return line[:m.start(4)] + leading + str(value) + trailing + line[m.end(4):]


def patch_field(section, key, value):
    matches = [(i,m) for i,line in enumerate(section.lines) if (m:=FIELD.match(line))
               and m.group(2).strip().casefold()==key.casefold()]
    if len(matches)!=1: raise ValueError(f'Missing/duplicate {section.name}/{key}')
    i,_=matches[0];section.lines[i]=replace_line_value(section.lines[i],value)


def roster(save, nation):
    section=unique_section(save,f'Nation{nation.index}Ships')
    records={};others=[];fields={}
    for line in section.lines:
        m=FIELD.match(line)
        key=SHIP_KEY.fullmatch(m.group(2).strip()) if m else None
        if not key:
            others.append(line);continue
        slot=int(key.group(1));suffix=key.group(2)
        if suffix.casefold() in fields.setdefault(slot,set()):
            raise ValueError(f'Duplicate ship field in {section.name}: {m.group(2)}')
        fields[slot].add(suffix.casefold())
        records.setdefault(slot,[]).append(line)
    if sorted(records)!=list(range(len(records))):raise ValueError(f'Noncontiguous ship slots in {section.name}')
    if unique_integer(unique_section(save,f'Nation{nation.index}'),'ShipCount')!=len(records):
        raise ValueError(f'ShipCount mismatch for {nation.name}')
    return section,records,others


def library(save,nation):
    files=[name for name in save.documents if name.casefold()==f'designfiles{nation.index}.des']
    if len(files)!=1:raise ValueError(f'Missing/ambiguous design library for {nation.name}')
    name=files[0];doc=save.documents[name];lines=doc.render().splitlines(keepends=True)
    if not lines or lines[0].strip()!='v10139':raise ValueError(f'Unsupported design format in {name}')
    designs=save._parse_positional_designs(name,doc)
    ids=[d.internal_design_id for d in designs]
    if len(ids)!=len(set(ids)):raise ValueError(f'Duplicate internal design IDs in {name}')
    counter=unique_integer(unique_section(save,f'Nation{nation.index}'),'DesignIDCount')
    if counter<0:raise ValueError(f'Invalid DesignIDCount for {nation.name}')
    return name,doc,lines,designs,counter


def positional_value(line,value):
    return re.sub(r'\S.*?(?=\r?\n|$)',str(value),line,count=1)


def officer_check(save):
    name=Path(save.main_file).with_suffix('.off').name
    path=save.folder/name
    if not path.is_file():raise ValueError('Player transfers require the matching officer file for dependency inspection')
    payload=path.read_bytes()
    try:text=payload.decode('utf-8-sig')
    except UnicodeDecodeError:text=payload.decode('cp1252')
    doc=TextDocument.parse(text)
    sections={s.name:s for s in doc.sections}
    if len(sections)!=len(doc.sections) or set(sections)!={'Officers','CampaignDivisions'}:
        raise ValueError('Unsupported officer-file sections; transfer dependencies need inspection')
    if unique_integer(sections['CampaignDivisions'],'CampDivNo')!=0 or set(sections['CampaignDivisions'].fields())!={'CampDivNo'}:
        raise ValueError('Active campaign divisions are not supported for player transfers; remove the ship from divisions in-game first')
    allowed={'Name','Ability','AbilityKnown','Rank','YearsInRank','Special','Special2','BattleStars','Status','Fate','Id'}
    fields=sections['Officers'].fields()
    for key in fields:
        m=re.fullmatch(r'Officer\d+(.+)',key)
        if key!='OfficerNo' and (not m or m.group(1) not in allowed):
            raise ValueError(f'Unrecognized officer assignment field: {key}')
    ids=[int(v) for k,v in fields.items() if re.fullmatch(r'Officer\d+Id',k)]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate officer IDs')
    return set(ids)


def transfer_batch(save, assignments):
    """Assignments map permanent hull IDs to destination save-slot indices."""
    if not assignments:return
    save.validate_or_raise()
    working=deepcopy(save)
    before={s.record_index:(n.index,dict(s.section.fields())) for n in working.nations for s in n.ships}
    ships={s.record_index:s for n in working.nations for s in n.ships}
    nation_indices={nation.index for nation in working.nations}
    planned=[];affected=set()
    for hull,dest in assignments.items():
        if (type(hull) is not int or hull not in ships or type(dest) is not int
                or dest not in nation_indices):
            raise ValueError('Choose an existing hull ID and destination nation slot')
        target=working.nation(dest);ship=ships[hull];source=working.nation(ship.owner_index)
        if source.index==dest:continue
        if not ship.flattened_record:raise ValueError('This transfer manager supports flattened NationNShips rosters')
        fields=ship.section.fields()
        if reason := final_fate_transfer_block_reason(ship, fields):
            raise ValueError(f'{ship.name}: {reason}')
        if int(fields.get('AircraftCapacity','0'))>0 or ship.ship_type in ('CV','CVL','AV'):
            raise ValueError(f'{ship.name}: carrier/air-group migration is not decoded')
        for key in ('DesignRefId','BuildingNationIdx','CommanderId'):
            if key not in fields:raise ValueError(f'{ship.name}: missing {key}')
        commander=int(fields['CommanderId'])
        if source.is_player or target.is_player:
            officers=officer_check(working)
            if source.is_player and commander!=-1 and commander not in officers:
                raise ValueError(f'{ship.name}: commander does not resolve in officer file')
        if not source.is_player and commander!=-1:
            raise ValueError(f'{ship.name}: non-player commander dependency is unsupported')
        if (working.player_detection_warning or '').startswith('Multiple'):
            raise ValueError('Ambiguous player metadata')
        planned.append((ship,source,target));affected.update((source.index,target.index))
    if not planned:return
    raw_rosters={i:roster(working,working.nation(i)) for i in affected}
    libraries={i:library(working,working.nation(i)) for i in affected}
    raw_by_id={s.record_index:list(raw_rosters[n.index][1][s.local_slot])
               for n in working.nations if n.index in affected for s in n.ships}
    final_ids={i:[s.record_index for s in working.nation(i).ships] for i in affected}
    clone_map={};new_blocks={};counters={i:lib[4] for i,lib in libraries.items()};changes={}
    for ship,source,target in planned:
        source_designs=[d for d in libraries[source.index][3] if d.internal_design_id==ship.design_ref_id]
        if len(source_designs)!=1:raise ValueError(f'{ship.name}: source design missing or ambiguous')
        design=source_designs[0];key=(source.index,ship.design_ref_id,target.index)
        if key not in clone_map:
            dest_designs=libraries[target.index][3]
            new_id=max(counters[target.index],max((d.internal_design_id for d in dest_designs),default=0))+1
            if new_id>2147483647:raise ValueError('Design ID allocation exceeds integer range')
            ordinal=len(dest_designs)+len(new_blocks.get(target.index,[]))
            block=list(design.positional_record)
            block[0]=positional_value(block[0],f'ShipDesign{ordinal}')
            block[4]=positional_value(block[4],new_id)
            new_blocks.setdefault(target.index,[]).append(block)
            counters[target.index]=new_id;clone_map[key]=new_id
            working.audit.append(f'Copied {source.name} design {ship.design_ref_id} to {target.name}: ordinal {ordinal}, internal ID {new_id}')
        # BuildingNationIdx is historical builder data, not current ownership.
        # Ownership is expressed by the containing NationNShips roster.
        edits={'DesignRefId':clone_map[key]}
        if source.is_player and not target.is_player:edits['CommanderId']=-1
        changes[ship.record_index]=edits
        for index,line in enumerate(raw_by_id[ship.record_index]):
            m=FIELD.match(line);suffix=SHIP_KEY.fullmatch(m.group(2).strip()).group(2)
            if suffix in edits:raw_by_id[ship.record_index][index]=replace_line_value(line,edits[suffix])
        final_ids[source.index].remove(ship.record_index);final_ids[target.index].append(ship.record_index)
        working.audit.append(f'Transferred hull {ship.record_index} {ship.name}: Nation{source.index} -> Nation{target.index}; design {ship.design_ref_id} -> {edits["DesignRefId"]}; builder {ship.building_nation_index} preserved; commander {ship.section.fields()["CommanderId"]} -> {edits.get("CommanderId",ship.section.fields()["CommanderId"])}')
    for i in affected:
        section,_,others=raw_rosters[i];lines=list(others)
        for slot,hull in enumerate(final_ids[i]):
            for line in raw_by_id[hull]:
                m=FIELD.match(line);start,end=m.span(2)
                prefix=re.sub(r'Ship\d+',f'Ship{slot}',m.group(2),count=1)
                if lines and not lines[-1].endswith(('\n','\r')):lines[-1]+=working.documents[working.main_file].newline
                lines.append(line[:start]+prefix+line[end:])
        section.lines=lines
        patch_field(working.nation(i).section,'ShipCount',len(final_ids[i]))
    for i,blocks in new_blocks.items():
        name,doc,lines,designs,_=libraries[i]
        lines[1]=positional_value(lines[1],len(designs)+len(blocks))
        for block in blocks:
            if lines and not lines[-1].endswith(('\n','\r')):lines[-1]+=doc.newline
            lines.extend(block)
        working.documents[name]=TextDocument.parse(''.join(lines),encoding=doc.encoding,has_bom=doc.has_bom)
        patch_field(working.nation(i).section,'DesignIDCount',counters[i])
    working.nations=[];working._build_model();working.validate_or_raise()
    after={s.record_index:(n.index,dict(s.section.fields())) for n in working.nations for s in n.ships}
    if set(before)!=set(after):raise ValueError('Transfer changed permanent hull IDs')
    for hull,(owner,fields) in before.items():
        expected=dict(fields);expected.update({k:str(v) for k,v in changes.get(hull,{}).items()})
        if after[hull]!=(assignments.get(hull,owner),expected):raise ValueError(f'Hull preservation failed: {hull}')
    for i in affected:roster(working,working.nation(i))
    for doc in working.documents.values():doc.to_bytes()  # Reject incompatible encodings before commit.
    save.documents,save.nations,save.audit=working.documents,working.nations,working.audit
    save.modified=True;save._ship_changes=True
