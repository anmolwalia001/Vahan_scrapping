# db/seed.py
from __future__ import annotations
from datetime import datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    # Fallback for environments without IANA tz database (e.g., Windows without tzdata)
    IST = timezone(timedelta(hours=5, minutes=30))

# from zoneinfo import ZoneInfo
from typing import Dict, List, Optional
import sys
import pathlib

# IST = ZoneInfo("Asia/Kolkata")

# allow "python db/seed.py" when run from project root
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session

from db.session import SessionLocal
from db.models import (
    PortalSite, PortalField, PortalFieldOption,
    State, RTO,
    AxisFilter, VehicleFilter,
    UserAgentPool, UserAgent, JobTemplate
)

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def get_or_create(session: Session, model, defaults=None, **kwargs):
    inst = session.query(model).filter_by(**kwargs).one_or_none()
    if inst:
        if defaults:
            for k, v in defaults.items():
                setattr(inst, k, v)
        return inst, False
    params = {**kwargs, **(defaults or {})}
    inst = model(**params)
    session.add(inst)
    return inst, True


def ensure_portal_field(session: Session, site_id: int, field_name: str,
                        selector: str, ui_type: str = "select",
                        depends_on_id: Optional[int] = None) -> PortalField:
    row = session.query(PortalField).filter(
        PortalField.site_id == site_id,
        PortalField.field_name == field_name
    ).one_or_none()
    if row:
        row.selector = selector
        row.ui_type = ui_type
        row.depends_on_id = depends_on_id
        return row
    row = PortalField(
        site_id=site_id, field_name=field_name,
        selector=selector, ui_type=ui_type, depends_on_id=depends_on_id
    )
    session.add(row)
    return row


def ensure_field_option(session: Session, field_id: int,
                        value_code: str, label: str, parent_code: Optional[str]) -> PortalFieldOption:
    now = datetime.now(IST).replace(tzinfo=None)
    row = session.query(PortalFieldOption).filter(
        PortalFieldOption.field_id == field_id,
        PortalFieldOption.value_code == value_code
    ).one_or_none()
    if row:
        row.label = label
        row.parent_code = parent_code
        row.is_active = True
        row.last_seen_at = now
        row.first_seen_at = row.first_seen_at or now
        return row
    row = PortalFieldOption(
        field_id=field_id, value_code=value_code, label=label,
        parent_code=parent_code, is_active=True,
        first_seen_at=now, last_seen_at=now
    )
    session.add(row)
    return row


# ──────────────────────────────────────────────────────────────────────────────
# Static seed for axis & vehicle filters (from your POC)
# ──────────────────────────────────────────────────────────────────────────────

AXIS_ROWS = [
    {"axis": "Y", "filter": "Maker"},
    {"axis": "X", "filter": "Month Wise"},
]

VEHICLE_FILTER_ROWS = [
    {"name": "MOTOR CAR"},
    {"name": "MOTOR CAB"},
    {"name": "ELECTRIC(BOV)"},
    {"name": "PURE EV"},
]

# ──────────────────────────────────────────────────────────────────────────────
# Payloads you provided (trimmed to what you sent). You can extend later.
# ──────────────────────────────────────────────────────────────────────────────

ALL_STATES_BLOB = {
  "extraction_date": "2025-07-29T13:09:38.601830",
  "total_states": 36,
  "states": [
    {"name":"All Vahan4 Running States (35/36)","display_name":"All Vahan4 Running States (35/36)","code":"AL","value":"-1","index":0},
    {"name":"Andaman & Nicobar Island","display_name":"Andaman & Nicobar Island(3)","code":"AN","value":"AN","index":1},
    {"name":"Andhra Pradesh","display_name":"Andhra Pradesh(83)","code":"AP","value":"AP","index":2},
    {"name":"Arunachal Pradesh","display_name":"Arunachal Pradesh(29)","code":"AR","value":"AR","index":3},
    {"name":"Assam","display_name":"Assam(33)","code":"AS","value":"AS","index":4},
    {"name":"Bihar","display_name":"Bihar(48)","code":"BR","value":"BR","index":5},
    {"name":"Chhattisgarh","display_name":"Chhattisgarh(31)","code":"CG","value":"CG","index":6},
    {"name":"Chandigarh","display_name":"Chandigarh(1)","code":"CH","value":"CH","index":7},
    {"name":"UT of DNH and DD","display_name":"UT of DNH and DD(3)","code":"UT","value":"DD","index":8},
    {"name":"Delhi","display_name":"Delhi(16)","code":"DL","value":"DL","index":9},
    {"name":"Goa","display_name":"Goa(13)","code":"GA","value":"GA","index":10},
    {"name":"Gujarat","display_name":"Gujarat(37)","code":"GJ","value":"GJ","index":11},
    {"name":"Himachal Pradesh","display_name":"Himachal Pradesh(96)","code":"HP","value":"HP","index":12},
    {"name":"Haryana","display_name":"Haryana(98)","code":"HR","value":"HR","index":13},
    {"name":"Jharkhand","display_name":"Jharkhand(25)","code":"JH","value":"JH","index":14},
    {"name":"Jammu and Kashmir","display_name":"Jammu and Kashmir(21)","code":"JK","value":"JK","index":15},
    {"name":"Karnataka","display_name":"Karnataka(68)","code":"KA","value":"KA","index":16},
    {"name":"Kerala","display_name":"Kerala(87)","code":"KL","value":"KL","index":17},
    {"name":"Ladakh","display_name":"Ladakh(3)","code":"LA","value":"LA","index":18},
    {"name":"Lakshadweep","display_name":"Lakshadweep(6)","code":"LA","value":"LD","index":19},
    {"name":"Maharashtra","display_name":"Maharashtra(59)","code":"MH","value":"MH","index":20},
    {"name":"Meghalaya","display_name":"Meghalaya(15)","code":"ML","value":"ML","index":21},
    {"name":"Manipur","display_name":"Manipur(13)","code":"MN","value":"MN","index":22},
    {"name":"Madhya Pradesh","display_name":"Madhya Pradesh(53)","code":"MP","value":"MP","index":23},
    {"name":"Mizoram","display_name":"Mizoram(10)","code":"MZ","value":"MZ","index":24},
    {"name":"Nagaland","display_name":"Nagaland(9)","code":"NL","value":"NL","index":25},
    {"name":"Odisha","display_name":"Odisha(39)","code":"OD","value":"OR","index":26},
    {"name":"Punjab","display_name":"Punjab(96)","code":"PB","value":"PB","index":27},
    {"name":"Puducherry","display_name":"Puducherry(8)","code":"PY","value":"PY","index":28},
    {"name":"Rajasthan","display_name":"Rajasthan(59)","code":"RJ","value":"RJ","index":29},
    {"name":"Sikkim","display_name":"Sikkim(9)","code":"SK","value":"SK","index":30},
    {"name":"Tamil Nadu","display_name":"Tamil Nadu(148)","code":"TN","value":"TN","index":31},
    {"name":"Tripura","display_name":"Tripura(9)","code":"TR","value":"TR","index":32},
    {"name":"Uttarakhand","display_name":"Uttarakhand(21)","code":"UK","value":"UK","index":33},
    {"name":"Uttar Pradesh","display_name":"Uttar Pradesh(77)","code":"UP","value":"UP","index":34},
    {"name":"West Bengal","display_name":"West Bengal(59)","code":"WB","value":"WB","index":35}
  ]
}

ALL_STATE_ONLY_RTO = {
  "state": "All Vahan4 Running States",
  "state_code": "AL",
  "extraction_date": "2025-07-23T13:25:01.608237",
  "total_rtos": 1,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1",
     "full_text":"All Vahan4 Running Office(1386/1445)"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Chandigarh
# ──────────────────────────────────────────────────────────────────────────────
STATE_CH = {
  "state": "Chandigarh",
  "state_code": "CH",
  "extraction_date": "2025-07-29T13:45:08.603262",
  "total_rtos": 2,
  "rtos": [
    {"name": "All Vahan4 Running Office", "code": "ALL", "value": "-1",
     "full_text": "All Vahan4 Running Office(1/1)"},
    {"name": "CHANDIGARH UT (RLA AND STA)", "code": "CH1", "value": "1",
     "full_text": "CHANDIGARH UT (RLA AND STA) - CH1( 08-JAN-2018 )"}
  ]
}


STATE_AN = {  # Andaman & Nicobar
  "state": "Andaman & Nicobar Island",
  "state_code": "AN",
  "extraction_date": "2025-07-29T13:17:46.131813",
  "total_rtos": 11,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(5/5)"},
    {"name":"Baratang","code":"AN201","value":"201","full_text":"Baratang - AN201( 29-NOV-2024 )"},
    {"name":"Campbell Bay","code":"AN212","value":"212","full_text":"Campbell Bay - AN212( 18-FEB-2022 )"},
    {"name":"Car Nicobar","code":"AN211","value":"211","full_text":"Car Nicobar - AN211( 23-FEB-2023 )"},
    {"name":"Diglipur","code":"AN204","value":"204","full_text":"Diglipur - AN204( 09-NOV-2021 )"},
    {"name":"Ferrargunj","code":"AN200","value":"200","full_text":"Ferrargunj - AN200( 12-OCT-2021 )"},
    {"name":"Little Andaman","code":"AN207","value":"207","full_text":"Little Andaman - AN207( 17-FEB-2025 )"},
    {"name":"Mayabunder","code":"AN203","value":"203","full_text":"Mayabunder - AN203( 09-NOV-2021 )"},
    {"name":"Port Blair DTO","code":"AN1","value":"1","full_text":"Port Blair DTO - AN1( 15-AUG-2020 )"},
    {"name":"Rangat","code":"AN202","value":"202","full_text":"Rangat - AN202( 17-NOV-2021 )"},
    {"name":"Swaraj Dweep","code":"AN206","value":"206","full_text":"Swaraj Dweep - AN206( 29-NOV-2021 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Karnataka — Python seeder
# ──────────────────────────────────────────────────────────────────────────────

STATE_KA = {
  "state": "Karnataka",
  "state_code": "KA",
  "extraction_date": "2025-07-29T14:07:04.393550",
  "total_rtos": 69,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(68/68)"},
    {"name":"ATHANI ARTO","code":"KA71","value":"71","full_text":"ATHANI ARTO - KA71( 03-AUG-2020 )"},
    {"name":"BAGALKOT  RTO","code":"KA29","value":"29","full_text":"BAGALKOT  RTO - KA29( 29-SEP-2018 )"},
    {"name":"BAILHONGAL  RTO","code":"KA24","value":"24","full_text":"BAILHONGAL  RTO - KA24( 13-AUG-2018 )"},
    {"name":"BANTWALA ARTO","code":"KA70","value":"70","full_text":"BANTWALA ARTO - KA70( 03-MAR-2018 )"},
    {"name":"BASAVAKALYAN ARTO","code":"KA56","value":"56","full_text":"BASAVAKALYAN ARTO - KA56( 01-AUG-2018 )"},
    {"name":"BELLARY  RTO","code":"KA34","value":"34","full_text":"BELLARY  RTO - KA34( 31-JUL-2018 )"},
    {"name":"BENGALURU CENTRAL  RTO","code":"KA1","value":"1","full_text":"BENGALURU CENTRAL  RTO - KA1( 21-JAN-2019 )"},
    {"name":"BENGALURU EAST  RTO","code":"KA3","value":"3","full_text":"BENGALURU EAST  RTO - KA3( 04-FEB-2019 )"},
    {"name":"BENGALURU NORTH  RTO","code":"KA4","value":"4","full_text":"BENGALURU NORTH  RTO - KA4( 28-JAN-2019 )"},
    {"name":"BENGALURU SOUTH  RTO","code":"KA5","value":"5","full_text":"BENGALURU SOUTH  RTO - KA5( 07-JAN-2019 )"},
    {"name":"BENGALURU WEST  RTO","code":"KA2","value":"2","full_text":"BENGALURU WEST  RTO - KA2( 26-DEC-2018 )"},
    {"name":"BHALKI  ARTO","code":"KA39","value":"39","full_text":"BHALKI  ARTO - KA39( 31-JUL-2018 )"},
    {"name":"BIDAR  RTO","code":"KA38","value":"38","full_text":"BIDAR  RTO - KA38( 01-AUG-2018 )"},
    {"name":"BIJAPUR  RTO","code":"KA28","value":"28","full_text":"BIJAPUR  RTO - KA28( 29-SEP-2018 )"},
    {"name":"CHAMARAJANAGAR  RTO","code":"KA10","value":"10","full_text":"CHAMARAJANAGAR  RTO - KA10( 23-JUL-2018 )"},
    {"name":"CHANDAPURA, BENGALURU RTO","code":"KA59","value":"59","full_text":"CHANDAPURA, BENGALURU RTO - KA59( 08-FEB-2018 )"},
    {"name":"CHICKABALLAPUR  RTO","code":"KA40","value":"40","full_text":"CHICKABALLAPUR  RTO - KA40( 27-JUN-2018 )"},
    {"name":"CHIKAMANGLUR RTO","code":"KA18","value":"18","full_text":"CHIKAMANGLUR RTO - KA18( 12-JUN-2018 )"},
    {"name":"CHIKKODI  RTO","code":"KA23","value":"23","full_text":"CHIKKODI  RTO - KA23( 22-SEP-2018 )"},
    {"name":"CHINTAMANI ARTO","code":"KA67","value":"67","full_text":"CHINTAMANI ARTO - KA67( 16-JUL-2018 )"},
    {"name":"CHITRADURGA  RTO","code":"KA16","value":"16","full_text":"CHITRADURGA  RTO - KA16( 09-AUG-2018 )"},
    {"name":"DANDELI ARTO","code":"KA65","value":"65","full_text":"DANDELI ARTO - KA65( 28-SEP-2018 )"},
    {"name":"DAVANAGERE  RTO","code":"KA17","value":"17","full_text":"DAVANAGERE  RTO - KA17( 02-JUL-2018 )"},
    {"name":"DEVANAHALLI  ARTO","code":"KA43","value":"43","full_text":"DEVANAHALLI  ARTO - KA43( 28-JUN-2018 )"},
    {"name":"DHARWAD EAST RTO","code":"KA63","value":"63","full_text":"DHARWAD EAST RTO - KA63( 25-SEP-2018 )"},
    {"name":"DHARWAD WEST RTO","code":"KA25","value":"25","full_text":"DHARWAD WEST RTO - KA25( 25-SEP-2018 )"},
    {"name":"ELECTRONIC CITY  RTO","code":"KA51","value":"51","full_text":"ELECTRONIC CITY  RTO - KA51( 31-DEC-2018 )"},
    {"name":"GADAG  RTO","code":"KA26","value":"26","full_text":"GADAG  RTO - KA26( 25-SEP-2018 )"},
    {"name":"GOKAK  ARTO","code":"KA49","value":"49","full_text":"GOKAK  ARTO - KA49( 25-SEP-2018 )"},
    {"name":"HASSAN  RTO","code":"KA13","value":"13","full_text":"HASSAN  RTO - KA13( 09-JUL-2018 )"},
    {"name":"HAVERI  RTO","code":"KA27","value":"27","full_text":"HAVERI  RTO - KA27( 23-MAR-2018 )"},
    {"name":"HONNAVAR  ARTO","code":"KA47","value":"47","full_text":"HONNAVAR  ARTO - KA47( 29-SEP-2018 )"},
    {"name":"HOSPET  RTO","code":"KA35","value":"35","full_text":"HOSPET  RTO - KA35( 28-JUL-2018 )"},
    {"name":"HUNSUR  ARTO","code":"KA45","value":"45","full_text":"HUNSUR  ARTO - KA45( 11-JUL-2018 )"},
    {"name":"JAMKHANDI  ARTO","code":"KA48","value":"48","full_text":"JAMKHANDI  ARTO - KA48( 21-DEC-2018 )"},
    {"name":"JNANABHARATHI  RTO","code":"KA41","value":"41","full_text":"JNANABHARATHI  RTO - KA41( 24-JAN-2019 )"},
    {"name":"KALABURAGI  RTO","code":"KA32","value":"32","full_text":"KALABURAGI  RTO - KA32( 25-JUL-2018 )"},
    {"name":"KARWAR  RTO","code":"KA30","value":"30","full_text":"KARWAR  RTO - KA30( 29-SEP-2018 )"},
    {"name":"K G F  ARTO","code":"KA8","value":"8","full_text":"K G F  ARTO - KA8( 21-JUN-2018 )"},
    {"name":"KOLAR  RTO","code":"KA7","value":"7","full_text":"KOLAR  RTO - KA7( 21-JUN-2018 )"},
    {"name":"KOPPAL  RTO","code":"KA37","value":"37","full_text":"KOPPAL  RTO - KA37( 02-AUG-2018 )"},
    {"name":"KRISHNARAJAPURAM  RTO","code":"KA53","value":"53","full_text":"KRISHNARAJAPURAM  RTO - KA53( 06-FEB-2019 )"},
    {"name":"MADHUGIRI, TUMAKURU ARTO","code":"KA64","value":"64","full_text":"MADHUGIRI, TUMAKURU ARTO - KA64( 22-FEB-2019 )"},
    {"name":"MADIKERI  RTO","code":"KA12","value":"12","full_text":"MADIKERI  RTO - KA12( 23-JUL-2018 )"},
    {"name":"MANDYA  RTO","code":"KA11","value":"11","full_text":"MANDYA  RTO - KA11( 21-JUL-2018 )"},
    {"name":"MANGALORE  RTO","code":"KA19","value":"19","full_text":"MANGALORE  RTO - KA19( 27-MAR-2018 )"},
    {"name":"MYSURU  EAST  RTO","code":"KA55","value":"55","full_text":"MYSURU  EAST  RTO - KA55( 12-JUL-2018 )"},
    {"name":"MYSURU WEST  RTO","code":"KA9","value":"9","full_text":"MYSURU WEST  RTO - KA9( 12-JUL-2018 )"},
    {"name":"NAGAMANGALA  RTO","code":"KA54","value":"54","full_text":"NAGAMANGALA  RTO - KA54( 23-JUL-2018 )"},
    {"name":"NELAMANGALA  RTO","code":"KA52","value":"52","full_text":"NELAMANGALA  RTO - KA52( 13-AUG-2018 )"},
    {"name":"PUTTUR  RTO","code":"KA21","value":"21","full_text":"PUTTUR  RTO - KA21( 27-MAR-2018 )"},
    {"name":"RAICHUR  RTO","code":"KA36","value":"36","full_text":"RAICHUR  RTO - KA36( 27-JUL-2018 )"},
    {"name":"RAMANAGAR  RTO","code":"KA42","value":"42","full_text":"RAMANAGAR  RTO - KA42( 02-JAN-2018 )"},
    {"name":"RAMDURGA ARTO","code":"KA69","value":"69","full_text":"RAMDURGA ARTO - KA69( 19-JUL-2018 )"},
    {"name":"RANIBENNUR ARTO","code":"KA68","value":"68","full_text":"RANIBENNUR ARTO - KA68( 24-FEB-2018 )"},
    {"name":"REGIONAL TRANSPORT OFFICE BELAGAVI","code":"KA22","value":"22","full_text":"REGIONAL TRANSPORT OFFICE BELAGAVI - KA22( 20-SEP-2018 )"},
    {"name":"SAGAR  ARTO","code":"KA15","value":"15","full_text":"SAGAR  ARTO - KA15( 29-JUN-2018 )"},
    {"name":"SAKALESHPURA  ARTO","code":"KA46","value":"46","full_text":"SAKALESHPURA  ARTO - KA46( 09-JUL-2018 )"},
    {"name":"SHIMOGA  RTO","code":"KA14","value":"14","full_text":"SHIMOGA  RTO - KA14( 29-JUN-2018 )"},
    {"name":"SIRSI  RTO","code":"KA31","value":"31","full_text":"SIRSI  RTO - KA31( 29-SEP-2018 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"KA99","value":"99","full_text":"STATE TRANSPORT AUTHORITY - KA99( 15-APR-2021 )"},
    {"name":"STU AND AUTORIKSHAW,  SHANTHINAGAR RTO","code":"KA57","value":"57","full_text":"STU AND AUTORIKSHAW,  SHANTHINAGAR RTO - KA57( 26-APR-2021 )"},
    {"name":"TARIKERE, CHIKKAMAGALURU ARTO","code":"KA66","value":"66","full_text":"TARIKERE, CHIKKAMAGALURU ARTO - KA66( 12-JUN-2018 )"},
    {"name":"TIPTUR  ARTO","code":"KA44","value":"44","full_text":"TIPTUR  ARTO - KA44( 28-JUN-2018 )"},
    {"name":"TUMKUR  RTO","code":"KA6","value":"6","full_text":"TUMKUR  RTO - KA6( 25-JUN-2018 )"},
    {"name":"UDUPI  RTO","code":"KA20","value":"20","full_text":"UDUPI  RTO - KA20( 14-JUN-2018 )"},
    {"name":"YADGIRI  RTO","code":"KA33","value":"33","full_text":"YADGIRI  RTO - KA33( 26-JUL-2018 )"},
    {"name":"YALAHANKA  RTO","code":"KA50","value":"50","full_text":"YALAHANKA  RTO - KA50( 31-JAN-2019 )"},
  ]
}

# Quick sanity check for duplicate RTO codes
_codes = [rt["code"] for rt in STATE_KA["rtos"]]
assert len(_codes) == len(set(_codes)), "Duplicate RTO codes detected in KA payload"

STATE_AP = {
  "state": "Andhra Pradesh",
  "state_code": "AP",
  "extraction_date": "2025-07-29T13:36:17.902745",
  "total_rtos": 84,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(83/83)"},
    {"name":"Adoni RTO","code":"AP221","value":"221","full_text":"Adoni RTO - AP221( 06-MAY-2022 )"},
    {"name":"Amalapuram RTA","code":"AP205","value":"205","full_text":"Amalapuram RTA - AP205( 25-APR-2022 )"},
    {"name":"Anakapalli RTA","code":"AP131","value":"131","full_text":"Anakapalli RTA - AP131( 25-APR-2022 )"},
    {"name":"Anantapur RTA","code":"AP2","value":"2","full_text":"Anantapur RTA - AP2( 25-APR-2022 )"},
    {"name":"Atmakur-Kurnool MVI Office","code":"AP321","value":"321","full_text":"Atmakur-Kurnool MVI Office - AP321( 06-MAY-2022 )"},
    {"name":"Atmakur MVI Office","code":"AP126","value":"126","full_text":"Atmakur MVI Office - AP126( 11-MAY-2022 )"},
    {"name":"Badvel MVI Office","code":"AP104","value":"104","full_text":"Badvel MVI Office - AP104( 06-MAY-2022 )"},
    {"name":"BAPATLA RTO OFFICE","code":"AP207","value":"207","full_text":"BAPATLA RTO OFFICE - AP207( 25-APR-2022 )"},
    {"name":"Bhimavaram RTA","code":"AP137","value":"137","full_text":"Bhimavaram RTA - AP137( 25-APR-2022 )"},
    {"name":"Chilakaluripeta MVI Office","code":"AP307","value":"307","full_text":"Chilakaluripeta MVI Office - AP307( 06-MAY-2022 )"},
    {"name":"Chintoor","code":"AP905","value":"905","full_text":"Chintoor - AP905( 09-JUN-2022 )"},
    {"name":"Chirala UO","code":"AP127","value":"127","full_text":"Chirala UO - AP127( 06-MAY-2022 )"},
    {"name":"Chittoor RTA","code":"AP3","value":"3","full_text":"Chittoor RTA - AP3( 25-APR-2022 )"},
    {"name":"Cuddapah RTA","code":"AP4","value":"4","full_text":"Cuddapah RTA - AP4( 25-APR-2022 )"},
    {"name":"Darsi UO","code":"AP427","value":"427","full_text":"Darsi UO - AP427( 11-MAY-2022 )"},
    {"name":"Dharamavaram unit office","code":"AP602","value":"602","full_text":"Dharamavaram unit office - AP602( 04-DEC-2024 )"},
    {"name":"Dhone MVI Office","code":"AP421","value":"421","full_text":"Dhone MVI Office - AP421( 06-MAY-2022 )"},
    {"name":"Gajuwaka RTA","code":"AP231","value":"231","full_text":"Gajuwaka RTA - AP231( 06-MAY-2022 )"},
    {"name":"Gudiwada RTA","code":"AP116","value":"116","full_text":"Gudiwada RTA - AP116( 05-MAY-2022 )"},
    {"name":"Gudur RTA","code":"AP226","value":"226","full_text":"Gudur RTA - AP226( 06-MAY-2022 )"},
    {"name":"Guntakal UO","code":"AP202","value":"202","full_text":"Guntakal UO - AP202( 06-MAY-2022 )"},
    {"name":"Guntur RTA","code":"AP7","value":"7","full_text":"Guntur RTA - AP7( 25-APR-2022 )"},
    {"name":"Hindupur RTA","code":"AP102","value":"102","full_text":"Hindupur RTA - AP102( 25-APR-2022 )"},
    {"name":"Itchapuram MVI Office","code":"AP130","value":"130","full_text":"Itchapuram MVI Office - AP130( 12-MAY-2022 )"},
    {"name":"Jaggayyapet UO","code":"AP616","value":"616","full_text":"Jaggayyapet UO - AP616( 05-MAY-2022 )"},
    {"name":"JANGAREDDYGUDEM RTA","code":"AP237","value":"237","full_text":"JANGAREDDYGUDEM RTA - AP237( 06-MAY-2022 )"},
    {"name":"Kalyandurg RTO office","code":"AP702","value":"702","full_text":"Kalyandurg RTO office - AP702( 04-DEC-2024 )"},
    {"name":"Kandukur MVI Office","code":"AP227","value":"227","full_text":"Kandukur MVI Office - AP227( 11-MAY-2022 )"},
    {"name":"Kavali UO","code":"AP326","value":"326","full_text":"Kavali UO - AP326( 11-MAY-2022 )"},
    {"name":"Kovvuru UO","code":"AP337","value":"337","full_text":"Kovvuru UO - AP337( 12-MAY-2022 )"},
    {"name":"Kurnool RTA","code":"AP21","value":"21","full_text":"Kurnool RTA - AP21( 25-APR-2022 )"},
    {"name":"Macherla MVI Office","code":"AP407","value":"407","full_text":"Macherla MVI Office - AP407( 06-MAY-2022 )"},
    {"name":"Mandapeta UO","code":"AP405","value":"405","full_text":"Mandapeta UO - AP405( 06-MAY-2022 )"},
    {"name":"Mangalagiri MVI Office","code":"AP507","value":"507","full_text":"Mangalagiri MVI Office - AP507( 06-MAY-2022 )"},
    {"name":"Markapur UO","code":"AP327","value":"327","full_text":"Markapur UO - AP327( 12-MAY-2022 )"},
    {"name":"Nagari MVI office","code":"AP114","value":"114","full_text":"Nagari MVI office - AP114( 30-NOV-2024 )"},
    {"name":"Nandigama RTA","code":"AP316","value":"316","full_text":"Nandigama RTA - AP316( 05-MAY-2022 )"},
    {"name":"Nandyal RTA","code":"AP121","value":"121","full_text":"Nandyal RTA - AP121( 25-APR-2022 )"},
    {"name":"Narasaraopet RTA","code":"AP107","value":"107","full_text":"Narasaraopet RTA - AP107( 25-APR-2022 )"},
    {"name":"Narsipatnam MVI Office","code":"AP331","value":"331","full_text":"Narsipatnam MVI Office - AP331( 06-MAY-2022 )"},
    {"name":"Nellore RTA","code":"AP26","value":"26","full_text":"Nellore RTA - AP26( 25-APR-2022 )"},
    {"name":"Nuzvid UO","code":"AP416","value":"416","full_text":"Nuzvid UO - AP416( 06-MAY-2022 )"},
    {"name":"Paderu RTA","code":"AP41","value":"41","full_text":"Paderu RTA - AP41( 09-JUN-2022 )"},
    {"name":"Palakole UO","code":"AP637","value":"637","full_text":"Palakole UO - AP637( 06-MAY-2022 )"},
    {"name":"PALAKONDA RTA","code":"AP230","value":"230","full_text":"PALAKONDA RTA - AP230( 12-MAY-2022 )"},
    {"name":"Palamaner MVI Office","code":"AP303","value":"303","full_text":"Palamaner MVI Office - AP303( 10-MAY-2022 )"},
    {"name":"Palasa MVI Office","code":"AP330","value":"330","full_text":"Palasa MVI Office - AP330( 12-MAY-2022 )"},
    {"name":"PARVATHIPURAM RTO OFFICE","code":"AP135","value":"135","full_text":"PARVATHIPURAM RTO OFFICE - AP135( 25-APR-2022 )"},
    {"name":"Peddapuram MVI Office","code":"AP505","value":"505","full_text":"Peddapuram MVI Office - AP505( 06-MAY-2022 )"},
    {"name":"Piduguralla UO","code":"AP607","value":"607","full_text":"Piduguralla UO - AP607( 06-MAY-2022 )"},
    {"name":"Piler MVI Office","code":"AP403","value":"403","full_text":"Piler MVI Office - AP403( 12-MAY-2022 )"},
    {"name":"Prakasam RTA","code":"AP27","value":"27","full_text":"Prakasam RTA - AP27( 25-APR-2022 )"},
    {"name":"Proddutur RTA","code":"AP204","value":"204","full_text":"Proddutur RTA - AP204( 06-MAY-2022 )"},
    {"name":"Pulivendula MVI Office","code":"AP304","value":"304","full_text":"Pulivendula MVI Office - AP304( 06-MAY-2022 )"},
    {"name":"Punganur UO","code":"AP113","value":"113","full_text":"Punganur UO - AP113( 09-JUN-2022 )"},
    {"name":"Puttur MVI Office","code":"AP503","value":"503","full_text":"Puttur MVI Office - AP503( 12-MAY-2022 )"},
    {"name":"Rajahmundry RTA","code":"AP105","value":"105","full_text":"Rajahmundry RTA - AP105( 25-APR-2022 )"},
    {"name":"Rajampet MVI Office","code":"AP404","value":"404","full_text":"Rajampet MVI Office - AP404( 12-MAY-2022 )"},
    {"name":"Ramachandrapuram UO","code":"AP605","value":"605","full_text":"Ramachandrapuram UO - AP605( 09-JUN-2022 )"},
    {"name":"Ravulapalem UO","code":"AP705","value":"705","full_text":"Ravulapalem UO - AP705( 06-MAY-2022 )"},
    {"name":"Rayachoti MVI Office","code":"AP504","value":"504","full_text":"Rayachoti MVI Office - AP504( 25-APR-2022 )"},
    {"name":"REGIONAL TRANSPORT OFFICE RAMPACHODAVARAM","code":"AP141","value":"141","full_text":"REGIONAL TRANSPORT OFFICE RAMPACHODAVARAM - AP141( 04-APR-2023 )"},
    {"name":"RTA Eluru","code":"AP37","value":"37","full_text":"RTA Eluru - AP37( 25-APR-2022 )"},
    {"name":"RTA Kakinada","code":"AP5","value":"5","full_text":"RTA Kakinada - AP5( 25-APR-2022 )"},
    {"name":"RTA MACHILIPATNAM","code":"AP216","value":"216","full_text":"RTA MACHILIPATNAM - AP216( 25-APR-2022 )"},
    {"name":"RTO KADIRI","code":"AP302","value":"302","full_text":"RTO KADIRI - AP302( 11-MAY-2022 )"},
    {"name":"RTO MADANAPALLE","code":"AP203","value":"203","full_text":"RTO MADANAPALLE - AP203( 12-MAY-2022 )"},
    {"name":"Salur MVI Office","code":"AP235","value":"235","full_text":"Salur MVI Office - AP235( 12-MAY-2022 )"},
    {"name":"Srikakulam RTA","code":"AP30","value":"30","full_text":"Srikakulam RTA - AP30( 25-APR-2022 )"},
    {"name":"Srikalahasthi MVI Office","code":"AP603","value":"603","full_text":"Srikalahasthi MVI Office - AP603( 12-MAY-2022 )"},
    {"name":"Sullurpet UO","code":"AP426","value":"426","full_text":"Sullurpet UO - AP426( 11-MAY-2022 )"},
    {"name":"Tadepalli Gudem UO","code":"AP437","value":"437","full_text":"Tadepalli Gudem UO - AP437( 06-MAY-2022 )"},
    {"name":"Tadipatri UO","code":"AP402","value":"402","full_text":"Tadipatri UO - AP402( 06-MAY-2022 )"},
    {"name":"Tanuku UO","code":"AP537","value":"537","full_text":"Tanuku UO - AP537( 06-MAY-2022 )"},
    {"name":"Tekkali MVI Office","code":"AP430","value":"430","full_text":"Tekkali MVI Office - AP430( 12-MAY-2022 )"},
    {"name":"TENALI RTA","code":"AP707","value":"707","full_text":"TENALI RTA - AP707( 06-MAY-2022 )"},
    {"name":"Tirupati RTA","code":"AP103","value":"103","full_text":"Tirupati RTA - AP103( 25-APR-2022 )"},
    {"name":"UNIT OFFICE KATHIPUDI","code":"AP305","value":"305","full_text":"UNIT OFFICE KATHIPUDI - AP305( 06-MAY-2022 )"},
    {"name":"UNIT OFFICE RAYADURG","code":"AP502","value":"502","full_text":"UNIT OFFICE RAYADURG - AP502( 23-JUN-2022 )"},
    {"name":"Vijayawada RTA","code":"AP16","value":"16","full_text":"Vijayawada RTA - AP16( 17-FEB-2022 )"},
    {"name":"Vishakapatnam RTA","code":"AP31","value":"31","full_text":"Vishakapatnam RTA - AP31( 25-APR-2022 )"},
    {"name":"Vizianagaram RTA","code":"AP35","value":"35","full_text":"Vizianagaram RTA - AP35( 25-APR-2022 )"},
    {"name":"Vuyyuru UO","code":"AP516","value":"516","full_text":"Vuyyuru UO - AP516( 05-MAY-2022 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Arunachal Pradesh
# ──────────────────────────────────────────────────────────────────────────────
STATE_AR = {
  "state": "Arunachal Pradesh",
  "state_code": "AR",
  "extraction_date": "2025-07-29T13:38:04.448764",
  "total_rtos": 30,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(29/29)"},
    {"name":"ANJAW","code":"AR17","value":"17","full_text":"ANJAW - AR17( 23-JUL-2021 )"},
    {"name":"Bichom","code":"AR28","value":"28","full_text":"Bichom - AR28( 23-DEC-2024 )"},
    {"name":"CHANGLANG","code":"AR12","value":"12","full_text":"CHANGLANG - AR12( 11-DEC-2019 )"},
    {"name":"DIBANG VALLEY","code":"AR10","value":"10","full_text":"DIBANG VALLEY - AR10( 06-JUL-2023 )"},
    {"name":"EAST KAMENG","code":"AR5","value":"5","full_text":"EAST KAMENG - AR5( 06-OCT-2020 )"},
    {"name":"EAST SIANG","code":"AR9","value":"9","full_text":"EAST SIANG - AR9( 21-JUN-2018 )"},
    {"name":"ITANAGAR CAPITAL REGION","code":"AR1","value":"1","full_text":"ITANAGAR CAPITAL REGION - AR1( 09-OCT-2017 )"},
    {"name":"KAMLE","code":"AR23","value":"23","full_text":"KAMLE - AR23( 08-FEB-2021 )"},
    {"name":"Keyi Panyor","code":"AR27","value":"27","full_text":"Keyi Panyor - AR27( 23-DEC-2024 )"},
    {"name":"KRA-DAADI","code":"AR19","value":"19","full_text":"KRA-DAADI - AR19( 05-SEP-2022 )"},
    {"name":"KURUNG KUMEY","code":"AR15","value":"15","full_text":"KURUNG KUMEY - AR15( 10-AUG-2020 )"},
    {"name":"LEPARADA","code":"AR25","value":"25","full_text":"LEPARADA - AR25( 07-SEP-2022 )"},
    {"name":"LOHIT","code":"AR11","value":"11","full_text":"LOHIT - AR11( 16-JUL-2018 )"},
    {"name":"LONGDING","code":"AR18","value":"18","full_text":"LONGDING - AR18( 24-MAY-2021 )"},
    {"name":"LOWER DIBANG VALLEY","code":"AR16","value":"16","full_text":"LOWER DIBANG VALLEY - AR16( 30-JUL-2018 )"},
    {"name":"LOWER SIANG","code":"AR22","value":"22","full_text":"LOWER SIANG - AR22( 29-AUG-2022 )"},
    {"name":"LOWER SUBANSIRI","code":"AR6","value":"6","full_text":"LOWER SUBANSIRI - AR6( 05-FEB-2019 )"},
    {"name":"NAMSAI","code":"AR20","value":"20","full_text":"NAMSAI - AR20( 26-JUL-2019 )"},
    {"name":"PAKKE-KESANG","code":"AR24","value":"24","full_text":"PAKKE-KESANG - AR24( 15-FEB-2023 )"},
    {"name":"SHI-YOMI","code":"AR26","value":"26","full_text":"SHI-YOMI - AR26( 18-JUL-2019 )"},
    {"name":"SIANG","code":"AR21","value":"21","full_text":"SIANG - AR21( 21-MAR-2022 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"AR99","value":"99","full_text":"STATE TRANSPORT AUTHORITY - AR99( 27-APR-2021 )"},
    {"name":"TAWANG","code":"AR3","value":"3","full_text":"TAWANG - AR3( 25-JUL-2018 )"},
    {"name":"TIRAP","code":"AR13","value":"13","full_text":"TIRAP - AR13( 15-OCT-2018 )"},
    {"name":"UPPER SIANG","code":"AR14","value":"14","full_text":"UPPER SIANG - AR14( 06-FEB-2019 )"},
    {"name":"UPPER SUBANSIRI","code":"AR7","value":"7","full_text":"UPPER SUBANSIRI - AR7( 30-JUL-2019 )"},
    {"name":"WEST KAMENG","code":"AR4","value":"4","full_text":"WEST KAMENG - AR4( 21-JUN-2018 )"},
    {"name":"WEST SIANG","code":"AR8","value":"8","full_text":"WEST SIANG - AR8( 29-OCT-2018 )"},
    {"name":"YUPIA","code":"AR2","value":"2","full_text":"YUPIA - AR2( 22-JAN-2020 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Tamil Nadu — Python seeder
# ──────────────────────────────────────────────────────────────────────────────

STATE_TN = {
  "state": "Tamil Nadu",
  "state_code": "TN",
  "extraction_date": "2025-07-29T14:40:10.387336",
  "total_rtos": 149,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(148/148)"},
    {"name":"ALANGUDI UO","code":"TN641","value":"641","full_text":"ALANGUDI UO - TN641( 04-JUN-2018 )"},
    {"name":"ALANGULAM UO","code":"TN644","value":"644","full_text":"ALANGULAM UO - TN644( 05-MAR-2024 )"},
    {"name":"AMBASAMUTHIRAM UO","code":"TN611","value":"611","full_text":"AMBASAMUTHIRAM UO - TN611( 28-AUG-2018 )"},
    {"name":"AMBATTUR RTO","code":"TN612","value":"612","full_text":"AMBATTUR RTO - TN612( 07-JUN-2018 )"},
    {"name":"AMBUR UO","code":"TN628","value":"628","full_text":"AMBUR UO - TN628( 11-JUL-2018 )"},
    {"name":"ARAKKONAM UO","code":"TN609","value":"609","full_text":"ARAKKONAM UO - TN609( 06-JUL-2018 )"},
    {"name":"ARANI RTO","code":"TN516","value":"516","full_text":"ARANI RTO - TN516( 21-MAY-2018 )"},
    {"name":"ARANTHANGI UO","code":"TN592","value":"592","full_text":"ARANTHANGI UO - TN592( 19-DEC-2017 )"},
    {"name":"ARAVAKURICHI UO","code":"TN632","value":"632","full_text":"ARAVAKURICHI UO - TN632( 27-JUN-2018 )"},
    {"name":"ARIYALUR RTO","code":"TN61","value":"61","full_text":"ARIYALUR RTO - TN61( 14-AUG-2018 )"},
    {"name":"ARUPPUKOTTAI UO","code":"TN622","value":"622","full_text":"ARUPPUKOTTAI UO - TN622( 25-JUL-2018 )"},
    {"name":"ATTUR RTO","code":"TN591","value":"591","full_text":"ATTUR RTO - TN591( 08-JAN-2018 )"},
    {"name":"AVINASHI UO","code":"TN580","value":"580","full_text":"AVINASHI UO - TN580( 14-AUG-2018 )"},
    {"name":"BATLAGUNDU UO","code":"TN596","value":"596","full_text":"BATLAGUNDU UO - TN596( 20-JUL-2018 )"},
    {"name":"BHAVANI UO","code":"TN578","value":"578","full_text":"BHAVANI UO - TN578( 30-JUL-2018 )"},
    {"name":"CHENGALPATTU RTO","code":"TN19","value":"19","full_text":"CHENGALPATTU RTO - TN19( 07-JUN-2018 )"},
    {"name":"CHENNAI (CENTRAL) RTO","code":"TN1","value":"1","full_text":"CHENNAI (CENTRAL) RTO - TN1( 12-JUN-2018 )"},
    {"name":"CHENNAI (EAST) RTO","code":"TN4","value":"4","full_text":"CHENNAI (EAST) RTO - TN4( 03-JUL-2018 )"},
    {"name":"CHENNAI (NORTH-EAST) RTO","code":"TN3","value":"3","full_text":"CHENNAI (NORTH-EAST) RTO - TN3( 03-JUL-2018 )"},
    {"name":"CHENNAI (NORTH) RTO","code":"TN5","value":"5","full_text":"CHENNAI (NORTH) RTO - TN5( 01-JUL-2018 )"},
    {"name":"CHENNAI (SOUTH-EAST) RTO","code":"TN6","value":"6","full_text":"CHENNAI (SOUTH-EAST) RTO - TN6( 11-JUN-2018 )"},
    {"name":"CHENNAI (SOUTH) RTO","code":"TN7","value":"7","full_text":"CHENNAI (SOUTH) RTO - TN7( 01-JUN-2018 )"},
    {"name":"CHENNAI (SOUTH-WEST) RTO","code":"TN10","value":"10","full_text":"CHENNAI (SOUTH-WEST) RTO - TN10( 03-JUL-2018 )"},
    {"name":"CHENNAI (WEST) RTO","code":"TN9","value":"9","full_text":"CHENNAI (WEST) RTO - TN9( 28-MAY-2018 )"},
    {"name":"CHEYYAR UO","code":"TN635","value":"635","full_text":"CHEYYAR UO - TN635( 07-APR-2017 )"},
    {"name":"CHIDAMBARAM RTO","code":"TN544","value":"544","full_text":"CHIDAMBARAM RTO - TN544( 19-JUN-2018 )"},
    {"name":"COIMBATORE (CENTRAL) RTO","code":"TN66","value":"66","full_text":"COIMBATORE (CENTRAL) RTO - TN66( 17-JUL-2018 )"},
    {"name":"COIMBATORE (NORTH) RTO","code":"TN38","value":"38","full_text":"COIMBATORE (NORTH) RTO - TN38( 17-JUL-2018 )"},
    {"name":"COIMBATORE (SOUTH) RTO","code":"TN37","value":"37","full_text":"COIMBATORE (SOUTH) RTO - TN37( 28-MAY-2018 )"},
    {"name":"COIMBATORE (WEST) RTO","code":"TN99","value":"99","full_text":"COIMBATORE (WEST) RTO - TN99( 17-JUL-2018 )"},
    {"name":"CUDDALORE RTO","code":"TN31","value":"31","full_text":"CUDDALORE RTO - TN31( 15-JUN-2018 )"},
    {"name":"DHARAPURAM RTO","code":"TN594","value":"594","full_text":"DHARAPURAM RTO - TN594( 18-JUL-2018 )"},
    {"name":"DHARMAPURI RTO","code":"TN29","value":"29","full_text":"DHARMAPURI RTO - TN29( 03-AUG-2018 )"},
    {"name":"DINDIGUL RTO","code":"TN57","value":"57","full_text":"DINDIGUL RTO - TN57( 19-JUN-2018 )"},
    {"name":"ERODE RTO","code":"TN33","value":"33","full_text":"ERODE RTO - TN33( 14-AUG-2018 )"},
    {"name":"ERODE (WEST) RTO","code":"TN86","value":"86","full_text":"ERODE (WEST) RTO - TN86( 10-AUG-2018 )"},
    {"name":"GINGEE UO","code":"TN627","value":"627","full_text":"GINGEE UO - TN627( 14-JUN-2018 )"},
    {"name":"GOPICHETTIPALAYAM RTO","code":"TN36","value":"36","full_text":"GOPICHETTIPALAYAM RTO - TN36( 30-JUL-2018 )"},
    {"name":"GUDALORE UO","code":"TN582","value":"582","full_text":"GUDALORE UO - TN582( 18-JUL-2018 )"},
    {"name":"GUDIYATHAM UO","code":"TN514","value":"514","full_text":"GUDIYATHAM UO - TN514( 06-JUL-2018 )"},
    {"name":"GUMMIDIPOONDI UO","code":"TN625","value":"625","full_text":"GUMMIDIPOONDI UO - TN625( 07-JUN-2018 )"},
    {"name":"HARUR UO","code":"TN527","value":"527","full_text":"HARUR UO - TN527( 03-AUG-2018 )"},
    {"name":"HOSUR RTO","code":"TN70","value":"70","full_text":"HOSUR RTO - TN70( 06-JUL-2018 )"},
    {"name":"ILLUPPUR UO","code":"TN629","value":"629","full_text":"ILLUPPUR UO - TN629( 24-MAY-2018 )"},
    {"name":"KALLAKURICHI RTO","code":"TN615","value":"615","full_text":"KALLAKURICHI RTO - TN615( 15-JUN-2018 )"},
    {"name":"KANCHEEPURAM RTO","code":"TN21","value":"21","full_text":"KANCHEEPURAM RTO - TN21( 05-JUL-2018 )"},
    {"name":"KANGEYAM UO","code":"TN593","value":"593","full_text":"KANGEYAM UO - TN593( 17-AUG-2018 )"},
    {"name":"KARAIKUDI UO","code":"TN602","value":"602","full_text":"KARAIKUDI UO - TN602( 21-AUG-2018 )"},
    {"name":"KARUR RTO","code":"TN47","value":"47","full_text":"KARUR RTO - TN47( 27-JUN-2018 )"},
    {"name":"KOVILPATTI RTO","code":"TN607","value":"607","full_text":"KOVILPATTI RTO - TN607( 24-AUG-2018 )"},
    {"name":"KRISHNAGIRI RTO","code":"TN24","value":"24","full_text":"KRISHNAGIRI RTO - TN24( 06-JUL-2018 )"},
    {"name":"KULITHALI UO","code":"TN585","value":"585","full_text":"KULITHALI UO - TN585( 27-JUN-2018 )"},
    {"name":"KUMARAPALAYAM RTO","code":"TN638","value":"638","full_text":"KUMARAPALAYAM RTO - TN638( 28-JAN-2018 )"},
    {"name":"KUMBAKONAM RTO","code":"TN68","value":"68","full_text":"KUMBAKONAM RTO - TN68( 06-AUG-2018 )"},
    {"name":"KUNDRATHUR RTO","code":"TN85","value":"85","full_text":"KUNDRATHUR RTO - TN85( 19-JUN-2018 )"},
    {"name":"LALKUDI UO","code":"TN631","value":"631","full_text":"LALKUDI UO - TN631( 28-JUN-2018 )"},
    {"name":"MADURAI (CENTRAL) RTO","code":"TN64","value":"64","full_text":"MADURAI (CENTRAL) RTO - TN64( 17-AUG-2018 )"},
    {"name":"MADURAI (NORTH) RTO","code":"TN59","value":"59","full_text":"MADURAI (NORTH) RTO - TN59( 01-JUN-2018 )"},
    {"name":"MADURAI (SOUTH) RTO","code":"TN58","value":"58","full_text":"MADURAI (SOUTH) RTO - TN58( 06-JUL-2018 )"},
    {"name":"MADURANTAGAM UO","code":"TN508","value":"508","full_text":"MADURANTAGAM UO - TN508( 07-JUN-2018 )"},
    {"name":"MANAPARAI UO","code":"TN584","value":"584","full_text":"MANAPARAI UO - TN584( 30-MAY-2018 )"},
    {"name":"MANMANGALAM UO","code":"TN637","value":"637","full_text":"MANMANGALAM UO - TN637( 25-JUN-2018 )"},
    {"name":"MANNARGUDI UO","code":"TN588","value":"588","full_text":"MANNARGUDI UO - TN588( 09-AUG-2018 )"},
    {"name":"MARTHANDAM RTO","code":"TN75","value":"75","full_text":"MARTHANDAM RTO - TN75( 31-JUL-2018 )"},
    {"name":"MAYILADUTHURAI RTO","code":"TN589","value":"589","full_text":"MAYILADUTHURAI RTO - TN589( 07-AUG-2018 )"},
    {"name":"MEENAMBAKKAM RTO","code":"TN22","value":"22","full_text":"MEENAMBAKKAM RTO - TN22( 09-JUL-2018 )"},
    {"name":"MELUR UO","code":"TN600","value":"600","full_text":"MELUR UO - TN600( 01-JUN-2018 )"},
    {"name":"METTUPALAYAM RTO","code":"TN40","value":"40","full_text":"METTUPALAYAM RTO - TN40( 18-JUL-2018 )"},
    {"name":"METTUR RTO","code":"TN590","value":"590","full_text":"METTUR RTO - TN590( 30-AUG-2018 )"},
    {"name":"MUSURI UO","code":"TN621","value":"621","full_text":"MUSURI UO - TN621( 28-JUN-2018 )"},
    {"name":"NAGAPATTINAM RTO","code":"TN51","value":"51","full_text":"NAGAPATTINAM RTO - TN51( 07-AUG-2018 )"},
    {"name":"NAGERCOIL RTO","code":"TN74","value":"74","full_text":"NAGERCOIL RTO - TN74( 28-AUG-2018 )"},
    {"name":"NAMAKKAL (NORTH) RTO","code":"TN28","value":"28","full_text":"NAMAKKAL (NORTH) RTO - TN28( 30-AUG-2018 )"},
    {"name":"NAMAKKAL (SOUTH) RTO","code":"TN88","value":"88","full_text":"NAMAKKAL (SOUTH) RTO - TN88( 30-AUG-2018 )"},
    {"name":"NATHAM UO","code":"TN640","value":"640","full_text":"NATHAM UO - TN640( 04-JUN-2018 )"},
    {"name":"NEYVELI UO","code":"TN562","value":"562","full_text":"NEYVELI UO - TN562( 20-JUN-2018 )"},
    {"name":"ODDANCHATRAM  UO","code":"TN595","value":"595","full_text":"ODDANCHATRAM  UO - TN595( 24-JUL-2018 )"},
    {"name":"OMALURE UO","code":"TN535","value":"535","full_text":"OMALURE UO - TN535( 29-AUG-2018 )"},
    {"name":"OOTY RTO","code":"TN43","value":"43","full_text":"OOTY RTO - TN43( 18-JUL-2018 )"},
    {"name":"PALACODE UO","code":"TN616","value":"616","full_text":"PALACODE UO - TN616( 03-AUG-2018 )"},
    {"name":"PALANI RTO","code":"TN597","value":"597","full_text":"PALANI RTO - TN597( 24-JUL-2018 )"},
    {"name":"PANRUTI UO","code":"TN626","value":"626","full_text":"PANRUTI UO - TN626( 19-JUN-2018 )"},
    {"name":"PARAMAKUDI UO","code":"TN603","value":"603","full_text":"PARAMAKUDI UO - TN603( 24-JUL-2018 )"},
    {"name":"PARAMATHI VELLURE UO","code":"TN517","value":"517","full_text":"PARAMATHI VELLURE UO - TN517( 30-AUG-2018 )"},
    {"name":"PATTUKOTTAI UNIT OFFICE","code":"TN587","value":"587","full_text":"PATTUKOTTAI UNIT OFFICE - TN587( 06-AUG-2018 )"},
    {"name":"PERAMBALUR RTO","code":"TN46","value":"46","full_text":"PERAMBALUR RTO - TN46( 14-AUG-2018 )"},
    {"name":"PERUNDURAI RTO","code":"TN56","value":"56","full_text":"PERUNDURAI RTO - TN56( 14-AUG-2018 )"},
    {"name":"POLLACHI RTO","code":"TN41","value":"41","full_text":"POLLACHI RTO - TN41( 23-JUL-2018 )"},
    {"name":"POONAMALLEE RTO","code":"TN511","value":"511","full_text":"POONAMALLEE RTO - TN511( 11-JUN-2018 )"},
    {"name":"PUDUKOTTAI RTO","code":"TN55","value":"55","full_text":"PUDUKOTTAI RTO - TN55( 28-DEC-2017 )"},
    {"name":"RAJAPALAYAM UO","code":"TN643","value":"643","full_text":"RAJAPALAYAM UO - TN643( 15-NOV-2023 )"},
    {"name":"RAMANATHAPURAM RTO","code":"TN65","value":"65","full_text":"RAMANATHAPURAM RTO - TN65( 21-AUG-2018 )"},
    {"name":"RANIPET RTO","code":"TN73","value":"73","full_text":"RANIPET RTO - TN73( 06-JUL-2018 )"},
    {"name":"RASIPURAM UO","code":"TN526","value":"526","full_text":"RASIPURAM UO - TN526( 30-AUG-2018 )"},
    {"name":"REDHILLS RTO","code":"TN18","value":"18","full_text":"REDHILLS RTO - TN18( 07-JUN-2018 )"},
    {"name":"RTO CHENNAI (NORTH WEST)","code":"TN2","value":"2","full_text":"RTO CHENNAI (NORTH WEST) - TN2( 25-JUN-2018 )"},
    {"name":"SALEM (EAST) RTO","code":"TN54","value":"54","full_text":"SALEM (EAST) RTO - TN54( 29-AUG-2018 )"},
    {"name":"SALEM (SOUTH) RTO","code":"TN90","value":"90","full_text":"SALEM (SOUTH) RTO - TN90( 29-AUG-2018 )"},
    {"name":"SALEM (WEST) RTO","code":"TN30","value":"30","full_text":"SALEM (WEST) RTO - TN30( 29-AUG-2018 )"},
    {"name":"SANKAGIRI RTO","code":"TN52","value":"52","full_text":"SANKAGIRI RTO - TN52( 30-AUG-2018 )"},
    {"name":"SANKARANKOVIL RTO","code":"TN610","value":"610","full_text":"SANKARANKOVIL RTO - TN610( 28-AUG-2018 )"},
    {"name":"SATHYAMANGALAM UO","code":"TN579","value":"579","full_text":"SATHYAMANGALAM UO - TN579( 30-JUL-2018 )"},
    {"name":"SHOLINGANALLUR RTO","code":"TN512","value":"512","full_text":"SHOLINGANALLUR RTO - TN512( 19-JUN-2018 )"},
    {"name":"SIRKALI UO","code":"TN623","value":"623","full_text":"SIRKALI UO - TN623( 07-AUG-2018 )"},
    {"name":"SIVAGANGAI RTO","code":"TN63","value":"63","full_text":"SIVAGANGAI RTO - TN63( 21-AUG-2018 )"},
    {"name":"SIVAKASI RTO","code":"TN604","value":"604","full_text":"SIVAKASI RTO - TN604( 21-AUG-2018 )"},
    {"name":"SRIPERUMBUDUR RTO","code":"TN614","value":"614","full_text":"SRIPERUMBUDUR RTO - TN614( 01-AUG-2018 )"},
    {"name":"SRIRANGAM RTO","code":"TN48","value":"48","full_text":"SRIRANGAM RTO - TN48( 28-JUN-2018 )"},
    {"name":"SRIVILLIPUTHUR RTO","code":"TN605","value":"605","full_text":"SRIVILLIPUTHUR RTO - TN605( 17-AUG-2018 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"TN999","value":"999","full_text":"STATE TRANSPORT AUTHORITY - TN999( 13-JUN-2018 )"},
    {"name":"SULUR UO","code":"TN620","value":"620","full_text":"SULUR UO - TN620( 28-MAY-2018 )"},
    {"name":"TAMBARAM RTO","code":"TN513","value":"513","full_text":"TAMBARAM RTO - TN513( 25-JUN-2018 )"},
    {"name":"TENKASI RTO","code":"TN76","value":"76","full_text":"TENKASI RTO - TN76( 25-JUL-2018 )"},
    {"name":"THANJAVUR RTO","code":"TN49","value":"49","full_text":"THANJAVUR RTO - TN49( 06-AUG-2018 )"},
    {"name":"THENI RTO","code":"TN60","value":"60","full_text":"THENI RTO - TN60( 20-JUL-2018 )"},
    {"name":"THIRUCHENDUR RTO","code":"TN606","value":"606","full_text":"THIRUCHENDUR RTO - TN606( 28-AUG-2018 )"},
    {"name":"THIRUKALUKUNTRAM UO","code":"TN639","value":"639","full_text":"THIRUKALUKUNTRAM UO - TN639( 04-JUN-2018 )"},
    {"name":"THIRUMANGALAM  UO","code":"TN598","value":"598","full_text":"THIRUMANGALAM  UO - TN598( 07-JUL-2018 )"},
    {"name":"THIRUPATTUR RTO","code":"TN624","value":"624","full_text":"THIRUPATTUR RTO - TN624( 11-JUL-2018 )"},
    {"name":"THIRUTHURAIPOONDI UO","code":"TN630","value":"630","full_text":"THIRUTHURAIPOONDI UO - TN630( 09-AUG-2018 )"},
    {"name":"THIRUTTANI UO","code":"TN634","value":"634","full_text":"THIRUTTANI UO - TN634( 11-JUN-2018 )"},
    {"name":"THOOTHUKUDI RTO","code":"TN69","value":"69","full_text":"THOOTHUKUDI RTO - TN69( 24-AUG-2018 )"},
    {"name":"THURAIYUR UO","code":"TN586","value":"586","full_text":"THURAIYUR UO - TN586( 28-JUN-2018 )"},
    {"name":"TINDIVANAM RTO","code":"TN571","value":"571","full_text":"TINDIVANAM RTO - TN571( 14-JUN-2018 )"},
    {"name":"TIRUCHENGODE RTO","code":"TN34","value":"34","full_text":"TIRUCHENGODE RTO - TN34( 15-MAR-2018 )"},
    {"name":"TIRUCHI(EAST) RTO","code":"TN81","value":"81","full_text":"TIRUCHI(EAST) RTO - TN81( 06-JUL-2018 )"},
    {"name":"TIRUCHI RTO","code":"TN45","value":"45","full_text":"TIRUCHI RTO - TN45( 30-MAY-2018 )"},
    {"name":"TIRUNELVELI RTO","code":"TN72","value":"72","full_text":"TIRUNELVELI RTO - TN72( 25-JUL-2018 )"},
    {"name":"TIRUPPUR (NORTH) RTO","code":"TN39","value":"39","full_text":"TIRUPPUR (NORTH) RTO - TN39( 25-JUL-2018 )"},
    {"name":"TIRUPPUR (SOUTH) RTO","code":"TN42","value":"42","full_text":"TIRUPPUR (SOUTH) RTO - TN42( 25-JUL-2018 )"},
    {"name":"TIRUVALLUR RTO","code":"TN20","value":"20","full_text":"TIRUVALLUR RTO - TN20( 11-JUN-2018 )"},
    {"name":"TIRUVANNAMALAI RTO","code":"TN25","value":"25","full_text":"TIRUVANNAMALAI RTO - TN25( 21-MAY-2018 )"},
    {"name":"TIRUVARUR RTO","code":"TN50","value":"50","full_text":"TIRUVARUR RTO - TN50( 09-AUG-2018 )"},
    {"name":"TIRUVERANBUR UO","code":"TN583","value":"583","full_text":"TIRUVERANBUR UO - TN583( 09-JUL-2018 )"},
    {"name":"UDUMALPET RTO","code":"TN581","value":"581","full_text":"UDUMALPET RTO - TN581( 17-AUG-2018 )"},
    {"name":"ULUNDURPET RTO","code":"TN577","value":"577","full_text":"ULUNDURPET RTO - TN577( 15-JUN-2018 )"},
    {"name":"USILAMPATTI UO","code":"TN636","value":"636","full_text":"USILAMPATTI UO - TN636( 14-AUG-2018 )"},
    {"name":"UTHAMAPALAYAM UO","code":"TN601","value":"601","full_text":"UTHAMAPALAYAM UO - TN601( 20-JUL-2018 )"},
    {"name":"VADIPATTI UO","code":"TN599","value":"599","full_text":"VADIPATTI UO - TN599( 05-JUN-2018 )"},
    {"name":"VALAPPADI UO","code":"TN613","value":"613","full_text":"VALAPPADI UO - TN613( 08-JAN-2018 )"},
    {"name":"VALLIYUR UO","code":"TN608","value":"608","full_text":"VALLIYUR UO - TN608( 25-JUL-2018 )"},
    {"name":"VALPARAI UO","code":"TN633","value":"633","full_text":"VALPARAI UO - TN633( 24-JUL-2018 )"},
    {"name":"VANIYAMBADI RTO","code":"TN515","value":"515","full_text":"VANIYAMBADI RTO - TN515( 11-JUL-2018 )"},
    {"name":"VEDACHANDUR UO","code":"TN617","value":"617","full_text":"VEDACHANDUR UO - TN617( 20-JUL-2018 )"},
    {"name":"VELLORE RTO","code":"TN23","value":"23","full_text":"VELLORE RTO - TN23( 05-JUL-2018 )"},
    {"name":"VILUPPURAM RTO","code":"TN32","value":"32","full_text":"VILUPPURAM RTO - TN32( 14-JUN-2018 )"},
    {"name":"VIRUDHACHALAM UO","code":"TN553","value":"553","full_text":"VIRUDHACHALAM UO - TN553( 19-JUN-2018 )"},
    {"name":"VIRUDHUNAGAR RTO","code":"TN67","value":"67","full_text":"VIRUDHUNAGAR RTO - TN67( 25-JUL-2018 )"},
  ]
}

# Quick sanity check for duplicate codes
_codes = [rt["code"] for rt in STATE_TN["rtos"]]
assert len(_codes) == len(set(_codes)), "Duplicate RTO codes detected in TN payload"

# ──────────────────────────────────────────────────────────────────────────────
# Lakshadweep
# ──────────────────────────────────────────────────────────────────────────────
STATE_LD = {
  "state": "Lakshadweep",
  "state_code": "LD",
  "extraction_date": "2025-07-29T14:12:32.423115",
  "total_rtos": 7,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(6/9)"},
    {"name":"AMINI","code":"LD3","value":"3","full_text":"AMINI - LD3( 23-DEC-2024 )"},
    {"name":"ANDROTH","code":"LD4","value":"4","full_text":"ANDROTH - LD4( 06-NOV-2024 )"},
    {"name":"CHETLAT","code":"LD5","value":"5","full_text":"CHETLAT - LD5( 06-FEB-2025 )"},
    {"name":"KALPENI","code":"LD7","value":"7","full_text":"KALPENI - LD7( 09-MAY-2025 )"},
    {"name":"KAVARATTI","code":"LD1","value":"1","full_text":"KAVARATTI - LD1( 13-JUN-2024 )"},
    {"name":"MINICOY","code":"LD9","value":"9","full_text":"MINICOY - LD9( 06-NOV-2024 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Uttar Pradesh
# ──────────────────────────────────────────────────────────────────────────────
STATE_UP = {
  "state": "Uttar Pradesh",
  "state_code": "UP",
  "extraction_date": "2025-07-29T14:46:02.075715",
  "total_rtos": 79,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(77/77)"},
    {"name":"Agra RTO","code":"UP80","value":"80","full_text":"Agra RTO - UP80( 23-NOV-2017 )"},
    {"name":"AKBARPUR(AMBEDKAR NAGAR)","code":"UP45","value":"45","full_text":"AKBARPUR(AMBEDKAR NAGAR) - UP45( 27-DEC-2017 )"},
    {"name":"ALIGARH RTO","code":"UP81","value":"81","full_text":"ALIGARH RTO - UP81( 20-DEC-2017 )"},
    {"name":"Amethi ARTO","code":"UP36","value":"36","full_text":"Amethi ARTO - UP36( 28-DEC-2017 )"},
    {"name":"ARTO OFFICE RAMPUR","code":"UP22","value":"22","full_text":"ARTO OFFICE RAMPUR - UP22( 12-FEB-2018 )"},
    {"name":"AURAIYA","code":"UP79","value":"79","full_text":"AURAIYA - UP79( 12-OCT-2017 )"},
    {"name":"AYODHYA RTO","code":"UP42","value":"42","full_text":"AYODHYA RTO - UP42( 26-DEC-2017 )"},
    {"name":"Azamgarh RTO","code":"UP50","value":"50","full_text":"Azamgarh RTO - UP50( 26-FEB-2018 )"},
    {"name":"Badaun","code":"UP24","value":"24","full_text":"Badaun - UP24( 12-FEB-2018 )"},
    {"name":"Baghpat","code":"UP17","value":"17","full_text":"Baghpat - UP17( 14-NOV-2017 )"},
    {"name":"Bahraich","code":"UP40","value":"40","full_text":"Bahraich - UP40( 11-DEC-2017 )"},
    {"name":"Ballia","code":"UP60","value":"60","full_text":"Ballia - UP60( 15-JAN-2018 )"},
    {"name":"Balrampur","code":"UP47","value":"47","full_text":"Balrampur - UP47( 11-DEC-2017 )"},
    {"name":"BANDARTO","code":"UP90","value":"90","full_text":"BANDARTO - UP90( 22-FEB-2018 )"},
    {"name":"Barabanki ARTO","code":"UP41","value":"41","full_text":"Barabanki ARTO - UP41( 12-JAN-2016 )"},
    {"name":"BAREILLY","code":"UP25","value":"25","full_text":"BAREILLY - UP25( 13-FEB-2018 )"},
    {"name":"BASTI RTO","code":"UP51","value":"51","full_text":"BASTI RTO - UP51( 13-DEC-2017 )"},
    {"name":"Bhadohi(SANT RAVIDAS NAGAR)","code":"UP66","value":"66","full_text":"Bhadohi(SANT RAVIDAS NAGAR) - UP66( 25-OCT-2017 )"},
    {"name":"Bijnor","code":"UP20","value":"20","full_text":"Bijnor - UP20( 13-FEB-2018 )"},
    {"name":"Bulandshahar","code":"UP13","value":"13","full_text":"Bulandshahar - UP13( 22-JAN-2018 )"},
    {"name":"Chandauli","code":"UP67","value":"67","full_text":"Chandauli - UP67( 17-JAN-2018 )"},
    {"name":"Chitrakoot","code":"UP96","value":"96","full_text":"Chitrakoot - UP96( 22-FEB-2018 )"},
    {"name":"DEORIA","code":"UP52","value":"52","full_text":"DEORIA - UP52( 23-JAN-2018 )"},
    {"name":"Etah","code":"UP82","value":"82","full_text":"Etah - UP82( 27-NOV-2017 )"},
    {"name":"Etawah","code":"UP75","value":"75","full_text":"Etawah - UP75( 11-OCT-2017 )"},
    {"name":"Farrukhabad","code":"UP76","value":"76","full_text":"Farrukhabad - UP76( 29-JAN-2018 )"},
    {"name":"FATHEHPUR","code":"UP71","value":"71","full_text":"FATHEHPUR - UP71( 24-JAN-2018 )"},
    {"name":"FEROZABAD","code":"UP83","value":"83","full_text":"FEROZABAD - UP83( 25-OCT-2017 )"},
    {"name":"GHAZIABAD","code":"UP14","value":"14","full_text":"GHAZIABAD - UP14( 23-JAN-2018 )"},
    {"name":"Ghazipur","code":"UP61","value":"61","full_text":"Ghazipur - UP61( 29-JAN-2018 )"},
    {"name":"GONDA","code":"UP43","value":"43","full_text":"GONDA - UP43( 14-DEC-2017 )"},
    {"name":"Gorakhpur RTO","code":"UP53","value":"53","full_text":"Gorakhpur RTO - UP53( 08-NOV-2017 )"},
    {"name":"HAMIRPUR(UP)","code":"UP91","value":"91","full_text":"HAMIRPUR(UP) - UP91( 24-FEB-2018 )"},
    {"name":"Hapur","code":"UP37","value":"37","full_text":"Hapur - UP37( 23-JAN-2018 )"},
    {"name":"HARDOI","code":"UP30","value":"30","full_text":"HARDOI - UP30( 11-SEP-2017 )"},
    {"name":"HATHRAS","code":"UP86","value":"86","full_text":"HATHRAS - UP86( 18-DEC-2017 )"},
    {"name":"JAUNPUR","code":"UP62","value":"62","full_text":"JAUNPUR - UP62( 18-JAN-2018 )"},
    {"name":"JhansiRTO","code":"UP93","value":"93","full_text":"JhansiRTO - UP93( 19-DEC-2017 )"},
    {"name":"JPNAGAR","code":"UP23","value":"23","full_text":"JPNAGAR - UP23( 17-NOV-2017 )"},
    {"name":"Kannauj","code":"UP74","value":"74","full_text":"Kannauj - UP74( 13-FEB-2018 )"},
    {"name":"Kanpur Dehat","code":"UP77","value":"77","full_text":"Kanpur Dehat - UP77( 11-DEC-2017 )"},
    {"name":"KANPUR NAGAR","code":"UP78","value":"78","full_text":"KANPUR NAGAR - UP78( 05-DEC-2016 )"},
    {"name":"Kasganj(kashi ram nagar)","code":"UP87","value":"87","full_text":"Kasganj(kashi ram nagar) - UP87( 29-NOV-2017 )"},
    {"name":"Kaushambi","code":"UP73","value":"73","full_text":"Kaushambi - UP73( 11-OCT-2017 )"},
    {"name":"LAKHIMPUR KHERI","code":"UP31","value":"31","full_text":"LAKHIMPUR KHERI - UP31( 29-JAN-2018 )"},
    {"name":"Lalitpur","code":"UP94","value":"94","full_text":"Lalitpur - UP94( 26-OCT-2017 )"},
    {"name":"MAHANAGAR ARTO LUCKNOW (","code":"UP321","value":"321","full_text":"MAHANAGAR ARTO LUCKNOW (UP321) - UP321( 22-NOV-2017 )"},
    {"name":"Maharajganj","code":"UP56","value":"56","full_text":"Maharajganj - UP56( 18-SEP-2017 )"},
    {"name":"Mahoba","code":"UP95","value":"95","full_text":"Mahoba - UP95( 23-FEB-2018 )"},
    {"name":"Mainpuri","code":"UP84","value":"84","full_text":"Mainpuri - UP84( 20-FEB-2018 )"},
    {"name":"MATHURA","code":"UP85","value":"85","full_text":"MATHURA - UP85( 22-FEB-2018 )"},
    {"name":"Mau","code":"UP54","value":"54","full_text":"Mau - UP54( 23-JAN-2018 )"},
    {"name":"MEERUT RTO","code":"UP15","value":"15","full_text":"MEERUT RTO - UP15( 15-JAN-2018 )"},
    {"name":"MIRZAPUR RTO","code":"UP63","value":"63","full_text":"MIRZAPUR RTO - UP63( 20-DEC-2017 )"},
    {"name":"MORADABAD","code":"UP21","value":"21","full_text":"MORADABAD - UP21( 17-NOV-2017 )"},
    {"name":"M/S Sai Dham Super Srv Soln Pvt Ltd Ghaziabad","code":"UP214","value":"214","full_text":"M/S Sai Dham Super Srv Soln Pvt Ltd Ghaziabad - UP214( 20-JAN-2021 )"},
    {"name":"MuzaffarNagar","code":"UP12","value":"12","full_text":"MuzaffarNagar - UP12( 19-FEB-2018 )"},
    {"name":"Noida","code":"UP16","value":"16","full_text":"Noida - UP16( 13-NOV-2017 )"},
    {"name":"Orai","code":"UP92","value":"92","full_text":"Orai - UP92( 18-DEC-2017 )"},
    {"name":"PADRAUNA(KUSHI NAGAR)","code":"UP57","value":"57","full_text":"PADRAUNA(KUSHI NAGAR) - UP57( 08-NOV-2017 )"},
    {"name":"Pilibhit","code":"UP26","value":"26","full_text":"Pilibhit - UP26( 12-FEB-2018 )"},
    {"name":"PRATAPGARH","code":"UP72","value":"72","full_text":"PRATAPGARH - UP72( 09-FEB-2018 )"},
    {"name":"Prayagraj RTO","code":"UP70","value":"70","full_text":"Prayagraj RTO - UP70( 29-JAN-2018 )"},
    {"name":"Raibareilly","code":"UP33","value":"33","full_text":"Raibareilly - UP33( 23-AUG-2017 )"},
    {"name":"SAHARANPUR RTO","code":"UP11","value":"11","full_text":"SAHARANPUR RTO - UP11( 18-JAN-2018 )"},
    {"name":"SAHJAHANPUR","code":"UP27","value":"27","full_text":"SAHJAHANPUR - UP27( 15-FEB-2018 )"},
    {"name":"Sambhal ARTO","code":"UP38","value":"38","full_text":"Sambhal ARTO - UP38( 30-NOV-2017 )"},
    {"name":"Sant Kabir Nagar","code":"UP58","value":"58","full_text":"Sant Kabir Nagar - UP58( 12-DEC-2017 )"},
    {"name":"SHAMLI ARTO","code":"UP19","value":"19","full_text":"SHAMLI ARTO - UP19( 08-FEB-2018 )"},
    {"name":"Shravasti","code":"UP46","value":"46","full_text":"Shravasti - UP46( 14-DEC-2017 )"},
    {"name":"Siddharth Nagar(naugarh)","code":"UP55","value":"55","full_text":"Siddharth Nagar(naugarh) - UP55( 19-SEP-2017 )"},
    {"name":"Sitapur","code":"UP34","value":"34","full_text":"Sitapur - UP34( 18-DEC-2017 )"},
    {"name":"SONBHADRA","code":"UP64","value":"64","full_text":"SONBHADRA - UP64( 18-DEC-2017 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"UP999","value":"999","full_text":"STATE TRANSPORT AUTHORITY - UP999( 20-FEB-2019 )"},
    {"name":"Sultanpur","code":"UP44","value":"44","full_text":"Sultanpur - UP44( 11-OCT-2017 )"},
    {"name":"TRANSPORT NAGAR RTO LUCKNOW (","code":"UP32","value":"32","full_text":"TRANSPORT NAGAR RTO LUCKNOW (UP32) - UP32( 19-JUL-2016 )"},
    {"name":"Unnao","code":"UP35","value":"35","full_text":"Unnao - UP35( 12-SEP-2017 )"},
    {"name":"VARANASI RTO","code":"UP65","value":"65","full_text":"VARANASI RTO - UP65( 17-JAN-2018 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Jammu & Kashmir
# ──────────────────────────────────────────────────────────────────────────────
STATE_JK = {
  "state": "Jammu and Kashmir",
  "state_code": "JK",
  "extraction_date": "2025-07-29T14:04:16.414015",
  "total_rtos": 22,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(21/21)"},
    {"name":"ANANTNAG ARTO","code":"JK3","value":"3","full_text":"ANANTNAG ARTO - JK3( 24-OCT-2016 )"},
    {"name":"BANDIPORA ARTO","code":"JK15","value":"15","full_text":"BANDIPORA ARTO - JK15( 29-FEB-2016 )"},
    {"name":"BARAMULLA ARTO","code":"JK5","value":"5","full_text":"BARAMULLA ARTO - JK5( 07-DEC-2016 )"},
    {"name":"BUDGAM ARTO","code":"JK4","value":"4","full_text":"BUDGAM ARTO - JK4( 16-MAY-2016 )"},
    {"name":"DODA ARTO","code":"JK6","value":"6","full_text":"DODA ARTO - JK6( 05-SEP-2016 )"},
    {"name":"GANDERBAL ARTO","code":"JK16","value":"16","full_text":"GANDERBAL ARTO - JK16( 18-MAY-2016 )"},
    {"name":"JAMMU RTO","code":"JK2","value":"2","full_text":"JAMMU RTO - JK2( 01-DEC-2016 )"},
    {"name":"KATHUA RTO","code":"JK8","value":"8","full_text":"KATHUA RTO - JK8( 22-SEP-2016 )"},
    {"name":"KISHTWAR ARTO","code":"JK17","value":"17","full_text":"KISHTWAR ARTO - JK17( 18-NOV-2016 )"},
    {"name":"KULGAM ARTO","code":"JK18","value":"18","full_text":"KULGAM ARTO - JK18( 21-APR-2016 )"},
    {"name":"KUPWARA ARTO","code":"JK9","value":"9","full_text":"KUPWARA ARTO - JK9( 25-NOV-2016 )"},
    {"name":"POONCH ARTO","code":"JK12","value":"12","full_text":"POONCH ARTO - JK12( 08-FEB-2017 )"},
    {"name":"PULWAMA ARTO","code":"JK13","value":"13","full_text":"PULWAMA ARTO - JK13( 29-FEB-2016 )"},
    {"name":"RAJOURI ARTO","code":"JK11","value":"11","full_text":"RAJOURI ARTO - JK11( 09-DEC-2016 )"},
    {"name":"RAMBAN ARTO","code":"JK19","value":"19","full_text":"RAMBAN ARTO - JK19( 07-APR-2016 )"},
    {"name":"REASI ARTO","code":"JK20","value":"20","full_text":"REASI ARTO - JK20( 29-FEB-2016 )"},
    {"name":"SAMBA ARTO","code":"JK21","value":"21","full_text":"SAMBA ARTO - JK21( 29-FEB-2016 )"},
    {"name":"SHOPIAN ARTO","code":"JK22","value":"22","full_text":"SHOPIAN ARTO - JK22( 08-NOV-2016 )"},
    {"name":"SRINAGAR RTO","code":"JK1","value":"1","full_text":"SRINAGAR RTO - JK1( 12-NOV-2016 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"JK999","value":"999","full_text":"STATE TRANSPORT AUTHORITY - JK999( 04-MAY-2021 )"},
    {"name":"UDHAMPUR ARTO","code":"JK14","value":"14","full_text":"UDHAMPUR ARTO - JK14( 12-SEP-2016 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Punjab
# ──────────────────────────────────────────────────────────────────────────────
STATE_PB = {
  "state": "Punjab",
  "state_code": "PB",
  "extraction_date": "2025-07-29T14:28:05.709334",
  "total_rtos": 97,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(96/96)"},
    {"name":"PUNJAB STA(RAC)/(AITP)","code":"PB1","value":"1","full_text":"PUNJAB STA(RAC)/(AITP) - PB1( 16-FEB-2018 )"},
    {"name":"RTO AMRITSAR","code":"PB2","value":"2","full_text":"RTO AMRITSAR - PB2( 02-NOV-2017 )"},
    {"name":"RTO BARNALA","code":"PB19","value":"19","full_text":"RTO BARNALA - PB19( 02-JAN-2018 )"},
    {"name":"RTO BATHINDA","code":"PB3","value":"3","full_text":"RTO BATHINDA - PB3( 25-OCT-2017 )"},
    {"name":"RTO FARIDKOT","code":"PB4","value":"4","full_text":"RTO FARIDKOT - PB4( 25-OCT-2017 )"},
    {"name":"RTO FATEHGARH SAHIB","code":"PB23","value":"23","full_text":"RTO FATEHGARH SAHIB - PB23( 11-OCT-2017 )"},
    {"name":"RTO FAZILKA","code":"PB22","value":"22","full_text":"RTO FAZILKA - PB22( 10-NOV-2017 )"},
    {"name":"RTO FEROZPUR","code":"PB5","value":"5","full_text":"RTO FEROZPUR - PB5( 25-OCT-2017 )"},
    {"name":"RTO GURDASPUR","code":"PB6","value":"6","full_text":"RTO GURDASPUR - PB6( 27-OCT-2017 )"},
    {"name":"RTO HOSHIARPUR","code":"PB7","value":"7","full_text":"RTO HOSHIARPUR - PB7( 01-NOV-2017 )"},
    {"name":"RTO JALANDHAR","code":"PB8","value":"8","full_text":"RTO JALANDHAR - PB8( 30-OCT-2017 )"},
    {"name":"RTO KAPURTHALA","code":"PB9","value":"9","full_text":"RTO KAPURTHALA - PB9( 01-NOV-2017 )"},
    {"name":"RTO LUDHIANA","code":"PB10","value":"10","full_text":"RTO LUDHIANA - PB10( 25-JAN-2018 )"},
    {"name":"RTO MALERKOTLA","code":"PB28","value":"28","full_text":"RTO MALERKOTLA - PB28( 01-NOV-2017 )"},
    {"name":"RTO MANSA","code":"PB31","value":"31","full_text":"RTO MANSA - PB31( 24-OCT-2017 )"},
    {"name":"RTO MOGA","code":"PB29","value":"29","full_text":"RTO MOGA - PB29( 18-OCT-2017 )"},
    {"name":"RTO MUKTSAR SAHIB","code":"PB30","value":"30","full_text":"RTO MUKTSAR SAHIB - PB30( 27-FEB-2018 )"},
    {"name":"RTO PATHANKOT","code":"PB35","value":"35","full_text":"RTO PATHANKOT - PB35( 01-NOV-2017 )"},
    {"name":"RTO PATIALA","code":"PB11","value":"11","full_text":"RTO PATIALA - PB11( 22-DEC-2017 )"},
    {"name":"RTO ROPAR","code":"PB12","value":"12","full_text":"RTO ROPAR - PB12( 31-OCT-2017 )"},
    {"name":"RTO SAHIBZADA AJIT SINGH NAGAR","code":"PB65","value":"65","full_text":"RTO SAHIBZADA AJIT SINGH NAGAR - PB65( 24-OCT-2017 )"},
    {"name":"RTO SANGRUR","code":"PB13","value":"13","full_text":"RTO SANGRUR - PB13( 13-NOV-2017 )"},
    {"name":"RTO SBS NAGAR","code":"PB32","value":"32","full_text":"RTO SBS NAGAR - PB32( 28-OCT-2017 )"},
    {"name":"RTO TARN TARAN","code":"PB46","value":"46","full_text":"RTO TARN TARAN - PB46( 26-OCT-2017 )"},
    {"name":"SDM ABOHAR","code":"PB15","value":"15","full_text":"SDM ABOHAR - PB15( 26-OCT-2017 )"},
    {"name":"SDM ADAMPUR","code":"PB94","value":"94","full_text":"SDM ADAMPUR - PB94( 26-OCT-2023 )"},
    {"name":"SDM AHMEDGARH","code":"PB82","value":"82","full_text":"SDM AHMEDGARH - PB82( 01-NOV-2017 )"},
    {"name":"SDM AJNALA","code":"PB14","value":"14","full_text":"SDM AJNALA - PB14( 02-NOV-2017 )"},
    {"name":"SDM AMARGARH","code":"PB92","value":"92","full_text":"SDM AMARGARH - PB92( 22-OCT-2021 )"},
    {"name":"SDM AMLOH","code":"PB48","value":"48","full_text":"SDM AMLOH - PB48( 04-OCT-2017 )"},
    {"name":"SDM AMRITSAR-2","code":"PB89","value":"89","full_text":"SDM AMRITSAR-2 - PB89( 02-NOV-2017 )"},
    {"name":"SDM ANANDPUR SAHIB","code":"PB16","value":"16","full_text":"SDM ANANDPUR SAHIB - PB16( 30-OCT-2017 )"},
    {"name":"SDM BABA BAKALA","code":"PB17","value":"17","full_text":"SDM BABA BAKALA - PB17( 02-NOV-2017 )"},
    {"name":"SDM BAGHA PURANA","code":"PB69","value":"69","full_text":"SDM BAGHA PURANA - PB69( 18-OCT-2017 )"},
    {"name":"SDM BALACHAUR","code":"PB20","value":"20","full_text":"SDM BALACHAUR - PB20( 01-NOV-2017 )"},
    {"name":"SDM BANGA","code":"PB78","value":"78","full_text":"SDM BANGA - PB78( 01-NOV-2017 )"},
    {"name":"SDM BASSI PATHANA","code":"PB52","value":"52","full_text":"SDM BASSI PATHANA - PB52( 28-SEP-2017 )"},
    {"name":"SDM BATALA","code":"PB18","value":"18","full_text":"SDM BATALA - PB18( 27-OCT-2017 )"},
    {"name":"SDM BHAWNIGARH","code":"PB84","value":"84","full_text":"SDM BHAWNIGARH - PB84( 25-OCT-2017 )"},
    {"name":"SDM BHIKHIWIND","code":"PB88","value":"88","full_text":"SDM BHIKHIWIND - PB88( 26-OCT-2017 )"},
    {"name":"SDM BHOLATH","code":"PB57","value":"57","full_text":"SDM BHOLATH - PB57( 01-NOV-2017 )"},
    {"name":"SDM BUDHLADA","code":"PB50","value":"50","full_text":"SDM BUDHLADA - PB50( 26-OCT-2017 )"},
    {"name":"SDM CHAMKAUR SAHIB","code":"PB71","value":"71","full_text":"SDM CHAMKAUR SAHIB - PB71( 26-OCT-2017 )"},
    {"name":"SDM DASUYA","code":"PB21","value":"21","full_text":"SDM DASUYA - PB21( 01-NOV-2017 )"},
    {"name":"SDM DERA BABA NANAK","code":"PB58","value":"58","full_text":"SDM DERA BABA NANAK - PB58( 27-OCT-2017 )"},
    {"name":"SDM DERA BASSI","code":"PB70","value":"70","full_text":"SDM DERA BASSI - PB70( 17-OCT-2017 )"},
    {"name":"SDM DHARAMKOT","code":"PB76","value":"76","full_text":"SDM DHARAMKOT - PB76( 18-OCT-2017 )"},
    {"name":"SDM DHAR KALAN","code":"PB68","value":"68","full_text":"SDM DHAR KALAN - PB68( 01-NOV-2017 )"},
    {"name":"SDM DHURI","code":"PB59","value":"59","full_text":"SDM DHURI - PB59( 27-OCT-2017 )"},
    {"name":"SDM DINANAGAR","code":"PB99","value":"99","full_text":"SDM DINANAGAR - PB99( 25-MAR-2019 )"},
    {"name":"SDM DIRBA","code":"PB86","value":"86","full_text":"SDM DIRBA - PB86( 01-NOV-2017 )"},
    {"name":"SDM DUDHAN SADHAN","code":"PB83","value":"83","full_text":"SDM DUDHAN SADHAN - PB83( 26-OCT-2017 )"},
    {"name":"SDM GARSHANKAR","code":"PB24","value":"24","full_text":"SDM GARSHANKAR - PB24( 27-OCT-2017 )"},
    {"name":"SDM GIDDARBAHA","code":"PB60","value":"60","full_text":"SDM GIDDARBAHA - PB60( 13-OCT-2017 )"},
    {"name":"SDM GURU HAR SAHAI","code":"PB77","value":"77","full_text":"SDM GURU HAR SAHAI - PB77( 24-OCT-2017 )"},
    {"name":"SDM JAGRAON","code":"PB25","value":"25","full_text":"SDM JAGRAON - PB25( 03-NOV-2017 )"},
    {"name":"SDM JAITO","code":"PB62","value":"62","full_text":"SDM JAITO - PB62( 24-OCT-2017 )"},
    {"name":"SDM JALALABAD","code":"PB61","value":"61","full_text":"SDM JALALABAD - PB61( 26-OCT-2017 )"},
    {"name":"SDM JALANDHAR-11","code":"PB90","value":"90","full_text":"SDM JALANDHAR-11 - PB90( 27-OCT-2017 )"},
    {"name":"SDM KALANAUR","code":"PB85","value":"85","full_text":"SDM KALANAUR - PB85( 27-OCT-2017 )"},
    {"name":"SDM KHADUR SAHIB","code":"PB63","value":"63","full_text":"SDM KHADUR SAHIB - PB63( 26-OCT-2017 )"},
    {"name":"SDM KHAMANO","code":"PB49","value":"49","full_text":"SDM KHAMANO - PB49( 26-SEP-2017 )"},
    {"name":"SDM KHANNA","code":"PB26","value":"26","full_text":"SDM KHANNA - PB26( 01-NOV-2017 )"},
    {"name":"SDM KHARAR","code":"PB27","value":"27","full_text":"SDM KHARAR - PB27( 23-OCT-2017 )"},
    {"name":"SDM KOTKAPURA","code":"PB79","value":"79","full_text":"SDM KOTKAPURA - PB79( 25-OCT-2017 )"},
    {"name":"SDM LEHRAGAGA","code":"PB75","value":"75","full_text":"SDM LEHRAGAGA - PB75( 27-OCT-2017 )"},
    {"name":"SDM LOPOKE","code":"PB93","value":"93","full_text":"SDM LOPOKE - PB93( 26-OCT-2023 )"},
    {"name":"SDM LUDHIANA EAST","code":"PB91","value":"91","full_text":"SDM LUDHIANA EAST - PB91( 29-DEC-2017 )"},
    {"name":"SDM MAJITHA","code":"PB81","value":"81","full_text":"SDM MAJITHA - PB81( 28-OCT-2017 )"},
    {"name":"SDM MALOUT","code":"PB53","value":"53","full_text":"SDM MALOUT - PB53( 17-OCT-2017 )"},
    {"name":"SDM MAUR MANDI","code":"PB80","value":"80","full_text":"SDM MAUR MANDI - PB80( 25-OCT-2017 )"},
    {"name":"SDM MOONAK","code":"PB64","value":"64","full_text":"SDM MOONAK - PB64( 27-OCT-2017 )"},
    {"name":"SDM MORINDA","code":"PB87","value":"87","full_text":"SDM MORINDA - PB87( 27-OCT-2017 )"},
    {"name":"SDM MUKERIAN","code":"PB54","value":"54","full_text":"SDM MUKERIAN - PB54( 27-OCT-2017 )"},
    {"name":"SDM NABHA","code":"PB34","value":"34","full_text":"SDM NABHA - PB34( 13-OCT-2017 )"},
    {"name":"SDM NAKODAR","code":"PB33","value":"33","full_text":"SDM NAKODAR - PB33( 31-OCT-2017 )"},
    {"name":"SDM NANGAL","code":"PB74","value":"74","full_text":"SDM NANGAL - PB74( 26-OCT-2017 )"},
    {"name":"SDM NIHAL SINGH WALA","code":"PB66","value":"66","full_text":"SDM NIHAL SINGH WALA  - PB66( 18-OCT-2017 )"},
    {"name":"SDM PATRAN","code":"PB72","value":"72","full_text":"SDM PATRAN - PB72( 11-OCT-2017 )"},
    {"name":"SDM PATTI","code":"PB38","value":"38","full_text":"SDM PATTI - PB38( 26-OCT-2017 )"},
    {"name":"SDM PAYAL","code":"PB55","value":"55","full_text":"SDM PAYAL - PB55( 03-NOV-2017 )"},
    {"name":"SDM PHAGWARA","code":"PB36","value":"36","full_text":"SDM PHAGWARA - PB36( 01-NOV-2017 )"},
    {"name":"SDM PHILLOUR","code":"PB37","value":"37","full_text":"SDM PHILLOUR - PB37( 28-OCT-2017 )"},
    {"name":"SDM RAIKOT","code":"PB56","value":"56","full_text":"SDM RAIKOT - PB56( 20-NOV-2017 )"},
    {"name":"SDM RAJPURA","code":"PB39","value":"39","full_text":"SDM RAJPURA - PB39( 24-OCT-2017 )"},
    {"name":"SDM RAMPURA PHUL","code":"PB40","value":"40","full_text":"SDM RAMPURA PHUL - PB40( 25-OCT-2017 )"},
    {"name":"SDM SAMANA","code":"PB42","value":"42","full_text":"SDM SAMANA - PB42( 11-OCT-2017 )"},
    {"name":"SDM SAMRALA","code":"PB43","value":"43","full_text":"SDM SAMRALA - PB43( 27-OCT-2017 )"},
    {"name":"SDM SARDULGARH","code":"PB51","value":"51","full_text":"SDM SARDULGARH - PB51( 27-OCT-2017 )"},
    {"name":"SDM SHAHKOT","code":"PB67","value":"67","full_text":"SDM SHAHKOT - PB67( 30-OCT-2017 )"},
    {"name":"SDM SULTANPUR LODHI","code":"PB41","value":"41","full_text":"SDM SULTANPUR LODHI - PB41( 30-OCT-2017 )"},
    {"name":"SDM SUNAM","code":"PB44","value":"44","full_text":"SDM SUNAM - PB44( 26-OCT-2017 )"},
    {"name":"SDM TALWANDI SABO","code":"PB45","value":"45","full_text":"SDM TALWANDI SABO - PB45( 24-OCT-2017 )"},
    {"name":"SDM TANDA","code":"PB95","value":"95","full_text":"SDM TANDA - PB95( 29-AUG-2024 )"},
    {"name":"SDM TAPA","code":"PB73","value":"73","full_text":"SDM TAPA - PB73( 03-NOV-2017 )"},
    {"name":"SDM ZIRA","code":"PB47","value":"47","full_text":"SDM ZIRA - PB47( 26-OCT-2017 )"}
  ]
}


# ──────────────────────────────────────────────────────────────────────────────
# Manipur
# ──────────────────────────────────────────────────────────────────────────────
STATE_MN = {
  "state": "Manipur",
  "state_code": "MN",
  "extraction_date": "2025-07-29T14:17:46.391728",
  "total_rtos": 14,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(13/13)"},
    {"name":"BISHNUPUR","code":"MN5","value":"5","full_text":"BISHNUPUR - MN5( 27-AUG-2018 )"},
    {"name":"Chandel","code":"MN9","value":"9","full_text":"Chandel - MN9( 27-OCT-2021 )"},
    {"name":"CHURACHANDPUR","code":"MN2","value":"2","full_text":"CHURACHANDPUR - MN2( 11-APR-2018 )"},
    {"name":"DTO, KAMJONG","code":"MN12","value":"12","full_text":"DTO, KAMJONG - MN12( 13-FEB-2025 )"},
    {"name":"IMPHAL EAST","code":"MN6","value":"6","full_text":"IMPHAL EAST - MN6( 26-SEP-2018 )"},
    {"name":"IMPHAL WEST","code":"MN1","value":"1","full_text":"IMPHAL WEST - MN1( 09-MAY-2017 )"},
    {"name":"KANGPOKPI","code":"MN3","value":"3","full_text":"KANGPOKPI - MN3( 20-AUG-2018 )"},
    {"name":"SENAPATI","code":"MN8","value":"8","full_text":"SENAPATI - MN8( 11-OCT-2018 )"},
    {"name":"STA MANIPUR","code":"MN99","value":"99","full_text":"STA MANIPUR - MN99( 08-SEP-2020 )"},
    {"name":"Tamenglong","code":"MN10","value":"10","full_text":"Tamenglong - MN10( 27-OCT-2021 )"},
    {"name":"TENGNOUPAL","code":"MN11","value":"11","full_text":"TENGNOUPAL - MN11( 05-MAR-2023 )"},
    {"name":"THOUBAL","code":"MN4","value":"4","full_text":"THOUBAL - MN4( 20-SEP-2018 )"},
    {"name":"UKHRUL","code":"MN7","value":"7","full_text":"UKHRUL - MN7( 08-MAR-2018 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Haryana
# ──────────────────────────────────────────────────────────────────────────────
STATE_HR = {
  "state": "Haryana",
  "state_code": "HR",
  "extraction_date": "2025-07-29T14:00:55.963461",
  "total_rtos": 179,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(98/98)"},
    {"name":"AMBALA CITY","code":"HR1","value":"1","full_text":"AMBALA CITY - HR1( 27-APR-2017 )"},
    {"name":"ASSANDH","code":"HR40","value":"40","full_text":"ASSANDH - HR40( 16-JUN-2017 )"},
    {"name":"BAHADURGARH","code":"HR13","value":"13","full_text":"BAHADURGARH - HR13( 03-MAY-2017 )"},
    {"name":"BALLABGARH","code":"HR29","value":"29","full_text":"BALLABGARH - HR29( 18-JUL-2017 )"},
    {"name":"BARARA","code":"HR54","value":"54","full_text":"BARARA - HR54( 25-APR-2017 )"},
    {"name":"BAWAL","code":"HR81","value":"81","full_text":"BAWAL - HR81( 19-JUL-2017 )"},
    {"name":"BHIWANI","code":"HR16","value":"16","full_text":"BHIWANI - HR16( 30-MAY-2017 )"},
    {"name":"CHARKHI DADRI","code":"HR19","value":"19","full_text":"CHARKHI DADRI - HR19( 05-JUL-2017 )"},
    {"name":"DABWALI","code":"HR25","value":"25","full_text":"DABWALI - HR25( 03-JUL-2017 )"},
    {"name":"ELLNABAD","code":"HR44","value":"44","full_text":"ELLNABAD - HR44( 03-JUL-2017 )"},
    {"name":"FARIDABAD","code":"HR51","value":"51","full_text":"FARIDABAD - HR51( 12-JUN-2017 )"},
    {"name":"FATEHABAD","code":"HR22","value":"22","full_text":"FATEHABAD - HR22( 27-JUN-2017 )"},
    {"name":"FEROZEPUR ZIRKHA","code":"HR28","value":"28","full_text":"FEROZEPUR ZIRKHA - HR28( 01-MAY-2017 )"},
    {"name":"GANAUR","code":"HR42","value":"42","full_text":"GANAUR - HR42( 29-JUN-2017 )"},
    {"name":"GOHANA","code":"HR11","value":"11","full_text":"GOHANA - HR11( 07-JUL-2017 )"},
    {"name":"GULHA","code":"HR9","value":"9","full_text":"GULHA - HR9( 25-JUL-2017 )"},
    {"name":"GURUGRAM SOUTH","code":"HR72","value":"72","full_text":"GURUGRAM SOUTH - HR72( 03-JUL-2017 )"},
    {"name":"HANSI","code":"HR21","value":"21","full_text":"HANSI - HR21( 03-JUL-2017 )"},
    {"name":"HARYANA HEAD OFFICE CHD","code":"HR70","value":"70","full_text":"HARYANA HEAD OFFICE CHD - HR70( 01-JAN-2018 )"},
    {"name":"HATHIN","code":"HR52","value":"52","full_text":"HATHIN - HR52( 21-JUL-2017 )"},
    {"name":"HISAR","code":"HR20","value":"20","full_text":"HISAR - HR20( 18-MAY-2017 )"},
    {"name":"HODEL","code":"HR50","value":"50","full_text":"HODEL - HR50( 19-JUL-2017 )"},
    {"name":"JAGADHARI","code":"HR2","value":"2","full_text":"JAGADHARI - HR2( 06-JUN-2017 )"},
    {"name":"JHAJHAR","code":"HR14","value":"14","full_text":"JHAJHAR - HR14( 25-MAY-2017 )"},
    {"name":"JIND","code":"HR31","value":"31","full_text":"JIND - HR31( 19-MAY-2017 )"},
    {"name":"KAITHAL","code":"HR8","value":"8","full_text":"KAITHAL - HR8( 04-JUL-2017 )"},
    {"name":"KALAYAT","code":"HR83","value":"83","full_text":"KALAYAT - HR83( 27-JUL-2017 )"},
    {"name":"KANINA","code":"HR82","value":"82","full_text":"KANINA - HR82( 12-JUL-2017 )"},
    {"name":"KARNAL","code":"HR5","value":"5","full_text":"KARNAL - HR5( 05-JUN-2017 )"},
    {"name":"KOSLI","code":"HR43","value":"43","full_text":"KOSLI - HR43( 27-JUL-2017 )"},
    {"name":"LADWA","code":"HR97","value":"97","full_text":"LADWA - HR97( 05-APR-2018 )"},
    {"name":"LOHARU","code":"HR18","value":"18","full_text":"LOHARU - HR18( 20-JUL-2017 )"},
    {"name":"MAHENDERGARH","code":"HR34","value":"34","full_text":"MAHENDERGARH - HR34( 29-JUN-2017 )"},
    {"name":"MEHAM","code":"HR15","value":"15","full_text":"MEHAM - HR15( 01-MAY-2017 )"},
    {"name":"M.G. MOTORS, 12KM MILE STONE(F.C)","code":"HR204","value":"204","full_text":"M.G. MOTORS, 12KM MILE STONE(F.C) - HR204( 27-AUG-2021 )"},
    {"name":"M/S ABC MOTORS DHANGARH FATEHABAD(F.C)","code":"HR238","value":"238","full_text":"M/S ABC MOTORS DHANGARH FATEHABAD(F.C) - HR238( 25-OCT-2021 )"},
    {"name":"M/S AMBA MOTORS","code":"HR271","value":"271","full_text":"M/S AMBA MOTORS - HR271( 21-JAN-2022 )"},
    {"name":"M/S COMPETENT AUTOMOBILES COMPANY LTD","code":"HR270","value":"270","full_text":"M/S COMPETENT AUTOMOBILES COMPANY LTD - HR270( 21-JAN-2022 )"},
    {"name":"M/S CSG AUTOMOBILES(F.C)","code":"HR266","value":"266","full_text":"M/S CSG AUTOMOBILES(F.C) - HR266( 03-DEC-2021 )"},
    {"name":"M/S DAISY MOTORS PVT LTD, 12KM STONE(F.C)","code":"HR206","value":"206","full_text":"M/S DAISY MOTORS PVT LTD, 12KM STONE(F.C) - HR206( 27-AUG-2021 )"},
    {"name":"M/S DAISY MOTORS PVT LTD(F.C)","code":"HR261","value":"261","full_text":"M/S DAISY MOTORS PVT LTD(F.C) - HR261( 22-NOV-2021 )"},
    {"name":"M/S DAISY MOTORS PVT LTD(F.C)","code":"HR259","value":"259","full_text":"M/S DAISY MOTORS PVT LTD(F.C) - HR259( 22-NOV-2021 )"},
    {"name":"M/S DAKSH MARKETING(F.C)","code":"HR251","value":"251","full_text":"M/S DAKSH MARKETING(F.C) - HR251( 15-NOV-2021 )"},
    {"name":"M/S DHINGRA TRUCKING PVT LTD","code":"HR268","value":"268","full_text":"M/S DHINGRA TRUCKING PVT LTD - HR268( 21-JAN-2022 )"},
    {"name":"M/S DINCO FOUR WHEELS LLP(F.C)","code":"HR263","value":"263","full_text":"M/S DINCO FOUR WHEELS LLP(F.C) - HR263( 22-NOV-2021 )"},
    {"name":"M/S EAKANSH MOTORS PVT LTD(F.C)","code":"HR247","value":"247","full_text":"M/S EAKANSH MOTORS PVT LTD(F.C) - HR247( 29-OCT-2021 )"},
    {"name":"M/S EAKANSH WHEELS 126KM STONE JAGDHARI ROAD(F.C)","code":"HR236","value":"236","full_text":"M/S EAKANSH WHEELS 126KM STONE JAGDHARI ROAD(F.C) - HR236( 29-SEP-2021 )"},
    {"name":"M/S GARG MOTORS(F.C)","code":"HR253","value":"253","full_text":"M/S GARG MOTORS(F.C) - HR253( 15-NOV-2021 )"},
    {"name":"M/S GLOBAL AUTMOBOLINES SCO 25-26 GROUND FLOOR(F.C)","code":"HR213","value":"213","full_text":"M/S GLOBAL AUTMOBOLINES SCO 25-26 GROUND FLOOR(F.C) - HR213( 22-SEP-2021 )"},
    {"name":"M/S GLOBAL AUTOMART PVT LTD, 82 KM STONE(F.C)","code":"HR203","value":"203","full_text":"M/S GLOBAL AUTOMART PVT LTD, 82 KM STONE(F.C) - HR203( 27-AUG-2021 )"},
    {"name":"M/S G.N.G AUTO AIDS PVT.LTD(F.C)","code":"HR256","value":"256","full_text":"M/S G.N.G AUTO AIDS PVT.LTD(F.C) - HR256( 15-NOV-2021 )"},
    {"name":"M/S HARCHAND MOTORS(F.C)","code":"HR260","value":"260","full_text":"M/S HARCHAND MOTORS(F.C) - HR260( 22-NOV-2021 )"},
    {"name":"M/S HARYANA MOTOR(F.C)","code":"HR276","value":"276","full_text":"M/S HARYANA MOTOR(F.C) - HR276( 22-FEB-2022 )"},
    {"name":"M/S HIMGIRI AUTOMOBILES PVT.LTD(F.C)","code":"HR257","value":"257","full_text":"M/S HIMGIRI AUTOMOBILES PVT.LTD(F.C) - HR257( 15-NOV-2021 )"},
    {"name":"M/S HIND MOTORS(F.C)","code":"HR246","value":"246","full_text":"M/S HIND MOTORS(F.C) - HR246( 29-OCT-2021 )"},
    {"name":"M/S HISAR AUTOMOBILES 5TH KM STONE SIRSA ROAD(F.C)","code":"HR215","value":"215","full_text":"M/S HISAR AUTOMOBILES 5TH KM STONE SIRSA ROAD(F.C) - HR215( 24-SEP-2021 )"},
    {"name":"M/S H.S MOTORS SANOLI ROAD(F.C)","code":"HR212","value":"212","full_text":"M/S H.S MOTORS SANOLI ROAD(F.C) - HR212( 15-SEP-2021 )"},
    {"name":"M/S JAGMOHAN AUTOMOBILES PVT LTD(F.C)","code":"HR218","value":"218","full_text":"M/S JAGMOHAN AUTOMOBILES PVT LTD(F.C) - HR218( 24-SEP-2021 )"},
    {"name":"M/S JOHAR AUTOMOBILES FARIDABAD(F.C)","code":"HR208","value":"208","full_text":"M/S JOHAR AUTOMOBILES FARIDABAD(F.C) - HR208( 27-AUG-2021 )"},
    {"name":"M/S KARAN AUTOMOTIVE(F.C)","code":"HR275","value":"275","full_text":"M/S KARAN AUTOMOTIVE(F.C) - HR275( 17-FEB-2022 )"},
    {"name":"M/S KARNAL MOTORS PVT 71/3 MILE STONE(F.C)","code":"HR210","value":"210","full_text":"M/S KARNAL MOTORS PVT 71/3 MILE STONE(F.C) - HR210( 17-SEP-2021 )"},
    {"name":"M/S KARNAL MOTORS PVT LTD,PLOT NO-156-157(F.C)","code":"HR209","value":"209","full_text":"M/S KARNAL MOTORS PVT LTD,PLOT NO-156-157(F.C) - HR209( 17-SEP-2021 )"},
    {"name":"M/S KBS MOTORS PVT LTD OLD COURT ROAD JAGADHARI(F.C)","code":"HR221","value":"221","full_text":"M/S KBS MOTORS PVT LTD OLD COURT ROAD JAGADHARI(F.C) - HR221( 24-SEP-2021 )"},
    {"name":"M/S KBS MOTORS PVT LTD VILL-TEPLA AMBALA(F.C)","code":"HR216","value":"216","full_text":"M/S KBS MOTORS PVT LTD VILL-TEPLA AMBALA(F.C) - HR216( 27-SEP-2021 )"},
    {"name":"M/S KHANNA CAR PLAZA PVT LTD(F.C)","code":"HR249","value":"249","full_text":"M/S KHANNA CAR PLAZA PVT LTD(F.C) - HR249( 29-OCT-2021 )"},
    {"name":"M/S LEKHRAJ AUTO PLAZA PVT LTD(F.C)","code":"HR250","value":"250","full_text":"M/S LEKHRAJ AUTO PLAZA PVT LTD(F.C) - HR250( 15-NOV-2021 )"},
    {"name":"M/S MAHABALAJI AUTO SERVICE PVT LTD, 1/158, KM STONE(F.C)","code":"HR223","value":"223","full_text":"M/S MAHABALAJI AUTO SERVICE PVT LTD, 1/158, KM STONE(F.C) - HR223( 24-SEP-2021 )"},
    {"name":"M/S MANGALAM MOTORS BAHADURGARH DISTT JHAJJAR(F.C)","code":"HR240","value":"240","full_text":"M/S MANGALAM MOTORS BAHADURGARH DISTT JHAJJAR(F.C) - HR240( 28-SEP-2021 )"},
    {"name":"M/S MANGLA MOTORS(F.C)","code":"HR277","value":"277","full_text":"M/S MANGLA MOTORS(F.C) - HR277( 25-APR-2022 )"},
    {"name":"M/S METRO MOTORS PVT LTD, 106, RAILWAY ROAD(F.C)","code":"HR219","value":"219","full_text":"M/S METRO MOTORS PVT LTD, 106, RAILWAY ROAD(F.C) - HR219( 24-SEP-2021 )"},
    {"name":"M/S METRO MOTORS PVT LTD, 76/1 MILE STONE(F.C)","code":"HR217","value":"217","full_text":"M/S METRO MOTORS PVT LTD, 76/1 MILE STONE(F.C) - HR217( 24-SEP-2021 )"},
    {"name":"M/S M.G. MOTORS","code":"HR269","value":"269","full_text":"M/S M.G. MOTORS - HR269( 21-JAN-2022 )"},
    {"name":"M/S MG MOTORS NEAR TOLL PLAZA NARANGPUR ROHTAK ROAD BHIWANI(F.C)","code":"HR227","value":"227","full_text":"M/S MG MOTORS NEAR TOLL PLAZA NARANGPUR ROHTAK ROAD BHIWANI(F.C) - HR227( 27-SEP-2021 )"},
    {"name":"M/S MOHAN FOURWHEEL PVT LTD, 13 KM STONE(F.C)","code":"HR205","value":"205","full_text":"M/S MOHAN FOURWHEEL PVT LTD, 13 KM STONE(F.C) - HR205( 27-AUG-2021 )"},
    {"name":"M/S M/S SATGURU MOTORS NH-52(F.C)","code":"HR235","value":"235","full_text":"M/S M/S SATGURU MOTORS NH-52(F.C) - HR235( 24-SEP-2021 )"},
    {"name":"M/S PALTINUM MOTOCOPR MANESAR GURUGRAM(F.C)","code":"HR239","value":"239","full_text":"M/S PALTINUM MOTOCOPR MANESAR GURUGRAM(F.C) - HR239( 28-SEP-2021 )"},
    {"name":"M/S PALUCK TECHNOLOGIES PVT.LTD(F.C)","code":"HR258","value":"258","full_text":"M/S PALUCK TECHNOLOGIES PVT.LTD(F.C) - HR258( 15-NOV-2021 )"},
    {"name":"M/S PANDIT AUTOMOBILES PVT LTD GOBINDPURA BYE PASS ROAD JAGADHARI YAMUNANAGAR(F.C)","code":"HR225","value":"225","full_text":"M/S PANDIT AUTOMOBILES PVT LTD GOBINDPURA BYE PASS ROAD JAGADHARI YAMUNANAGAR(F.C) - HR225( 28-SEP-2021 )"},
    {"name":"M/S PARAS TRUCKS, 11KM STONE DELHI BYE PASS ROAD(F.C)","code":"HR211","value":"211","full_text":"M/S PARAS TRUCKS, 11KM STONE DELHI BYE PASS ROAD(F.C) - HR211( 17-SEP-2021 )"},
    {"name":"M/S PASCO AUTOMOBILES","code":"HR214","value":"214","full_text":"M/S PASCO AUTOMOBILES - HR214( 24-SEP-2021 )"},
    {"name":"M/S PASCO AUTOMOBILES","code":"HR233","value":"233","full_text":"M/S PASCO AUTOMOBILES - HR233( 28-SEP-2021 )"},
    {"name":"M/S PASCO AUTOMOBILES","code":"HR232","value":"232","full_text":"M/S PASCO AUTOMOBILES - HR232( 28-SEP-2021 )"},
    {"name":"M/S PASCO AUTOMOBILES 34/3 DINESH JAIN COMPLEX(F.C)","code":"HR230","value":"230","full_text":"M/S PASCO AUTOMOBILES 34/3 DINESH JAIN COMPLEX(F.C) - HR230( 28-SEP-2021 )"},
    {"name":"M/S PASCO AUTOMOBILES, 6 INDUSTRIAL ESTATE PALAM GURUGRAM(F.C)","code":"HR228","value":"228","full_text":"M/S PASCO AUTOMOBILES, 6 INDUSTRIAL ESTATE PALAM GURUGRAM(F.C) - HR228( 28-SEP-2021 )"},
    {"name":"M/S PASCO MOTORS(F.C)","code":"HR252","value":"252","full_text":"M/S PASCO MOTORS(F.C) - HR252( 15-NOV-2021 )"},
    {"name":"M/S PASCO MOTORS LLP 30MILES STONE(F.C)","code":"HR224","value":"224","full_text":"M/S PASCO MOTORS LLP 30MILES STONE(F.C) - HR224( 24-SEP-2021 )"},
    {"name":"M/S PASCO MOTORS LLP, 40 MILE STONE(F.C)","code":"HR207","value":"207","full_text":"M/S PASCO MOTORS LLP, 40 MILE STONE(F.C) - HR207( 27-AUG-2021 )"},
    {"name":"M/S PASCO MOTORS LLP SHOP NO. G35(F.C)","code":"HR202","value":"202","full_text":"M/S PASCO MOTORS LLP SHOP NO. G35(F.C) - HR202( 27-AUG-2021 )"},
    {"name":"M/S PREM MOTORS PVT LTD DIVIDING ROAD(F.C)","code":"HR234","value":"234","full_text":"M/S PREM MOTORS PVT LTD DIVIDING ROAD(F.C) - HR234( 27-SEP-2021 )"},
    {"name":"M/S PREM MOTORS PVT LTD PLOT 3 IDC(F.C)","code":"HR231","value":"231","full_text":"M/S PREM MOTORS PVT LTD PLOT 3 IDC(F.C) - HR231( 28-SEP-2021 )"},
    {"name":"M/S RAMA MOTORS(F.C)","code":"HR279","value":"279","full_text":"M/S RAMA MOTORS(F.C) - HR279( 24-MAY-2022 )"},
    {"name":"M/S RANA MOTORS PVT LTD MEHARAULI ROAD GURUGRAM(F.C)","code":"HR241","value":"241","full_text":"M/S RANA MOTORS PVT LTD MEHARAULI ROAD GURUGRAM(F.C) - HR241( 28-SEP-2021 )"},
    {"name":"M/S R.K.H AUTOMOBILES PVT LTD(F.C)","code":"HR229","value":"229","full_text":"M/S R.K.H AUTOMOBILES PVT LTD(F.C) - HR229( 24-SEP-2021 )"},
    {"name":"M/S RUDRA MOTORS NARWANA DISTT JIND(F.C)","code":"HR243","value":"243","full_text":"M/S RUDRA MOTORS NARWANA DISTT JIND(F.C) - HR243( 28-SEP-2021 )"},
    {"name":"M/S SAHIL MOTORS(F.C)","code":"HR245","value":"245","full_text":"M/S SAHIL MOTORS(F.C) - HR245( 29-OCT-2021 )"},
    {"name":"M/S Sanjay Automotive LLP Old Delhi Road(F.C)","code":"HR280","value":"280","full_text":"M/S Sanjay Automotive LLP Old Delhi Road(F.C) - HR280( 24-MAY-2022 )"},
    {"name":"M/S SHAKTI MOTORS PVT LTD(F.C)","code":"HR254","value":"254","full_text":"M/S SHAKTI MOTORS PVT LTD(F.C) - HR254( 15-NOV-2021 )"},
    {"name":"M/S SHIVA MOTORS(F.C)","code":"HR248","value":"248","full_text":"M/S SHIVA MOTORS(F.C) - HR248( 29-OCT-2021 )"},
    {"name":"M/S SHREE KRISHANA MOTORS(F.C)","code":"HR264","value":"264","full_text":"M/S SHREE KRISHANA MOTORS(F.C) - HR264( 22-NOV-2021 )"},
    {"name":"M/S SHREE MOTORS PVT LTD, DEHCORA ROAD(F.C)","code":"HR201","value":"201","full_text":"M/S SHREE MOTORS PVT LTD, DEHCORA ROAD(F.C) - HR201( 27-AUG-2021 )"},
    {"name":"M/S SHREE SALASAR MOTORS(F.C)","code":"HR255","value":"255","full_text":"M/S SHREE SALASAR MOTORS(F.C) - HR255( 15-NOV-2021 )"},
    {"name":"M/S SISOTHYA AUTOMOBILES DELHI JAIPUR HIGHWAY(F.C)","code":"HR278","value":"278","full_text":"M/S SISOTHYA AUTOMOBILES DELHI JAIPUR HIGHWAY(F.C) - HR278( 25-APR-2022 )"},
    {"name":"M/S STAR AUTOMOBILE(F.C)","code":"HR244","value":"244","full_text":"M/S STAR AUTOMOBILE(F.C) - HR244( 29-OCT-2021 )"},
    {"name":"M/S SUPREME MOBILES PVT LTD(F.C)","code":"HR262","value":"262","full_text":"M/S SUPREME MOBILES PVT LTD(F.C) - HR262( 22-NOV-2021 )"},
    {"name":"M/S SUPREME MOBILES PVT LTD(F.C)","code":"HR267","value":"267","full_text":"M/S SUPREME MOBILES PVT LTD(F.C) - HR267( 14-DEC-2021 )"},
    {"name":"M/S TAYAL MOTORS PVT LTD MATHURA ROAD FARIDABAD(F.C)","code":"HR237","value":"237","full_text":"M/S TAYAL MOTORS PVT LTD MATHURA ROAD FARIDABAD(F.C) - HR237( 28-SEP-2021 )"},
    {"name":"M/S TCS AUTOWORLD","code":"HR273","value":"273","full_text":"M/S TCS AUTOWORLD - HR273( 21-JAN-2022 )"},
    {"name":"M/S THADESHRI Motors(F.C)","code":"HR265","value":"265","full_text":"M/S THADESHRI Motors(F.C) - HR265( 03-DEC-2021 )"},
    {"name":"M/S TIRUPATI MOTORS REWARI-DELHI ROAD VILL-JONAWAS(F.C)","code":"HR220","value":"220","full_text":"M/S TIRUPATI MOTORS REWARI-DELHI ROAD VILL-JONAWAS(F.C) - HR220( 24-SEP-2021 )"},
    {"name":"M/S UNIQUE MOTORS PVT LTD OPP-BHANU INDUSTRIES HISAR(F.C)","code":"HR242","value":"242","full_text":"M/S UNIQUE MOTORS PVT LTD OPP-BHANU INDUSTRIES HISAR(F.C) - HR242( 28-SEP-2021 )"},
    {"name":"M/S UNITED MOTORS MIRZAPUR ROAD NEAR MIRZAPUR CHOWK(F.C)","code":"HR222","value":"222","full_text":"M/S UNITED MOTORS MIRZAPUR ROAD NEAR MIRZAPUR CHOWK(F.C) - HR222( 24-SEP-2021 )"},
    {"name":"M/S VIPIN MOTORS","code":"HR272","value":"272","full_text":"M/S VIPIN MOTORS - HR272( 21-JAN-2022 )"},
    {"name":"M/S VMT MOTORS","code":"HR274","value":"274","full_text":"M/S VMT MOTORS - HR274( 21-JAN-2022 )"},
    {"name":"M/S YASHODHA TRANSWHEELS LLP, 78 MILE STONE VILLAGE KARHANS(F.C)","code":"HR226","value":"226","full_text":"M/S YASHODHA TRANSWHEELS LLP, 78 MILE STONE VILLAGE KARHANS(F.C) - HR226( 27-SEP-2021 )"},
    {"name":"NARAINGARH","code":"HR4","value":"4","full_text":"NARAINGARH - HR4( 15-MAR-2017 )"},
    {"name":"NARNAUL","code":"HR35","value":"35","full_text":"NARNAUL - HR35( 30-JUN-2017 )"},
    {"name":"NARWANA","code":"HR32","value":"32","full_text":"NARWANA - HR32( 20-MAY-2017 )"},
    {"name":"NUH","code":"HR27","value":"27","full_text":"NUH - HR27( 29-MAY-2017 )"},
    {"name":"PALWAL","code":"HR30","value":"30","full_text":"PALWAL - HR30( 17-JUL-2017 )"},
    {"name":"PANCHKULA","code":"HR3","value":"3","full_text":"PANCHKULA - HR3( 22-FEB-2017 )"},
    {"name":"PANIPAT","code":"HR6","value":"6","full_text":"PANIPAT - HR6( 06-JUL-2017 )"},
    {"name":"PATAUDI","code":"HR76","value":"76","full_text":"PATAUDI - HR76( 03-JUL-2017 )"},
    {"name":"PEHOWA","code":"HR41","value":"41","full_text":"PEHOWA - HR41( 04-AUG-2017 )"},
    {"name":"RA(MV),PANCHKULA","code":"HR99","value":"99","full_text":"RA(MV),PANCHKULA - HR99( 15-JAN-2021 )"},
    {"name":"RATIA","code":"HR59","value":"59","full_text":"RATIA - HR59( 28-JUN-2017 )"},
    {"name":"REWARI","code":"HR36","value":"36","full_text":"REWARI - HR36( 13-JUN-2017 )"},
    {"name":"RLA TAURU","code":"HR96","value":"96","full_text":"RLA TAURU - HR96( 20-DEC-2017 )"},
    {"name":"ROHTAK","code":"HR12","value":"12","full_text":"ROHTAK - HR12( 01-MAY-2017 )"},
    {"name":"RTA AMBALA","code":"HR37","value":"37","full_text":"RTA AMBALA - HR37( 01-APR-2017 )"},
    {"name":"RTA, BHIWANI","code":"HR61","value":"61","full_text":"RTA, BHIWANI - HR61( 01-APR-2017 )"},
    {"name":"RTA CHARKI DADRI","code":"HR84","value":"84","full_text":"RTA CHARKI DADRI - HR84( 01-APR-2017 )"},
    {"name":"RTA, FARIDABAD","code":"HR38","value":"38","full_text":"RTA, FARIDABAD - HR38( 01-APR-2017 )"},
    {"name":"RTA, FATEHABAD","code":"HR62","value":"62","full_text":"RTA, FATEHABAD - HR62( 01-APR-2017 )"},
    {"name":"RTA, GURGAON","code":"HR55","value":"55","full_text":"RTA, GURGAON - HR55( 01-APR-2017 )"},
    {"name":"RTA, HISAR","code":"HR39","value":"39","full_text":"RTA, HISAR - HR39( 01-APR-2017 )"},
    {"name":"RTA, JHAJJAR AT BAHADURGARH","code":"HR63","value":"63","full_text":"RTA, JHAJJAR AT BAHADURGARH - HR63( 01-APR-2017 )"},
    {"name":"RTA, JIND","code":"HR56","value":"56","full_text":"RTA, JIND - HR56( 01-APR-2017 )"},
    {"name":"RTA, KAITHAL","code":"HR64","value":"64","full_text":"RTA, KAITHAL - HR64( 01-APR-2017 )"},
    {"name":"RTA, KARNAL","code":"HR45","value":"45","full_text":"RTA, KARNAL - HR45( 01-APR-2017 )"},
    {"name":"RTA, KURUKSHETRA","code":"HR65","value":"65","full_text":"RTA, KURUKSHETRA - HR65( 01-APR-2017 )"},
    {"name":"RTA, MOHINDERGARH","code":"HR66","value":"66","full_text":"RTA, MOHINDERGARH - HR66( 01-APR-2017 )"},
    {"name":"RTA, NUH","code":"HR74","value":"74","full_text":"RTA, NUH - HR74( 01-APR-2017 )"},
    {"name":"RTA, PALWAL","code":"HR73","value":"73","full_text":"RTA, PALWAL - HR73( 01-APR-2017 )"},
    {"name":"RTA, PANCHKULA","code":"HR68","value":"68","full_text":"RTA, PANCHKULA - HR68( 01-APR-2017 )"},
    {"name":"RTA, PANIPAT","code":"HR67","value":"67","full_text":"RTA, PANIPAT - HR67( 01-APR-2017 )"},
    {"name":"RTA, REWARI","code":"HR47","value":"47","full_text":"RTA, REWARI - HR47( 01-APR-2017 )"},
    {"name":"RTA, ROHTAK","code":"HR46","value":"46","full_text":"RTA, ROHTAK - HR46( 01-APR-2017 )"},
    {"name":"RTA, SIRSA","code":"HR57","value":"57","full_text":"RTA, SIRSA - HR57( 01-APR-2017 )"},
    {"name":"RTA, SONEPAT","code":"HR69","value":"69","full_text":"RTA, SONEPAT - HR69( 01-APR-2017 )"},
    {"name":"RTA, YNR","code":"HR58","value":"58","full_text":"RTA, YNR - HR58( 01-APR-2017 )"},
    {"name":"SAFIDON","code":"HR33","value":"33","full_text":"SAFIDON - HR33( 19-MAY-2017 )"},
    {"name":"SAMALKHA","code":"HR60","value":"60","full_text":"SAMALKHA - HR60( 06-JUL-2017 )"},
    {"name":"SDM AMBALA CANTONMENT","code":"HR85","value":"85","full_text":"SDM AMBALA CANTONMENT - HR85( 10-MAR-2017 )"},
    {"name":"SDM BADHRA","code":"HR88","value":"88","full_text":"SDM BADHRA - HR88( 28-AUG-2017 )"},
    {"name":"SDM BADKHAL","code":"HR87","value":"87","full_text":"SDM BADKHAL - HR87( 19-JUN-2017 )"},
    {"name":"SDM BADLI","code":"HR89","value":"89","full_text":"SDM BADLI - HR89( 11-APR-2017 )"},
    {"name":"SDM BADSHAHPUR","code":"HR98","value":"98","full_text":"SDM BADSHAHPUR - HR98( 15-JUL-2020 )"},
    {"name":"SDM BARWALA","code":"HR80","value":"80","full_text":"SDM BARWALA - HR80( 23-JUN-2017 )"},
    {"name":"SDM BERI","code":"HR77","value":"77","full_text":"SDM BERI - HR77( 21-JUN-2017 )"},
    {"name":"SDM BILASPUR","code":"HR71","value":"71","full_text":"SDM BILASPUR - HR71( 18-JUL-2017 )"},
    {"name":"SDM GHARAUNDA","code":"HR91","value":"91","full_text":"SDM GHARAUNDA - HR91( 29-MAY-2017 )"},
    {"name":"SDM GURUGRAM","code":"HR26","value":"26","full_text":"SDM GURUGRAM - HR26( 27-JUN-2017 )"},
    {"name":"SDM INDIRI","code":"HR75","value":"75","full_text":"SDM INDIRI - HR75( 13-JUN-2017 )"},
    {"name":"SDM KALANWALI","code":"HR94","value":"94","full_text":"SDM KALANWALI - HR94( 28-JUL-2017 )"},
    {"name":"SDM KHARKHONDA","code":"HR79","value":"79","full_text":"SDM KHARKHONDA - HR79( 05-JUL-2017 )"},
    {"name":"SDM NARNAUND","code":"HR86","value":"86","full_text":"SDM NARNAUND - HR86( 22-MAY-2017 )"},
    {"name":"SDM OFFICE KALKA","code":"HR49","value":"49","full_text":"SDM OFFICE KALKA - HR49( 26-MAY-2017 )"},
    {"name":"SDM PUNHANA","code":"HR93","value":"93","full_text":"SDM PUNHANA - HR93( 03-MAY-2017 )"},
    {"name":"SDM RADAUR","code":"HR92","value":"92","full_text":"SDM RADAUR - HR92( 24-MAY-2017 )"},
    {"name":"SDM SAMPLA","code":"HR95","value":"95","full_text":"SDM SAMPLA - HR95( 24-APR-2017 )"},
    {"name":"SDM SHAHABAD","code":"HR78","value":"78","full_text":"SDM SHAHABAD - HR78( 08-JUN-2017 )"},
    {"name":"SDM UCHANA","code":"HR90","value":"90","full_text":"SDM UCHANA - HR90( 07-APR-2017 )"},
    {"name":"SIRSA","code":"HR24","value":"24","full_text":"SIRSA - HR24( 03-JUL-2017 )"},
    {"name":"SIWANI","code":"HR17","value":"17","full_text":"SIWANI - HR17( 21-JUL-2017 )"},
    {"name":"SONEPAT","code":"HR10","value":"10","full_text":"SONEPAT - HR10( 05-JUL-2017 )"},
    {"name":"THANESAR","code":"HR7","value":"7","full_text":"THANESAR - HR7( 22-JUN-2017 )"},
    {"name":"TOHANA","code":"HR23","value":"23","full_text":"TOHANA - HR23( 07-JUN-2017 )"},
    {"name":"TOSHAM","code":"HR48","value":"48","full_text":"TOSHAM - HR48( 01-JUN-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Meghalaya
# ──────────────────────────────────────────────────────────────────────────────
STATE_ML = {
  "state": "Meghalaya",
  "state_code": "ML",
  "extraction_date": "2025-07-29T14:16:27.411473",
  "total_rtos": 15,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(14/14)"},
    {"name":"AMPATI","code":"ML14","value":"14","full_text":"AMPATI - ML14( 03-NOV-2017 )"},
    {"name":"BAGHMARA","code":"ML9","value":"9","full_text":"BAGHMARA - ML9( 02-FEB-2017 )"},
    {"name":"Commissioner of Transport","code":"null98","value":"98","full_text":"Commissioner of Transport - null98( 07-MAY-2025 )"},
    {"name":"JOWAI","code":"ML4","value":"4","full_text":"JOWAI - ML4( 03-AUG-2017 )"},
    {"name":"KHLIEHRIAT","code":"ML11","value":"11","full_text":"KHLIEHRIAT - ML11( 11-JUL-2017 )"},
    {"name":"MAIRANG","code":"ML15","value":"15","full_text":"MAIRANG - ML15( 05-JUL-2022 )"},
    {"name":"MAWKYRWAT","code":"ML12","value":"12","full_text":"MAWKYRWAT - ML12( 26-FEB-2018 )"},
    {"name":"NONGPOH","code":"ML10","value":"10","full_text":"NONGPOH - ML10( 06-MAR-2017 )"},
    {"name":"NONGSTOIN","code":"ML6","value":"6","full_text":"NONGSTOIN - ML6( 08-DEC-2017 )"},
    {"name":"RESUBELPARA","code":"ML13","value":"13","full_text":"RESUBELPARA - ML13( 19-DEC-2017 )"},
    {"name":"SHILLONG","code":"ML5","value":"5","full_text":"SHILLONG - ML5( 29-FEB-2016 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"ML99","value":"99","full_text":"STATE TRANSPORT AUTHORITY - ML99( 28-NOV-2017 )"},
    {"name":"TURA","code":"ML8","value":"8","full_text":"TURA - ML8( 31-JAN-2017 )"},
    {"name":"WILLIAMNAGAR","code":"ML7","value":"7","full_text":"WILLIAMNAGAR - ML7( 14-AUG-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# West Bengal — Python seeder
# Notes:
# - A couple of WB ARTOs arrived with code like "null62"/"null98".
#   We normalize any code that starts with "null" to f"WB{value}".
# ──────────────────────────────────────────────────────────────────────────────

STATE_WB_RAW = {
  "state": "West Bengal",
  "state_code": "WB",
  "extraction_date": "2025-07-29T14:48:36.120399",
  "total_rtos": 60,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(59/59)"},
    {"name":"ALIPORE RTO","code":"WB19","value":"19","full_text":"ALIPORE RTO - WB19( 13-DEC-2016 )"},
    {"name":"ALIPURDUAR RTO","code":"WB69","value":"69","full_text":"ALIPURDUAR RTO - WB69( 22-FEB-2017 )"},
    {"name":"ARAMBAG ARTO","code":"WB18","value":"18","full_text":"ARAMBAG ARTO - WB18( 10-JAN-2017 )"},
    {"name":"BANGAON ARTO","code":"WB27","value":"27","full_text":"BANGAON ARTO - WB27( 17-JAN-2017 )"},
    {"name":"BANKURA RTO","code":"WB67","value":"67","full_text":"BANKURA RTO - WB67( 11-APR-2017 )"},
    {"name":"BARASAT RTO","code":"WB25","value":"25","full_text":"BARASAT RTO - WB25( 17-JAN-2017 )"},
    {"name":"BARRACKPORE ARTO","code":"WB23","value":"23","full_text":"BARRACKPORE ARTO - WB23( 27-DEC-2016 )"},
    {"name":"BARUIPUR ARTO","code":"WB95","value":"95","full_text":"BARUIPUR ARTO - WB95( 31-JAN-2017 )"},
    {"name":"BASIRHAT ARTO","code":"WB21","value":"21","full_text":"BASIRHAT ARTO - WB21( 17-JAN-2017 )"},
    {"name":"BEHALA ARTO","code":"WB9","value":"9","full_text":"BEHALA ARTO - WB9( 27-DEC-2017 )"},
    {"name":"BIRBHUM RTO","code":"WB53","value":"53","full_text":"BIRBHUM RTO - WB53( 28-FEB-2017 )"},
    {"name":"BISHNUPUR ARTO","code":"WB87","value":"87","full_text":"BISHNUPUR ARTO - WB87( 11-APR-2017 )"},
    {"name":"BOLPUR ARTO","code":"WB47","value":"47","full_text":"BOLPUR ARTO - WB47( 28-FEB-2017 )"},
    {"name":"BUNIADPUR ARTO","code":"null62","value":"62","full_text":"BUNIADPUR ARTO - null62( 19-MAY-2025 )"},
    {"name":"CANNING ARTO","code":"null98","value":"98","full_text":"CANNING ARTO - null98( 19-MAY-2025 )"},
    {"name":"CHANCHOL ARTO","code":"WB83","value":"83","full_text":"CHANCHOL ARTO - WB83( 23-MAR-2017 )"},
    {"name":"CONTAI ARTO","code":"WB31","value":"31","full_text":"CONTAI ARTO - WB31( 09-FEB-2017 )"},
    {"name":"COOCHBEHAR RTO","code":"WB63","value":"63","full_text":"COOCHBEHAR RTO - WB63( 28-MAR-2017 )"},
    {"name":"DAKSHIN DINAJPUR RTO","code":"WB61","value":"61","full_text":"DAKSHIN DINAJPUR RTO - WB61( 06-APR-2017 )"},
    {"name":"DARJEELING RTO","code":"WB76","value":"76","full_text":"DARJEELING RTO - WB76( 30-MAR-2017 )"},
    {"name":"DIAMOND HARBOUR ARTO","code":"WB97","value":"97","full_text":"DIAMOND HARBOUR ARTO - WB97( 31-JAN-2017 )"},
    {"name":"DURGAPORE ARTO","code":"WB39","value":"39","full_text":"DURGAPORE ARTO - WB39( 21-FEB-2017 )"},
    {"name":"GHATAL ARTO","code":"WB50","value":"50","full_text":"GHATAL ARTO - WB50( 07-MAR-2017 )"},
    {"name":"HALDIA ARTO","code":"WB32","value":"32","full_text":"HALDIA ARTO - WB32( 10-JUL-2017 )"},
    {"name":"HOOGHLY RTO","code":"WB15","value":"15","full_text":"HOOGHLY RTO - WB15( 10-JAN-2017 )"},
    {"name":"HOWRAH RTO","code":"WB11","value":"11","full_text":"HOWRAH RTO - WB11( 20-DEC-2016 )"},
    {"name":"ISLAMPUR ARTO","code":"WB91","value":"91","full_text":"ISLAMPUR ARTO - WB91( 28-MAR-2017 )"},
    {"name":"JALPAIGURI RTO","code":"WB71","value":"71","full_text":"JALPAIGURI RTO - WB71( 21-FEB-2017 )"},
    {"name":"JANGIPUR ARTO","code":"WB93","value":"93","full_text":"JANGIPUR ARTO - WB93( 16-MAR-2017 )"},
    {"name":"JHARGRAM RTO","code":"WB49","value":"49","full_text":"JHARGRAM RTO - WB49( 07-MAR-2017 )"},
    {"name":"KALIMPONG RTO","code":"WB78","value":"78","full_text":"KALIMPONG RTO - WB78( 30-MAR-2017 )"},
    {"name":"KALNA ARTO","code":"WB43","value":"43","full_text":"KALNA ARTO - WB43( 21-FEB-2017 )"},
    {"name":"KALYANI ARTO","code":"WB89","value":"89","full_text":"KALYANI ARTO - WB89( 16-MAR-2017 )"},
    {"name":"KANDI","code":"WB99","value":"99","full_text":"KANDI - WB99( 11-JUL-2024 )"},
    {"name":"KASBA ARTO","code":"WB5","value":"5","full_text":"KASBA ARTO - WB5( 28-SEP-2016 )"},
    {"name":"KATWA ARTO","code":"WB75","value":"75","full_text":"KATWA ARTO - WB75( 04-SEP-2018 )"},
    {"name":"KHARAGPUR ARTO","code":"WB35","value":"35","full_text":"KHARAGPUR ARTO - WB35( 07-MAR-2017 )"},
    {"name":"MALDA RTO","code":"WB65","value":"65","full_text":"MALDA RTO - WB65( 21-MAR-2017 )"},
    {"name":"MANBAZAR","code":"WB80","value":"80","full_text":"MANBAZAR - WB80( 09-JUN-2023 )"},
    {"name":"MATHABHANGA ARTO","code":"WB85","value":"85","full_text":"MATHABHANGA ARTO - WB85( 28-MAR-2017 )"},
    {"name":"MURSHIDABAD RTO","code":"WB57","value":"57","full_text":"MURSHIDABAD RTO - WB57( 23-MAR-2017 )"},
    {"name":"NADIA RTO","code":"WB51","value":"51","full_text":"NADIA RTO - WB51( 06-APR-2017 )"},
    {"name":"PASCHIM BURDWAN RTO","code":"WB37","value":"37","full_text":"PASCHIM BURDWAN RTO - WB37( 04-APR-2017 )"},
    {"name":"PASCHIM MIDNAPORE RTO","code":"WB33","value":"33","full_text":"PASCHIM MIDNAPORE RTO - WB33( 07-MAR-2017 )"},
    {"name":"PURBA BURDWAN RTO","code":"WB41","value":"41","full_text":"PURBA BURDWAN RTO - WB41( 21-FEB-2017 )"},
    {"name":"PURULIA RTO","code":"WB55","value":"55","full_text":"PURULIA RTO - WB55( 16-FEB-2017 )"},
    {"name":"PVD KOLKATA","code":"WB1","value":"1","full_text":"PVD KOLKATA - WB1( 25-JAN-2017 )"},
    {"name":"RAGHUNATHPUR ARTO","code":"WB81","value":"81","full_text":"RAGHUNATHPUR ARTO - WB81( 16-FEB-2017 )"},
    {"name":"RAMPURHAT ARTO","code":"WB45","value":"45","full_text":"RAMPURHAT ARTO - WB45( 28-FEB-2017 )"},
    {"name":"SALTLAKE ARTO","code":"WB7","value":"7","full_text":"SALTLAKE ARTO - WB7( 03-JAN-2017 )"},
    {"name":"SILIGURI ARTO","code":"WB73","value":"73","full_text":"SILIGURI ARTO - WB73( 30-MAR-2017 )"},
    {"name":"SRIRAMPUR ARTO","code":"WB17","value":"17","full_text":"SRIRAMPUR ARTO - WB17( 10-JAN-2017 )"},
    {"name":"STA-Durgapur","code":"WB997","value":"997","full_text":"STA-Durgapur - WB997( 08-MAR-2019 )"},
    {"name":"STA-North Bengal (Siliguri)","code":"WB998","value":"998","full_text":"STA-North Bengal (Siliguri) - WB998( 13-MAR-2019 )"},
    {"name":"STA WEST BENGAL","code":"WB999","value":"999","full_text":"STA WEST BENGAL - WB999( 08-AUG-2018 )"},
    {"name":"TAMLUK RTO","code":"WB29","value":"29","full_text":"TAMLUK RTO - WB29( 09-FEB-2017 )"},
    {"name":"TEHATTA ARTO","code":"WB52","value":"52","full_text":"TEHATTA ARTO - WB52( 08-JUL-2020 )"},
    {"name":"ULUBERIA ARTO","code":"WB13","value":"13","full_text":"ULUBERIA ARTO - WB13( 25-JAN-2017 )"},
    {"name":"UTTAR DINAJPUR RTO","code":"WB59","value":"59","full_text":"UTTAR DINAJPUR RTO - WB59( 04-APR-2017 )"}
  ]
}

def _normalize_wb_code(item):
    code = item.get("code", "")
    if isinstance(code, str) and code.lower().startswith("null"):
        # Fall back to WB + value when code is malformed
        return f"WB{item.get('value')}"
    return code

STATE_WB = {
    **{k: v for k, v in STATE_WB_RAW.items() if k != "rtos"},
    "rtos": [
        {**rt, "code": _normalize_wb_code(rt)}
        for rt in STATE_WB_RAW["rtos"]
    ],
}

# Optional: quick sanity check on unique codes
_codes = [rt["code"] for rt in STATE_WB["rtos"]]
assert len(_codes) == len(set(_codes)), "Duplicate RTO codes detected in WB payload"

# ──────────────────────────────────────────────────────────────────────────────
# Jharkhand
# ──────────────────────────────────────────────────────────────────────────────
STATE_JH = {
  "state": "Jharkhand",
  "state_code": "JH",
  "extraction_date": "2025-07-29T14:02:44.596996",
  "total_rtos": 32,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(25/25)"},
    {"name":"Authorised Testing  Centre (TUV SUD), Ranchi","code":"JH201","value":"201","full_text":"Authorised Testing  Centre (TUV SUD), Ranchi - JH201( 24-AUG-2018 )"},
    {"name":"Authorized Fitness Centre(VAHAN),Dhanbad","code":"JH202","value":"202","full_text":"Authorized Fitness Centre(VAHAN),Dhanbad - JH202( 24-SEP-2019 )"},
    {"name":"BOKARO","code":"JH9","value":"9","full_text":"BOKARO - JH9( 24-JAN-2017 )"},
    {"name":"CHATRA","code":"JH13","value":"13","full_text":"CHATRA - JH13( 19-JAN-2017 )"},
    {"name":"DEOGHAR","code":"JH15","value":"15","full_text":"DEOGHAR - JH15( 19-JAN-2017 )"},
    {"name":"DHANBAD","code":"JH10","value":"10","full_text":"DHANBAD - JH10( 19-JAN-2017 )"},
    {"name":"DTO OFFICE DUMKA","code":"JH4","value":"4","full_text":"DTO OFFICE DUMKA - JH4( 19-JAN-2017 )"},
    {"name":"EAST SINGHBHUM (JAMSHEDPUR)","code":"JH5","value":"5","full_text":"EAST SINGHBHUM (JAMSHEDPUR) - JH5( 19-JAN-2017 )"},
    {"name":"GARHWA","code":"JH14","value":"14","full_text":"GARHWA - JH14( 19-JAN-2017 )"},
    {"name":"GIRIDIH","code":"JH11","value":"11","full_text":"GIRIDIH - JH11( 19-JAN-2017 )"},
    {"name":"GODDA","code":"JH17","value":"17","full_text":"GODDA - JH17( 19-JAN-2017 )"},
    {"name":"GUMLA","code":"JH7","value":"7","full_text":"GUMLA - JH7( 29-JUN-2016 )"},
    {"name":"HAZARIBAG","code":"JH2","value":"2","full_text":"HAZARIBAG - JH2( 19-JAN-2017 )"},
    {"name":"JAMTARA","code":"JH21","value":"21","full_text":"JAMTARA - JH21( 19-JAN-2017 )"},
    {"name":"KHUNTI","code":"JH23","value":"23","full_text":"KHUNTI - JH23( 19-JAN-2017 )"},
    {"name":"KODERMA","code":"JH12","value":"12","full_text":"KODERMA - JH12( 19-JAN-2017 )"},
    {"name":"LATEHAR","code":"JH19","value":"19","full_text":"LATEHAR - JH19( 19-JAN-2017 )"},
    {"name":"LOHARDAGA","code":"JH8","value":"8","full_text":"LOHARDAGA - JH8( 19-JAN-2017 )"},
    {"name":"M/s Auto Fitness Centre,Ranchi","code":"JH203","value":"203","full_text":"M/s Auto Fitness Centre,Ranchi - JH203( 13-NOV-2019 )"},
    {"name":"M/s Auto Tech Vehicle Fitness,Ranchi","code":"JH205","value":"205","full_text":"M/s Auto Tech Vehicle Fitness,Ranchi - JH205( 05-AUG-2021 )"},
    {"name":"M/S Global Automated Fitness,Hazaribag","code":"JH206","value":"206","full_text":"M/S Global Automated Fitness,Hazaribag - JH206( 11-AUG-2023 )"},
    {"name":"M/s Universal Automated Fitness Centre, East Singhbhum","code":"JH204","value":"204","full_text":"M/s Universal Automated Fitness Centre, East Singhbhum - JH204( 09-MAR-2021 )"},
    {"name":"PAKUR","code":"JH16","value":"16","full_text":"PAKUR - JH16( 19-JAN-2017 )"},
    {"name":"PALAMU","code":"JH3","value":"3","full_text":"PALAMU - JH3( 19-JAN-2017 )"},
    {"name":"RAMGARH","code":"JH24","value":"24","full_text":"RAMGARH - JH24( 14-MAR-2016 )"},
    {"name":"RANCHI","code":"JH1","value":"1","full_text":"RANCHI - JH1( 19-JAN-2017 )"},
    {"name":"SAHEBGANJ","code":"JH18","value":"18","full_text":"SAHEBGANJ - JH18( 19-JAN-2017 )"},
    {"name":"SARAIKELA-KHARSAWAN","code":"JH22","value":"22","full_text":"SARAIKELA-KHARSAWAN - JH22( 19-JAN-2017 )"},
    {"name":"SIMDEGA","code":"JH20","value":"20","full_text":"SIMDEGA - JH20( 19-JAN-2017 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"JH99","value":"99","full_text":"STATE TRANSPORT AUTHORITY - JH99( 15-FEB-2022 )"},
    {"name":"WEST SINGHBHUM (CHAIBASA)","code":"JH6","value":"6","full_text":"WEST SINGHBHUM (CHAIBASA) - JH6( 19-JAN-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Mizoram
# ──────────────────────────────────────────────────────────────────────────────
STATE_MZ = {
  "state": "Mizoram",
  "state_code": "MZ",
  "extraction_date": "2025-07-29T14:21:22.705918",
  "total_rtos": 11,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(10/10)"},
    {"name":"AIZAWL DTO","code":"MZ1","value":"1","full_text":"AIZAWL DTO - MZ1( 29-AUG-2017 )"},
    {"name":"AIZAWL RURAL DTO","code":"MZ9","value":"9","full_text":"AIZAWL RURAL DTO - MZ9( 29-AUG-2017 )"},
    {"name":"CHAMPHAI","code":"MZ4","value":"4","full_text":"CHAMPHAI - MZ4( 29-AUG-2017 )"},
    {"name":"KOLASIB","code":"MZ5","value":"5","full_text":"KOLASIB - MZ5( 29-AUG-2017 )"},
    {"name":"LAWNGTLAI","code":"MZ7","value":"7","full_text":"LAWNGTLAI - MZ7( 10-MAY-2018 )"},
    {"name":"LUNGLEI","code":"MZ2","value":"2","full_text":"LUNGLEI - MZ2( 29-AUG-2017 )"},
    {"name":"MAMIT","code":"MZ8","value":"8","full_text":"MAMIT - MZ8( 29-AUG-2017 )"},
    {"name":"SAIHA","code":"MZ3","value":"3","full_text":"SAIHA - MZ3( 29-AUG-2017 )"},
    {"name":"SERCHHIP","code":"MZ6","value":"6","full_text":"SERCHHIP - MZ6( 29-AUG-2017 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"MZ99","value":"99","full_text":"STATE TRANSPORT AUTHORITY - MZ99( 30-AUG-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Kerala
# ──────────────────────────────────────────────────────────────────────────────
STATE_KL = {
  "state": "Kerala",
  "state_code": "KL",
  "extraction_date": "2025-07-29T14:10:22.203929",
  "total_rtos": 88,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(87/87)"},
    {"name":"ADOOR SRTO","code":"KL26","value":"26","full_text":"ADOOR SRTO - KL26( 27-MAR-2019 )"},
    {"name":"ALAPPUZHA RTO","code":"KL4","value":"4","full_text":"ALAPPUZHA RTO - KL4( 18-MAR-2019 )"},
    {"name":"ALATHUR SRTO","code":"KL49","value":"49","full_text":"ALATHUR SRTO - KL49( 30-MAR-2019 )"},
    {"name":"ALUVA SRTO","code":"KL41","value":"41","full_text":"ALUVA SRTO - KL41( 23-MAR-2019 )"},
    {"name":"ANGAMALI SRTO","code":"KL63","value":"63","full_text":"ANGAMALI SRTO - KL63( 23-MAR-2019 )"},
    {"name":"ATTINGAL RTO","code":"KL16","value":"16","full_text":"ATTINGAL RTO - KL16( 18-MAR-2019 )"},
    {"name":"CHADAYAMANGALA SRTO","code":"KL82","value":"82","full_text":"CHADAYAMANGALA SRTO - KL82( 28-SEP-2020 )"},
    {"name":"CHALAKKUDY SRTO","code":"KL64","value":"64","full_text":"CHALAKKUDY SRTO - KL64( 30-MAR-2019 )"},
    {"name":"CHANGANACHERRY SRTO","code":"KL33","value":"33","full_text":"CHANGANACHERRY SRTO - KL33( 30-MAR-2019 )"},
    {"name":"CHENGANNUR SRTO","code":"KL30","value":"30","full_text":"CHENGANNUR SRTO - KL30( 30-MAR-2019 )"},
    {"name":"CHERTHALA SRTO","code":"KL32","value":"32","full_text":"CHERTHALA SRTO - KL32( 30-MAR-2019 )"},
    {"name":"CHITTUR SRTO","code":"KL70","value":"70","full_text":"CHITTUR SRTO - KL70( 23-MAR-2019 )"},
    {"name":"DEVIKULAM SRTO","code":"KL68","value":"68","full_text":"DEVIKULAM SRTO - KL68( 30-MAR-2019 )"},
    {"name":"ERNAKULAM RTO","code":"KL7","value":"7","full_text":"ERNAKULAM RTO - KL7( 14-MAR-2019 )"},
    {"name":"GURUVAYUR SRTO","code":"KL46","value":"46","full_text":"GURUVAYUR SRTO - KL46( 30-MAR-2019 )"},
    {"name":"IDUKKI RTO","code":"KL6","value":"6","full_text":"IDUKKI RTO - KL6( 18-MAR-2019 )"},
    {"name":"IRINJALAKUDA SRTO","code":"KL45","value":"45","full_text":"IRINJALAKUDA SRTO - KL45( 30-MAR-2019 )"},
    {"name":"IRITTY SRTO","code":"KL78","value":"78","full_text":"IRITTY SRTO - KL78( 30-MAR-2019 )"},
    {"name":"KANHANGAD SRTO","code":"KL60","value":"60","full_text":"KANHANGAD SRTO - KL60( 30-MAR-2019 )"},
    {"name":"KANJIRAPPALLY SRTO","code":"KL34","value":"34","full_text":"KANJIRAPPALLY SRTO - KL34( 30-MAR-2019 )"},
    {"name":"KANNUR RTO","code":"KL13","value":"13","full_text":"KANNUR RTO - KL13( 18-MAR-2019 )"},
    {"name":"KARUNAGAPPALLY SRTO","code":"KL23","value":"23","full_text":"KARUNAGAPPALLY SRTO - KL23( 30-MAR-2019 )"},
    {"name":"KASARGODE RTO","code":"KL14","value":"14","full_text":"KASARGODE RTO - KL14( 18-MAR-2019 )"},
    {"name":"KATTAKADA SRTO","code":"KL74","value":"74","full_text":"KATTAKADA SRTO - KL74( 29-MAR-2019 )"},
    {"name":"KAYAMKULAM SRTO","code":"KL29","value":"29","full_text":"KAYAMKULAM SRTO - KL29( 30-MAR-2019 )"},
    {"name":"KAZHAKUTTOM SRTO","code":"KL22","value":"22","full_text":"KAZHAKUTTOM SRTO - KL22( 29-MAR-2019 )"},
    {"name":"KODUNGALLUR SRTO","code":"KL47","value":"47","full_text":"KODUNGALLUR SRTO - KL47( 30-MAR-2019 )"},
    {"name":"KODUVALLY SRTO","code":"KL57","value":"57","full_text":"KODUVALLY SRTO - KL57( 30-MAR-2019 )"},
    {"name":"KOILANDY SRTO","code":"KL56","value":"56","full_text":"KOILANDY SRTO - KL56( 30-MAR-2019 )"},
    {"name":"KOLLAM RTO","code":"KL2","value":"2","full_text":"KOLLAM RTO - KL2( 15-MAR-2019 )"},
    {"name":"KONDOTTY SRTO","code":"KL84","value":"84","full_text":"KONDOTTY SRTO - KL84( 28-SEP-2020 )"},
    {"name":"KONNI SRTO","code":"KL83","value":"83","full_text":"KONNI SRTO - KL83( 06-JUL-2020 )"},
    {"name":"KOTHAMANGALAM SRTO","code":"KL44","value":"44","full_text":"KOTHAMANGALAM SRTO - KL44( 23-MAR-2019 )"},
    {"name":"KOTTARAKKARA SRTO","code":"KL24","value":"24","full_text":"KOTTARAKKARA SRTO - KL24( 30-MAR-2019 )"},
    {"name":"KOTTAYAM RTO","code":"KL5","value":"5","full_text":"KOTTAYAM RTO - KL5( 18-MAR-2019 )"},
    {"name":"KOZHIKODE RTO","code":"KL11","value":"11","full_text":"KOZHIKODE RTO - KL11( 15-MAR-2019 )"},
    {"name":"KUNNATHUR SRTO","code":"KL61","value":"61","full_text":"KUNNATHUR SRTO - KL61( 30-MAR-2019 )"},
    {"name":"KUTTANADU SRTO","code":"KL66","value":"66","full_text":"KUTTANADU SRTO - KL66( 30-MAR-2019 )"},
    {"name":"MALAPPURAM RTO","code":"KL10","value":"10","full_text":"MALAPPURAM RTO - KL10( 20-MAR-2019 )"},
    {"name":"MALLAPPALLY SRTO","code":"KL28","value":"28","full_text":"MALLAPPALLY SRTO - KL28( 27-MAR-2019 )"},
    {"name":"MANANTHAVADY SRTO","code":"KL72","value":"72","full_text":"MANANTHAVADY SRTO - KL72( 30-MAR-2019 )"},
    {"name":"MANNARGHAT SRTO","code":"KL50","value":"50","full_text":"MANNARGHAT SRTO - KL50( 30-MAR-2019 )"},
    {"name":"MATTANCHERRY SRTO","code":"KL43","value":"43","full_text":"MATTANCHERRY SRTO - KL43( 23-MAR-2019 )"},
    {"name":"MAVELIKKARA SRTO","code":"KL31","value":"31","full_text":"MAVELIKKARA SRTO - KL31( 30-MAR-2019 )"},
    {"name":"MUVATTUPUZHA RTO","code":"KL17","value":"17","full_text":"MUVATTUPUZHA RTO - KL17( 15-MAR-2019 )"},
    {"name":"NANMANDA SRTO","code":"KL76","value":"76","full_text":"NANMANDA SRTO - KL76( 30-MAR-2019 )"},
    {"name":"NATIONALISED SECTOR(TVPM) RTO","code":"KL15","value":"15","full_text":"NATIONALISED SECTOR(TVPM) RTO - KL15( 18-MAR-2019 )"},
    {"name":"NEDUMANGADU SRTO","code":"KL21","value":"21","full_text":"NEDUMANGADU SRTO - KL21( 29-MAR-2019 )"},
    {"name":"NEYYATTINKARA SRTO","code":"KL20","value":"20","full_text":"NEYYATTINKARA SRTO - KL20( 29-MAR-2019 )"},
    {"name":"NILAMBUR SRTO","code":"KL71","value":"71","full_text":"NILAMBUR SRTO - KL71( 30-MAR-2019 )"},
    {"name":"NORTH PARUR SRTO","code":"KL42","value":"42","full_text":"NORTH PARUR SRTO - KL42( 23-MAR-2019 )"},
    {"name":"OTTAPPALAM SRTO","code":"KL51","value":"51","full_text":"OTTAPPALAM SRTO - KL51( 30-MAR-2019 )"},
    {"name":"PALAI SRTO","code":"KL35","value":"35","full_text":"PALAI SRTO - KL35( 30-MAR-2019 )"},
    {"name":"PALAKKAD RTO","code":"KL9","value":"9","full_text":"PALAKKAD RTO - KL9( 18-MAR-2019 )"},
    {"name":"PARASSALA SRTO","code":"KL19","value":"19","full_text":"PARASSALA SRTO - KL19( 29-MAR-2019 )"},
    {"name":"PATHANAMTHITTA RTO","code":"KL3","value":"3","full_text":"PATHANAMTHITTA RTO - KL3( 20-MAR-2019 )"},
    {"name":"PATHANAPURAM SRTO","code":"KL80","value":"80","full_text":"PATHANAPURAM SRTO - KL80( 28-SEP-2020 )"},
    {"name":"PATTAMBI SRTO","code":"KL52","value":"52","full_text":"PATTAMBI SRTO - KL52( 30-MAR-2019 )"},
    {"name":"PAYYANNUR SRTO","code":"KL86","value":"86","full_text":"PAYYANNUR SRTO - KL86( 28-SEP-2020 )"},
    {"name":"PERAMBRA SRTO","code":"KL77","value":"77","full_text":"PERAMBRA SRTO - KL77( 30-MAR-2019 )"},
    {"name":"PERINTHALMANNA SRTO","code":"KL53","value":"53","full_text":"PERINTHALMANNA SRTO - KL53( 30-MAR-2019 )"},
    {"name":"PERUMBAVUR SRTO","code":"KL40","value":"40","full_text":"PERUMBAVUR SRTO - KL40( 23-MAR-2019 )"},
    {"name":"PONNANI SRTO","code":"KL54","value":"54","full_text":"PONNANI SRTO - KL54( 30-MAR-2019 )"},
    {"name":"PUNALUR SRTO","code":"KL25","value":"25","full_text":"PUNALUR SRTO - KL25( 30-MAR-2019 )"},
    {"name":"RAMANATTUKARA (FEROKE) SRTO","code":"KL85","value":"85","full_text":"RAMANATTUKARA (FEROKE) SRTO - KL85( 28-SEP-2020 )"},
    {"name":"RANNI SRTO","code":"KL62","value":"62","full_text":"RANNI SRTO - KL62( 30-MAR-2019 )"},
    {"name":"SULTHANBATHERY SRTO","code":"KL73","value":"73","full_text":"SULTHANBATHERY SRTO - KL73( 30-MAR-2019 )"},
    {"name":"TC OFFICE - STA OFFICE","code":"KL99","value":"99","full_text":"TC OFFICE - STA OFFICE - KL99( 14-MAR-2019 )"},
    {"name":"THALASSERY SRTO","code":"KL58","value":"58","full_text":"THALASSERY SRTO - KL58( 30-MAR-2019 )"},
    {"name":"THALIPARAMBA SRTO","code":"KL59","value":"59","full_text":"THALIPARAMBA SRTO - KL59( 30-MAR-2019 )"},
    {"name":"THIRURANGADI SRTO","code":"KL65","value":"65","full_text":"THIRURANGADI SRTO - KL65( 30-MAR-2019 )"},
    {"name":"THIRUR SRTO","code":"KL55","value":"55","full_text":"THIRUR SRTO - KL55( 30-MAR-2019 )"},
    {"name":"THIRUVALLA SRTO","code":"KL27","value":"27","full_text":"THIRUVALLA SRTO - KL27( 27-MAR-2019 )"},
    {"name":"THODUPUZHA SRTO","code":"KL38","value":"38","full_text":"THODUPUZHA SRTO - KL38( 30-MAR-2019 )"},
    {"name":"THRIPRAYAR SRTO","code":"KL75","value":"75","full_text":"THRIPRAYAR SRTO - KL75( 30-MAR-2019 )"},
    {"name":"THRISSUR RTO","code":"KL8","value":"8","full_text":"THRISSUR RTO - KL8( 18-MAR-2019 )"},
    {"name":"TRIPUNITHURA SRTO","code":"KL39","value":"39","full_text":"TRIPUNITHURA SRTO - KL39( 23-MAR-2019 )"},
    {"name":"TRIVANDRUM RTO","code":"KL1","value":"1","full_text":"TRIVANDRUM RTO - KL1( 21-FEB-2019 )"},
    {"name":"UDUMBANCHOLA SRTO","code":"KL69","value":"69","full_text":"UDUMBANCHOLA SRTO - KL69( 30-MAR-2019 )"},
    {"name":"UZHAVOOR SRTO","code":"KL67","value":"67","full_text":"UZHAVOOR SRTO - KL67( 30-MAR-2019 )"},
    {"name":"VADAKARA RTO","code":"KL18","value":"18","full_text":"VADAKARA RTO - KL18( 15-MAR-2019 )"},
    {"name":"VAIKOM SRTO","code":"KL36","value":"36","full_text":"VAIKOM SRTO - KL36( 30-MAR-2019 )"},
    {"name":"VANDIPERIYAR SRTO","code":"KL37","value":"37","full_text":"VANDIPERIYAR SRTO - KL37( 30-MAR-2019 )"},
    {"name":"VARKALA SRTO","code":"KL81","value":"81","full_text":"VARKALA SRTO - KL81( 10-JUL-2020 )"},
    {"name":"VELLARIKUNDU SRTO","code":"KL79","value":"79","full_text":"VELLARIKUNDU SRTO - KL79( 30-MAR-2019 )"},
    {"name":"WADAKKANCHERRY SRTO","code":"KL48","value":"48","full_text":"WADAKKANCHERRY SRTO - KL48( 30-MAR-2019 )"},
    {"name":"WAYANAD RTO","code":"KL12","value":"12","full_text":"WAYANAD RTO - KL12( 15-MAR-2019 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Nagaland
# ──────────────────────────────────────────────────────────────────────────────
STATE_NL = {
  "state": "Nagaland",
  "state_code": "NL",
  "extraction_date": "2025-07-29T14:22:35.645465",
  "total_rtos": 10,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(9/9)"},
    {"name":"DIMAPUR DTO","code":"NL7","value":"7","full_text":"DIMAPUR DTO - NL7( 19-JUN-2018 )"},
    {"name":"KOHIMA RTO","code":"NL1","value":"1","full_text":"KOHIMA RTO - NL1( 16-SEP-2019 )"},
    {"name":"MOKOKCHUNG RTO","code":"NL2","value":"2","full_text":"MOKOKCHUNG RTO - NL2( 05-APR-2019 )"},
    {"name":"MON DTO","code":"NL4","value":"4","full_text":"MON DTO - NL4( 30-NOV-2018 )"},
    {"name":"PHEK DTO","code":"NL8","value":"8","full_text":"PHEK DTO - NL8( 16-NOV-2018 )"},
    {"name":"TRANSPORT COMMISSIONERATE","code":"NL99","value":"99","full_text":"TRANSPORT COMMISSIONERATE - NL99( 20-JUL-2021 )"},
    {"name":"TUENSANG DTO","code":"NL3","value":"3","full_text":"TUENSANG DTO - NL3( 05-NOV-2018 )"},
    {"name":"WOKHA DTO","code":"NL5","value":"5","full_text":"WOKHA DTO - NL5( 04-OCT-2018 )"},
    {"name":"ZUNHEBOTO DTO","code":"NL6","value":"6","full_text":"ZUNHEBOTO DTO - NL6( 28-MAR-2019 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Madhya Pradesh
# ──────────────────────────────────────────────────────────────────────────────
STATE_MP = {
  "state": "Madhya Pradesh",
  "state_code": "MP",
  "extraction_date": "2025-07-29T14:20:08.928644",
  "total_rtos": 54,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(53/53)"},
    {"name":"AGAR MALWA RTO","code":"MP70","value":"70","full_text":"AGAR MALWA RTO - MP70( 25-JUL-2022 )"},
    {"name":"ALIRAJPUR DTO","code":"MP69","value":"69","full_text":"ALIRAJPUR DTO - MP69( 23-JUL-2022 )"},
    {"name":"ANUPPUR DTO","code":"MP65","value":"65","full_text":"ANUPPUR DTO - MP65( 23-JUL-2022 )"},
    {"name":"ASHOKNAGAR DTO","code":"MP67","value":"67","full_text":"ASHOKNAGAR DTO - MP67( 23-JUL-2022 )"},
    {"name":"BADWANI DTO","code":"MP46","value":"46","full_text":"BADWANI DTO - MP46( 23-JUL-2022 )"},
    {"name":"BALAGHAT DTO","code":"MP50","value":"50","full_text":"BALAGHAT DTO - MP50( 23-JUL-2022 )"},
    {"name":"BETUL DTO","code":"MP48","value":"48","full_text":"BETUL DTO - MP48( 23-JUL-2022 )"},
    {"name":"BHIND DTO","code":"MP30","value":"30","full_text":"BHIND DTO - MP30( 23-JUL-2022 )"},
    {"name":"BHOPAL RTO","code":"MP4","value":"4","full_text":"BHOPAL RTO - MP4( 23-JUL-2022 )"},
    {"name":"BURHANPUR DTO","code":"MP68","value":"68","full_text":"BURHANPUR DTO - MP68( 23-JUL-2022 )"},
    {"name":"CHATTARPUR  ARTO","code":"MP16","value":"16","full_text":"CHATTARPUR  ARTO - MP16( 23-JUL-2022 )"},
    {"name":"CHHINDWARA ARTO","code":"MP28","value":"28","full_text":"CHHINDWARA ARTO - MP28( 23-JUL-2022 )"},
    {"name":"DAMOH DTO","code":"MP34","value":"34","full_text":"DAMOH DTO - MP34( 23-JUL-2022 )"},
    {"name":"DATIA DTO","code":"MP32","value":"32","full_text":"DATIA DTO - MP32( 23-JUL-2022 )"},
    {"name":"DEWAS DTO","code":"MP41","value":"41","full_text":"DEWAS DTO - MP41( 23-JUL-2022 )"},
    {"name":"DHAR ARTO","code":"MP11","value":"11","full_text":"DHAR ARTO - MP11( 23-JUL-2022 )"},
    {"name":"DINDORI DTO","code":"MP52","value":"52","full_text":"DINDORI DTO - MP52( 26-JUL-2022 )"},
    {"name":"GUNA DTO","code":"MP8","value":"8","full_text":"GUNA DTO - MP8( 23-JUL-2022 )"},
    {"name":"GWALIOR RTO","code":"MP7","value":"7","full_text":"GWALIOR RTO - MP7( 23-JUL-2022 )"},
    {"name":"HARDA DTO","code":"MP47","value":"47","full_text":"HARDA DTO - MP47( 23-JUL-2022 )"},
    {"name":"HOSANGABAD DTO","code":"MP5","value":"5","full_text":"HOSANGABAD DTO - MP5( 23-JUL-2022 )"},
    {"name":"INDORE RTO","code":"MP9","value":"9","full_text":"INDORE RTO - MP9( 23-JUL-2022 )"},
    {"name":"JABALPUR RTO","code":"MP20","value":"20","full_text":"JABALPUR RTO - MP20( 23-JUL-2022 )"},
    {"name":"JHABUA DTO","code":"MP45","value":"45","full_text":"JHABUA DTO - MP45( 23-JUL-2022 )"},
    {"name":"KATNI ARTO","code":"MP21","value":"21","full_text":"KATNI ARTO - MP21( 23-JUL-2022 )"},
    {"name":"KHANDWA ARTO","code":"MP12","value":"12","full_text":"KHANDWA ARTO - MP12( 23-JUL-2022 )"},
    {"name":"KHARGONE ARTO","code":"MP10","value":"10","full_text":"KHARGONE ARTO - MP10( 23-JUL-2022 )"},
    {"name":"MANDLA DTO","code":"MP51","value":"51","full_text":"MANDLA DTO - MP51( 23-JUL-2022 )"},
    {"name":"MANDSAUR ARTO","code":"MP14","value":"14","full_text":"MANDSAUR ARTO - MP14( 23-JUL-2022 )"},
    {"name":"MORENA DTO","code":"MP6","value":"6","full_text":"MORENA DTO - MP6( 23-JUL-2022 )"},
    {"name":"NARSINGHPUR DTO","code":"MP49","value":"49","full_text":"NARSINGHPUR DTO - MP49( 23-JUL-2022 )"},
    {"name":"NEEMUCH DTO","code":"MP44","value":"44","full_text":"NEEMUCH DTO - MP44( 23-JUL-2022 )"},
    {"name":"NIWARI DTO","code":"MP71","value":"71","full_text":"NIWARI DTO - MP71( 20-OCT-2023 )"},
    {"name":"PANNA DTO","code":"MP35","value":"35","full_text":"PANNA DTO - MP35( 23-JUL-2022 )"},
    {"name":"RAISEN DTO","code":"MP38","value":"38","full_text":"RAISEN DTO - MP38( 23-JUL-2022 )"},
    {"name":"RAJGARH DTO","code":"MP39","value":"39","full_text":"RAJGARH DTO - MP39( 23-JUL-2022 )"},
    {"name":"RATLAM DTO","code":"MP43","value":"43","full_text":"RATLAM DTO - MP43( 23-JUL-2022 )"},
    {"name":"REWA RTO","code":"MP17","value":"17","full_text":"REWA RTO - MP17( 23-JUL-2022 )"},
    {"name":"SAGAR RTO","code":"MP15","value":"15","full_text":"SAGAR RTO - MP15( 23-JUL-2022 )"},
    {"name":"SATNA ARTO","code":"MP19","value":"19","full_text":"SATNA ARTO - MP19( 23-JUL-2022 )"},
    {"name":"SEHORE DTO","code":"MP37","value":"37","full_text":"SEHORE DTO - MP37( 23-JUL-2022 )"},
    {"name":"SEONI ARTO","code":"MP22","value":"22","full_text":"SEONI ARTO - MP22( 23-JUL-2022 )"},
    {"name":"SHAHDOL RTO","code":"MP18","value":"18","full_text":"SHAHDOL RTO - MP18( 23-JUL-2022 )"},
    {"name":"SHAJAPUR DTO","code":"MP42","value":"42","full_text":"SHAJAPUR DTO - MP42( 23-JUL-2022 )"},
    {"name":"SHEOPUR DTO","code":"MP31","value":"31","full_text":"SHEOPUR DTO - MP31( 23-JUL-2022 )"},
    {"name":"SHIVPURI DTO","code":"MP33","value":"33","full_text":"SHIVPURI DTO - MP33( 23-JUL-2022 )"},
    {"name":"SIDHI DTO","code":"MP53","value":"53","full_text":"SIDHI DTO - MP53( 26-JUL-2022 )"},
    {"name":"SINGROLI DTO","code":"MP66","value":"66","full_text":"SINGROLI DTO - MP66( 23-JUL-2022 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"MP999","value":"999","full_text":"STATE TRANSPORT AUTHORITY - MP999( 14-FEB-2023 )"},
    {"name":"TIKAMGARH DTO","code":"MP36","value":"36","full_text":"TIKAMGARH DTO - MP36( 23-JUL-2022 )"},
    {"name":"UJJAIN RTO","code":"MP13","value":"13","full_text":"UJJAIN RTO - MP13( 23-JUL-2022 )"},
    {"name":"UMARIA DTO","code":"MP54","value":"54","full_text":"UMARIA DTO - MP54( 26-JUL-2022 )"},
    {"name":"VIDISHA DTO","code":"MP40","value":"40","full_text":"VIDISHA DTO - MP40( 19-JUL-2022 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Puducherry
# ──────────────────────────────────────────────────────────────────────────────
STATE_PY = {
  "state": "Puducherry",
  "state_code": "PY",
  "extraction_date": "2025-07-29T14:29:17.363047",
  "total_rtos": 9,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(8/8)"},
    {"name":"BAHOUR","code":"PY11","value":"11","full_text":"BAHOUR - PY11( 27-JAN-2017 )"},
    {"name":"CHECK POST","code":"PY99","value":"99","full_text":"CHECK POST - PY99( 23-MAR-2018 )"},
    {"name":"KARAIKAL","code":"PY2","value":"2","full_text":"KARAIKAL - PY2( 16-APR-2018 )"},
    {"name":"MAHE","code":"PY3","value":"3","full_text":"MAHE - PY3( 12-MAR-2018 )"},
    {"name":"OULGARET","code":"PY5","value":"5","full_text":"OULGARET - PY5( 06-FEB-2018 )"},
    {"name":"PUDUCHERRY","code":"PY1","value":"1","full_text":"PUDUCHERRY - PY1( 28-MAY-2018 )"},
    {"name":"VILLIANUR","code":"PY51","value":"51","full_text":"VILLIANUR - PY51( 27-JUN-2017 )"},
    {"name":"YANAM","code":"PY4","value":"4","full_text":"YANAM - PY4( 03-MAR-2018 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Himachal Pradesh — Python seeder
# ──────────────────────────────────────────────────────────────────────────────

STATE_HP = {
  "state": "Himachal Pradesh",
  "state_code": "HP",
  "extraction_date": "2025-07-29T13:55:06.367548",
  "total_rtos": 115,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(96/96)"},
    {"name":"HRTC BAIJNATH","code":"HP113","value":"113","full_text":"HRTC BAIJNATH - HP113( 18-DEC-2017 )"},
    {"name":"HRTC BILASPUR","code":"HP105","value":"105","full_text":"HRTC BILASPUR - HP105( 18-DEC-2017 )"},
    {"name":"HRTC CHAMBA","code":"HP115","value":"115","full_text":"HRTC CHAMBA - HP115( 18-DEC-2017 )"},
    {"name":"HRTC DEHRA","code":"HP114","value":"114","full_text":"HRTC DEHRA - HP114( 11-DEC-2017 )"},
    {"name":"HRTC DHARAMSHALA","code":"HP111","value":"111","full_text":"HRTC DHARAMSHALA - HP111( 20-NOV-2017 )"},
    {"name":"HRTC HAMIRPUR","code":"HP119","value":"119","full_text":"HRTC HAMIRPUR - HP119( 11-DEC-2017 )"},
    {"name":"HRTC JASSUR","code":"HP107","value":"107","full_text":"HRTC JASSUR - HP107( 18-DEC-2017 )"},
    {"name":"HRTC KULLU","code":"HP104","value":"104","full_text":"HRTC KULLU - HP104( 18-DEC-2017 )"},
    {"name":"HRTC MANDI","code":"HP106","value":"106","full_text":"HRTC MANDI - HP106( 18-DEC-2017 )"},
    {"name":"HRTC NAHAN","code":"HP110","value":"110","full_text":"HRTC NAHAN - HP110( 18-DEC-2017 )"},
    {"name":"HRTC NALAGARH","code":"HP109","value":"109","full_text":"HRTC NALAGARH - HP109( 11-DEC-2017 )"},
    {"name":"HRTC PALAMPUR","code":"HP112","value":"112","full_text":"HRTC PALAMPUR - HP112( 18-DEC-2017 )"},
    {"name":"HRTC RAMPUR","code":"HP122","value":"122","full_text":"HRTC RAMPUR - HP122( 18-DEC-2017 )"},
    {"name":"HRTC SARKAGHAT","code":"HP116","value":"116","full_text":"HRTC SARKAGHAT - HP116( 18-DEC-2017 )"},
    {"name":"HRTC SHIMLA(RURAL)","code":"HP121","value":"121","full_text":"HRTC SHIMLA(RURAL) - HP121( 18-DEC-2017 )"},
    {"name":"HRTC SUNDERNAGAR","code":"HP117","value":"117","full_text":"HRTC SUNDERNAGAR - HP117( 18-DEC-2017 )"},
    {"name":"HRTC TARADEVI","code":"HP103","value":"103","full_text":"HRTC TARADEVI - HP103( 18-DEC-2017 )"},
    {"name":"HRTC UNA","code":"HP108","value":"108","full_text":"HRTC UNA - HP108( 11-DEC-2017 )"},
    {"name":"RLA AMB","code":"HP19","value":"19","full_text":"RLA AMB - HP19( 07-JUL-2017 )"},
    {"name":"RLA ANI","code":"HP35","value":"35","full_text":"RLA ANI - HP35( 15-JUL-2017 )"},
    {"name":"RLA ARKI","code":"HP11","value":"11","full_text":"RLA ARKI - HP11( 07-JUL-2017 )"},
    {"name":"RLA BADDI","code":"HP127","value":"127","full_text":"RLA BADDI - HP127( 26-OCT-2024 )"},
    {"name":"RLA BAIJNATH","code":"HP53","value":"53","full_text":"RLA BAIJNATH - HP53( 30-JUN-2017 )"},
    {"name":"RLA BALH","code":"HP82","value":"82","full_text":"RLA BALH - HP82( 19-JUL-2017 )"},
    {"name":"RLA BALICHOWKI","code":"HP123","value":"123","full_text":"RLA BALICHOWKI - HP123( 25-JUN-2022 )"},
    {"name":"RLA BANGANA","code":"HP78","value":"78","full_text":"RLA BANGANA - HP78( 22-JUL-2017 )"},
    {"name":"RLA BANJAR","code":"HP49","value":"49","full_text":"RLA BANJAR - HP49( 15-JUL-2017 )"},
    {"name":"RLA BARSAR","code":"HP21","value":"21","full_text":"RLA BARSAR - HP21( 10-JUL-2017 )"},
    {"name":"RLA BHARMOUR","code":"HP46","value":"46","full_text":"RLA BHARMOUR - HP46( 12-JUL-2017 )"},
    {"name":"RLA BHORANJ","code":"HP74","value":"74","full_text":"RLA BHORANJ - HP74( 10-JUL-2017 )"},
    {"name":"RLA BILASPUR","code":"HP24","value":"24","full_text":"RLA BILASPUR - HP24( 12-JUN-2017 )"},
    {"name":"RLA CHAMBA","code":"HP48","value":"48","full_text":"RLA CHAMBA - HP48( 12-JUN-2017 )"},
    {"name":"RLA CHOPAL","code":"HP8","value":"8","full_text":"RLA CHOPAL - HP8( 21-JUN-2017 )"},
    {"name":"RLA CHURAH","code":"HP44","value":"44","full_text":"RLA CHURAH - HP44( 07-JUL-2017 )"},
    {"name":"RLA CHUWARI","code":"HP57","value":"57","full_text":"RLA CHUWARI - HP57( 07-JUL-2017 )"},
    {"name":"RLA DALHOUSIE","code":"HP47","value":"47","full_text":"RLA DALHOUSIE - HP47( 05-JUL-2017 )"},
    {"name":"RLA DEHRA","code":"HP36","value":"36","full_text":"RLA DEHRA - HP36( 12-JUL-2017 )"},
    {"name":"RLA DHARAMPUR","code":"HP86","value":"86","full_text":"RLA DHARAMPUR - HP86( 19-JUL-2017 )"},
    {"name":"RLA DHARAMSHALA","code":"HP39","value":"39","full_text":"RLA DHARAMSHALA - HP39( 22-MAY-2017 )"},
    {"name":"RLA DHEERA","code":"HP96","value":"96","full_text":"RLA DHEERA  - HP96( 05-MAR-2018 )"},
    {"name":"RLA DODRA KAWAR","code":"HP77","value":"77","full_text":"RLA DODRA KAWAR - HP77( 21-JUN-2017 )"},
    {"name":"RLA FATHEPUR","code":"HP88","value":"88","full_text":"RLA FATHEPUR - HP88( 26-DEC-2016 )"},
    {"name":"RLA GAGRET","code":"HP101","value":"101","full_text":"RLA GAGRET - HP101( 19-NOV-2019 )"},
    {"name":"RLA GHUMARVI","code":"HP23","value":"23","full_text":"RLA GHUMARVI - HP23( 05-JUL-2017 )"},
    {"name":"RLA GOHAR","code":"HP32","value":"32","full_text":"RLA GOHAR - HP32( 15-JUL-2017 )"},
    {"name":"RLA HAMIRPUR","code":"HP22","value":"22","full_text":"RLA HAMIRPUR - HP22( 12-JUN-2017 )"},
    {"name":"RLA HAROLI","code":"HP80","value":"80","full_text":"RLA HAROLI - HP80( 15-JUL-2017 )"},
    {"name":"RLA INDORA","code":"HP97","value":"97","full_text":"RLA INDORA  - HP97( 19-FEB-2018 )"},
    {"name":"RLA JAISINGPUR","code":"HP56","value":"56","full_text":"RLA JAISINGPUR - HP56( 30-JUN-2017 )"},
    {"name":"RLA JAWALAJI","code":"HP83","value":"83","full_text":"RLA JAWALAJI - HP83( 19-JUL-2017 )"},
    {"name":"RLA JAWALI","code":"HP54","value":"54","full_text":"RLA JAWALI - HP54( 15-JUL-2017 )"},
    {"name":"RLA JHANDUTTA","code":"HP89","value":"89","full_text":"RLA JHANDUTTA - HP89( 13-JUN-2017 )"},
    {"name":"RLA JOGINDER NAGAR","code":"HP29","value":"29","full_text":"RLA JOGINDER NAGAR - HP29( 15-JUL-2017 )"},
    {"name":"RLA JUBBAL","code":"HP75","value":"75","full_text":"RLA JUBBAL - HP75( 10-FEB-2023 )"},
    {"name":"RLA KAFFOTA","code":"HP125","value":"125","full_text":"RLA KAFFOTA - HP125( 25-NOV-2022 )"},
    {"name":"RLA KALPA","code":"HP25","value":"25","full_text":"RLA KALPA - HP25( 12-JUN-2017 )"},
    {"name":"RLA KANDAGHAT","code":"HP13","value":"13","full_text":"RLA KANDAGHAT - HP13( 19-JUL-2017 )"},
    {"name":"RLA KANGRA","code":"HP40","value":"40","full_text":"RLA KANGRA - HP40( 01-JUL-2017 )"},
    {"name":"RLA KARSOG","code":"HP30","value":"30","full_text":"RLA KARSOG - HP30( 15-JUL-2017 )"},
    {"name":"RLA KASAULI","code":"HP98","value":"98","full_text":"RLA KASAULI - HP98( 25-JUN-2021 )"},
    {"name":"RLA KAZA","code":"HP41","value":"41","full_text":"RLA KAZA - HP41( 17-JUL-2017 )"},
    {"name":"RLA KELANG","code":"HP42","value":"42","full_text":"RLA KELANG - HP42( 12-JUN-2017 )"},
    {"name":"RLA KOTKHAI","code":"HP99","value":"99","full_text":"RLA KOTKHAI - HP99( 10-FEB-2023 )"},
    {"name":"RLA KOTLI","code":"HP102","value":"102","full_text":"RLA KOTLI - HP102( 12-MAR-2022 )"},
    {"name":"RLA KULU","code":"HP34","value":"34","full_text":"RLA KULU - HP34( 12-JUN-2017 )"},
    {"name":"RLA KUMARSAIN","code":"HP95","value":"95","full_text":"RLA KUMARSAIN - HP95( 26-JUL-2017 )"},
    {"name":"RLA KUPVI","code":"HP126","value":"126","full_text":"RLA KUPVI - HP126( 10-FEB-2023 )"},
    {"name":"RLA MANALI","code":"HP58","value":"58","full_text":"RLA MANALI - HP58( 05-JUL-2017 )"},
    {"name":"RLA MANDI","code":"HP33","value":"33","full_text":"RLA MANDI - HP33( 12-JUN-2017 )"},
    {"name":"RLA NADAUN","code":"HP55","value":"55","full_text":"RLA NADAUN - HP55( 05-JUL-2017 )"},
    {"name":"RLA NAGROTA BAGWAN","code":"HP94","value":"94","full_text":"RLA NAGROTA BAGWAN - HP94( 29-SEP-2017 )"},
    {"name":"RLA NAHAN","code":"HP18","value":"18","full_text":"RLA NAHAN - HP18( 12-JUN-2017 )"},
    {"name":"RLA NALAGARH","code":"HP12","value":"12","full_text":"RLA NALAGARH - HP12( 21-JUN-2017 )"},
    {"name":"RLA NICHAR","code":"HP26","value":"26","full_text":"RLA NICHAR - HP26( 21-JUN-2017 )"},
    {"name":"RLA NIRMAND","code":"HP124","value":"124","full_text":"RLA NIRMAND - HP124( 05-SEP-2022 )"},
    {"name":"RLA NURPUR","code":"HP38","value":"38","full_text":"RLA NURPUR - HP38( 12-JUL-2017 )"},
    {"name":"RLA PACHHAD","code":"HP100","value":"100","full_text":"RLA PACHHAD - HP100( 19-NOV-2019 )"},
    {"name":"RLA PADDHAR","code":"HP76","value":"76","full_text":"RLA PADDHAR - HP76( 05-JUL-2017 )"},
    {"name":"RLA PALAMPUR","code":"HP37","value":"37","full_text":"RLA PALAMPUR - HP37( 01-JUL-2017 )"},
    {"name":"RLA PANGI","code":"HP45","value":"45","full_text":"RLA PANGI - HP45( 22-JUL-2017 )"},
    {"name":"RLA PAONTA SAHIB","code":"HP17","value":"17","full_text":"RLA PAONTA SAHIB - HP17( 05-JUL-2017 )"},
    {"name":"RLA PARWANOO","code":"HP15","value":"15","full_text":"RLA PARWANOO - HP15( 22-JUL-2017 )"},
    {"name":"RLA POOH","code":"HP27","value":"27","full_text":"RLA POOH - HP27( 21-JUN-2017 )"},
    {"name":"RLA RAJGARH","code":"HP16","value":"16","full_text":"RLA RAJGARH - HP16( 10-JUL-2017 )"},
    {"name":"RLA RAMPUR BUSHAR","code":"HP6","value":"6","full_text":"RLA RAMPUR BUSHAR - HP6( 21-JUN-2017 )"},
    {"name":"RLA ROHRU","code":"HP10","value":"10","full_text":"RLA ROHRU - HP10( 21-JUN-2017 )"},
    {"name":"RLA SALOONI","code":"HP81","value":"81","full_text":"RLA SALOONI - HP81( 20-JUN-2017 )"},
    {"name":"RLA SANGRAH","code":"HP79","value":"79","full_text":"RLA SANGRAH - HP79( 10-JUL-2017 )"},
    {"name":"RLA SARKAGHAT","code":"HP28","value":"28","full_text":"RLA SARKAGHAT - HP28( 15-JUL-2017 )"},
    {"name":"RLA SHAHPUR","code":"HP90","value":"90","full_text":"RLA SHAHPUR - HP90( 15-MAR-2017 )"},
    {"name":"RLA SHILLAI","code":"HP85","value":"85","full_text":"RLA SHILLAI - HP85( 10-JUL-2017 )"},
    {"name":"RLA SHIMLA HP-03/HP-07(URBAN)","code":"HP3","value":"3","full_text":"RLA SHIMLA HP-03/HP-07(URBAN) - HP3( 22-MAY-2017 )"},
    {"name":"RLA SHIMLA(RURAL)","code":"HP51","value":"51","full_text":"RLA SHIMLA(RURAL) - HP51( 12-JUN-2017 )"},
    {"name":"RLA SHRI NAINA DEVI JI SWARGHAT","code":"HP91","value":"91","full_text":"RLA SHRI NAINA DEVI JI SWARGHAT - HP91( 28-JUL-2017 )"},
    {"name":"RLA SOLAN","code":"HP14","value":"14","full_text":"RLA SOLAN - HP14( 12-JUN-2017 )"},
    {"name":"RLA SUJANPUR","code":"HP84","value":"84","full_text":"RLA SUJANPUR - HP84( 10-JUL-2017 )"},
    {"name":"RLA SUNDARNAGAR","code":"HP31","value":"31","full_text":"RLA SUNDARNAGAR - HP31( 15-JUL-2017 )"},
    {"name":"RLA THEOG","code":"HP9","value":"9","full_text":"RLA THEOG - HP9( 21-JUN-2017 )"},
    {"name":"RLA THUNAG","code":"HP87","value":"87","full_text":"RLA THUNAG - HP87( 02-MAY-2017 )"},
    {"name":"RLA UDAIPUR","code":"HP43","value":"43","full_text":"RLA UDAIPUR - HP43( 05-JUL-2017 )"},
    {"name":"RLA UNA","code":"HP20","value":"20","full_text":"RLA UNA - HP20( 12-JUN-2017 )"},
    {"name":"RTO BADDI(NALAGARH)","code":"HP93","value":"93","full_text":"RTO BADDI(NALAGARH) - HP93( 05-JUN-2017 )"},
    {"name":"RTO BILASPUR","code":"HP69","value":"69","full_text":"RTO BILASPUR - HP69( 11-OCT-2017 )"},
    {"name":"RTO CHAMBA","code":"HP73","value":"73","full_text":"RTO CHAMBA - HP73( 13-OCT-2017 )"},
    {"name":"RTO DHARAMSHALA","code":"HP68","value":"68","full_text":"RTO DHARAMSHALA - HP68( 29-SEP-2017 )"},
    {"name":"RTO HAMIRPUR","code":"HP67","value":"67","full_text":"RTO HAMIRPUR - HP67( 06-OCT-2017 )"},
    {"name":"RTO KULLU","code":"HP66","value":"66","full_text":"RTO KULLU - HP66( 20-SEP-2017 )"},
    {"name":"RTO MANDI","code":"HP65","value":"65","full_text":"RTO MANDI - HP65( 22-SEP-2017 )"},
    {"name":"RTO NAHAN","code":"HP71","value":"71","full_text":"RTO NAHAN - HP71( 18-OCT-2017 )"},
    {"name":"RTO RAMPUR","code":"HP92","value":"92","full_text":"RTO RAMPUR - HP92( 30-MAY-2017 )"},
    {"name":"RTO SHIMLA","code":"HP63","value":"63","full_text":"RTO SHIMLA - HP63( 14-AUG-2017 )"},
    {"name":"RTO SOLAN","code":"HP64","value":"64","full_text":"RTO SOLAN - HP64( 27-SEP-2017 )"},
    {"name":"RTO UNA","code":"HP72","value":"72","full_text":"RTO UNA - HP72( 25-OCT-2017 )"},
    {"name":"STA SHIMLA","code":"HP62","value":"62","full_text":"STA SHIMLA - HP62( 21-JUN-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Sikkim
# ──────────────────────────────────────────────────────────────────────────────
STATE_SK = {
  "state": "Sikkim",
  "state_code": "SK",
  "extraction_date": "2025-07-29T14:35:15.609759",
  "total_rtos": 10,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(9/9)"},
    {"name":"GYALSING","code":"SK2","value":"2","full_text":"GYALSING - SK2( 05-JUL-2017 )"},
    {"name":"JORETHANG","code":"SK4","value":"4","full_text":"JORETHANG - SK4( 19-APR-2018 )"},
    {"name":"MANGAN","code":"SK3","value":"3","full_text":"MANGAN - SK3( 24-APR-2017 )"},
    {"name":"NAMCHI","code":"SK5","value":"5","full_text":"NAMCHI - SK5( 01-DEC-2017 )"},
    {"name":"Office of the Secretary, STA","code":"SK99","value":"99","full_text":"Office of the Secretary, STA - SK99( 23-JAN-2024 )"},
    {"name":"Pakyong","code":"SK7","value":"7","full_text":"Pakyong - SK7( 12-JUN-2018 )"},
    {"name":"RTO GANGTOK","code":"SK1","value":"1","full_text":"RTO GANGTOK - SK1( 12-SEP-2016 )"},
    {"name":"Singtam, East Sikkim","code":"SK8","value":"8","full_text":"Singtam, East Sikkim - SK8( 25-JAN-2019 )"},
    {"name":"SORENG","code":"SK6","value":"6","full_text":"SORENG - SK6( 02-APR-2018 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Delhi
# ──────────────────────────────────────────────────────────────────────────────
STATE_DL = {
  "state": "Delhi",
  "state_code": "DL",
  "extraction_date": "2025-07-29T13:47:46.560823",
  "total_rtos": 24,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(16/16)"},
    {"name":"BURARI AUTO UNIT","code":"DL53","value":"53","full_text":"BURARI AUTO UNIT - DL53( 08-APR-2016 )"},
    {"name":"BURARI TAXI UNIT","code":"DL52","value":"52","full_text":"BURARI TAXI UNIT - DL52( 08-APR-2016 )"},
    {"name":"DWARKA","code":"DL9","value":"9","full_text":"DWARKA - DL9( 28-JUL-2015 )"},
    {"name":"I P ESTATE","code":"DL2","value":"2","full_text":"I P ESTATE - DL2( 01-JUN-2015 )"},
    {"name":"JANAKPURI","code":"DL4","value":"4","full_text":"JANAKPURI - DL4( 24-JUL-2015 )"},
    {"name":"JHULJHULI FITNESS CENTER","code":"DL207","value":"207","full_text":"JHULJHULI FITNESS CENTER - DL207( 19-JUN-2017 )"},
    {"name":"KAIR CLUSTER BUS FITNESS CENTER","code":"DL205","value":"205","full_text":"KAIR CLUSTER BUS FITNESS CENTER - DL205( 18-JAN-2017 )"},
    {"name":"KUSHAKNALA CLUSTER BUS FITNESS CENTER","code":"DL206","value":"206","full_text":"KUSHAKNALA CLUSTER BUS FITNESS CENTER - DL206( 18-JAN-2017 )"},
    {"name":"LADO SARAI FITNESS CENTER","code":"DL201","value":"201","full_text":"LADO SARAI FITNESS CENTER - DL201( 18-JAN-2017 )"},
    {"name":"LONI ROAD","code":"DL5","value":"5","full_text":"LONI ROAD - DL5( 09-SEP-2015 )"},
    {"name":"MALL ROAD","code":"DL1","value":"1","full_text":"MALL ROAD - DL1( 12-OCT-2015 )"},
    {"name":"MAYUR VIHAR","code":"DL7","value":"7","full_text":"MAYUR VIHAR - DL7( 29-JUN-2015 )"},
    {"name":"RAJA GARDEN FITNESS CENTER","code":"DL204","value":"204","full_text":"RAJA GARDEN FITNESS CENTER - DL204( 18-JAN-2017 )"},
    {"name":"RAJOURI GARDEN","code":"DL10","value":"10","full_text":"RAJOURI GARDEN - DL10( 12-AUG-2015 )"},
    {"name":"RAJPUR ROAD/VIU BURARI","code":"DL51","value":"51","full_text":"RAJPUR ROAD/VIU BURARI - DL51( 08-APR-2016 )"},
    {"name":"ROHINI","code":"DL11","value":"11","full_text":"ROHINI - DL11( 14-AUG-2015 )"},
    {"name":"SARAI KALE KHAN","code":"DL6","value":"6","full_text":"SARAI KALE KHAN - DL6( 10-SEP-2015 )"},
    {"name":"SHAKUR BASTI FITNESS CENTER","code":"DL202","value":"202","full_text":"SHAKUR BASTI FITNESS CENTER - DL202( 18-JAN-2017 )"},
    {"name":"SOUTH DELHI","code":"DL3","value":"3","full_text":"SOUTH DELHI - DL3( 15-SEP-2015 )"},
    {"name":"SURAJMAL VIHAR","code":"DL13","value":"13","full_text":"SURAJMAL VIHAR - DL13( 26-JUN-2015 )"},
    {"name":"VASANT VIHAR","code":"DL12","value":"12","full_text":"VASANT VIHAR - DL12( 01-JUN-2015 )"},
    {"name":"VISHWAS NAGAR FITNESS CENTER","code":"DL203","value":"203","full_text":"VISHWAS NAGAR FITNESS CENTER - DL203( 18-JAN-2017 )"},
    {"name":"WAZIRPUR","code":"DL8","value":"8","full_text":"WAZIRPUR - DL8( 17-SEP-2015 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Goa
# ──────────────────────────────────────────────────────────────────────────────
STATE_GA = {
  "state": "Goa",
  "state_code": "GA",
  "extraction_date": "2025-07-29T13:49:06.857938",
  "total_rtos": 14,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(13/13)"},
    {"name":"ASSISTANT DIRECTOR OF TRANSPORT ENF. (NORTH) PANAJI","code":"GA107","value":"107","full_text":"ASSISTANT DIRECTOR OF TRANSPORT ENF. (NORTH) PANAJI - GA107( 25-JAN-2021 )"},
    {"name":"ASSISTANT DIRECTOR OF TRANSPORT ENF. (SOUTH) MARGAO","code":"GA108","value":"108","full_text":"ASSISTANT DIRECTOR OF TRANSPORT ENF. (SOUTH) MARGAO - GA108( 08-MAR-2021 )"},
    {"name":"BICHOLIM RTO","code":"GA4","value":"4","full_text":"BICHOLIM RTO - GA4( 04-SEP-2017 )"},
    {"name":"CANACONA RTO","code":"GA10","value":"10","full_text":"CANACONA RTO - GA10( 04-OCT-2017 )"},
    {"name":"DHARBANDORA RTO","code":"GA12","value":"12","full_text":"DHARBANDORA RTO - GA12( 18-SEP-2017 )"},
    {"name":"MAPUSA RTO","code":"GA3","value":"3","full_text":"MAPUSA RTO - GA3( 18-SEP-2017 )"},
    {"name":"MARGAO RTO","code":"GA8","value":"8","full_text":"MARGAO RTO - GA8( 04-OCT-2017 )"},
    {"name":"PANAJI RTO","code":"GA7","value":"7","full_text":"PANAJI RTO - GA7( 03-JUL-2017 )"},
    {"name":"PERNEM RTO","code":"GA11","value":"11","full_text":"PERNEM RTO - GA11( 04-SEP-2017 )"},
    {"name":"PONDA RTO","code":"GA5","value":"5","full_text":"PONDA RTO - GA5( 11-SEP-2017 )"},
    {"name":"QUEPEM RTO","code":"GA9","value":"9","full_text":"QUEPEM RTO - GA9( 18-SEP-2017 )"},
    {"name":"STATE TRANSPORT AUTHORITY, GOA","code":"GA999","value":"999","full_text":"STATE TRANSPORT AUTHORITY, GOA - GA999( 01-JUN-2021 )"},
    {"name":"VASCO RTO","code":"GA6","value":"6","full_text":"VASCO RTO - GA6( 11-SEP-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Gujarat
# ──────────────────────────────────────────────────────────────────────────────
STATE_GJ = {
  "state": "Gujarat",
  "state_code": "GJ",
  "extraction_date": "2025-07-29T13:51:04.344947",
  "total_rtos": 38,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(37/37)"},
    {"name":"AAHWA","code":"GJ30","value":"30","full_text":"AAHWA - GJ30( 17-MAR-2017 )"},
    {"name":"AHMEDABAD","code":"GJ1","value":"1","full_text":"AHMEDABAD - GJ1( 22-MAY-2017 )"},
    {"name":"AHMEDABAD EAST","code":"GJ27","value":"27","full_text":"AHMEDABAD EAST - GJ27( 16-MAY-2017 )"},
    {"name":"Ahmedabad (Rural), Bawla ARTO","code":"GJ38","value":"38","full_text":"Ahmedabad (Rural), Bawla ARTO - GJ38( 29-APR-2017 )"},
    {"name":"AMRELI","code":"GJ14","value":"14","full_text":"AMRELI - GJ14( 16-MAY-2017 )"},
    {"name":"ANAND","code":"GJ23","value":"23","full_text":"ANAND - GJ23( 21-FEB-2017 )"},
    {"name":"BANASKANTHA","code":"GJ8","value":"8","full_text":"BANASKANTHA - GJ8( 09-MAY-2017 )"},
    {"name":"BARDOLI","code":"GJ19","value":"19","full_text":"BARDOLI - GJ19( 25-APR-2017 )"},
    {"name":"BHARUCH","code":"GJ16","value":"16","full_text":"BHARUCH - GJ16( 09-MAY-2017 )"},
    {"name":"BHAVNAGAR","code":"GJ4","value":"4","full_text":"BHAVNAGAR - GJ4( 16-MAY-2017 )"},
    {"name":"BOTAD","code":"GJ33","value":"33","full_text":"BOTAD - GJ33( 21-MAR-2017 )"},
    {"name":"CHHOTAUDAIPUR","code":"GJ34","value":"34","full_text":"CHHOTAUDAIPUR - GJ34( 17-MAR-2017 )"},
    {"name":"DAHOD","code":"GJ20","value":"20","full_text":"DAHOD - GJ20( 09-MAY-2017 )"},
    {"name":"GANDHINAGAR","code":"GJ18","value":"18","full_text":"GANDHINAGAR - GJ18( 21-MAR-2017 )"},
    {"name":"JAMNAGAR","code":"GJ10","value":"10","full_text":"JAMNAGAR - GJ10( 25-APR-2017 )"},
    {"name":"JUNAGADH","code":"GJ11","value":"11","full_text":"JUNAGADH - GJ11( 25-APR-2017 )"},
    {"name":"KACHCHH","code":"GJ12","value":"12","full_text":"KACHCHH - GJ12( 24-JUL-2017 )"},
    {"name":"KACHCHH EAST","code":"GJ39","value":"39","full_text":"KACHCHH EAST - GJ39( 12-SEP-2022 )"},
    {"name":"KHAMBHALIYA","code":"GJ37","value":"37","full_text":"KHAMBHALIYA - GJ37( 25-APR-2017 )"},
    {"name":"KHEDA","code":"GJ7","value":"7","full_text":"KHEDA - GJ7( 17-MAR-2017 )"},
    {"name":"LUNAVADA","code":"GJ35","value":"35","full_text":"LUNAVADA - GJ35( 25-APR-2017 )"},
    {"name":"MEHSANA","code":"GJ2","value":"2","full_text":"MEHSANA - GJ2( 21-MAR-2017 )"},
    {"name":"MODASA","code":"GJ31","value":"31","full_text":"MODASA - GJ31( 17-MAR-2017 )"},
    {"name":"MORBI","code":"GJ36","value":"36","full_text":"MORBI - GJ36( 25-APR-2017 )"},
    {"name":"NARMADA","code":"GJ22","value":"22","full_text":"NARMADA - GJ22( 25-APR-2017 )"},
    {"name":"NAVSARI","code":"GJ21","value":"21","full_text":"NAVSARI - GJ21( 25-APR-2017 )"},
    {"name":"PANCHMAHAL","code":"GJ17","value":"17","full_text":"PANCHMAHAL - GJ17( 16-MAY-2017 )"},
    {"name":"PATAN","code":"GJ24","value":"24","full_text":"PATAN - GJ24( 21-MAR-2017 )"},
    {"name":"PORBANDAR","code":"GJ25","value":"25","full_text":"PORBANDAR - GJ25( 25-APR-2017 )"},
    {"name":"RAJKOT","code":"GJ3","value":"3","full_text":"RAJKOT - GJ3( 13-JUL-2017 )"},
    {"name":"SABARKANTHA","code":"GJ9","value":"9","full_text":"SABARKANTHA - GJ9( 09-MAY-2017 )"},
    {"name":"SURAT","code":"GJ5","value":"5","full_text":"SURAT - GJ5( 24-JUL-2017 )"},
    {"name":"SURENDRANAGAR","code":"GJ13","value":"13","full_text":"SURENDRANAGAR - GJ13( 16-MAY-2017 )"},
    {"name":"TAPI","code":"GJ26","value":"26","full_text":"TAPI - GJ26( 25-APR-2017 )"},
    {"name":"VADODARA","code":"GJ6","value":"6","full_text":"VADODARA - GJ6( 13-JUL-2017 )"},
    {"name":"VALSAD","code":"GJ15","value":"15","full_text":"VALSAD - GJ15( 09-MAY-2017 )"},
    {"name":"VERAVAL","code":"GJ32","value":"32","full_text":"VERAVAL - GJ32( 21-MAR-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# West Bengal
# ──────────────────────────────────────────────────────────────────────────────
STATE_WB = {
  "state": "West Bengal",
  "state_code": "WB",
  "extraction_date": "2025-07-29T14:48:36.120399",
  "total_rtos": 60,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(59/59)"},
    {"name":"ALIPORE RTO","code":"WB19","value":"19","full_text":"ALIPORE RTO - WB19( 13-DEC-2016 )"},
    {"name":"ALIPURDUAR RTO","code":"WB69","value":"69","full_text":"ALIPURDUAR RTO - WB69( 22-FEB-2017 )"},
    {"name":"ARAMBAG ARTO","code":"WB18","value":"18","full_text":"ARAMBAG ARTO - WB18( 10-JAN-2017 )"},
    {"name":"BANGAON ARTO","code":"WB27","value":"27","full_text":"BANGAON ARTO - WB27( 17-JAN-2017 )"},
    {"name":"BANKURA RTO","code":"WB67","value":"67","full_text":"BANKURA RTO - WB67( 11-APR-2017 )"},
    {"name":"BARASAT RTO","code":"WB25","value":"25","full_text":"BARASAT RTO - WB25( 17-JAN-2017 )"},
    {"name":"BARRACKPORE ARTO","code":"WB23","value":"23","full_text":"BARRACKPORE ARTO - WB23( 27-DEC-2016 )"},
    {"name":"BARUIPUR ARTO","code":"WB95","value":"95","full_text":"BARUIPUR ARTO - WB95( 31-JAN-2017 )"},
    {"name":"BASIRHAT ARTO","code":"WB21","value":"21","full_text":"BASIRHAT ARTO - WB21( 17-JAN-2017 )"},
    {"name":"BEHALA ARTO","code":"WB9","value":"9","full_text":"BEHALA ARTO - WB9( 27-DEC-2017 )"},
    {"name":"BIRBHUM RTO","code":"WB53","value":"53","full_text":"BIRBHUM RTO - WB53( 28-FEB-2017 )"},
    {"name":"BISHNUPUR ARTO","code":"WB87","value":"87","full_text":"BISHNUPUR ARTO - WB87( 11-APR-2017 )"},
    {"name":"BOLPUR ARTO","code":"WB47","value":"47","full_text":"BOLPUR ARTO - WB47( 28-FEB-2017 )"},
    {"name":"BUNIADPUR ARTO","code":"null62","value":"62","full_text":"BUNIADPUR ARTO - null62( 19-MAY-2025 )"},
    {"name":"CANNING ARTO","code":"null98","value":"98","full_text":"CANNING ARTO - null98( 19-MAY-2025 )"},
    {"name":"CHANCHOL ARTO","code":"WB83","value":"83","full_text":"CHANCHOL ARTO - WB83( 23-MAR-2017 )"},
    {"name":"CONTAI ARTO","code":"WB31","value":"31","full_text":"CONTAI ARTO - WB31( 09-FEB-2017 )"},
    {"name":"COOCHBEHAR RTO","code":"WB63","value":"63","full_text":"COOCHBEHAR RTO - WB63( 28-MAR-2017 )"},
    {"name":"DAKSHIN DINAJPUR RTO","code":"WB61","value":"61","full_text":"DAKSHIN DINAJPUR RTO - WB61( 06-APR-2017 )"},
    {"name":"DARJEELING RTO","code":"WB76","value":"76","full_text":"DARJEELING RTO - WB76( 30-MAR-2017 )"},
    {"name":"DIAMOND HARBOUR ARTO","code":"WB97","value":"97","full_text":"DIAMOND HARBOUR ARTO - WB97( 31-JAN-2017 )"},
    {"name":"DURGAPORE ARTO","code":"WB39","value":"39","full_text":"DURGAPORE ARTO - WB39( 21-FEB-2017 )"},
    {"name":"GHATAL ARTO","code":"WB50","value":"50","full_text":"GHATAL ARTO - WB50( 07-MAR-2017 )"},
    {"name":"HALDIA ARTO","code":"WB32","value":"32","full_text":"HALDIA ARTO - WB32( 10-JUL-2017 )"},
    {"name":"HOOGHLY RTO","code":"WB15","value":"15","full_text":"HOOGHLY RTO - WB15( 10-JAN-2017 )"},
    {"name":"HOWRAH RTO","code":"WB11","value":"11","full_text":"HOWRAH RTO - WB11( 20-DEC-2016 )"},
    {"name":"ISLAMPUR ARTO","code":"WB91","value":"91","full_text":"ISLAMPUR ARTO - WB91( 28-MAR-2017 )"},
    {"name":"JALPAIGURI RTO","code":"WB71","value":"71","full_text":"JALPAIGURI RTO - WB71( 21-FEB-2017 )"},
    {"name":"JANGIPUR ARTO","code":"WB93","value":"93","full_text":"JANGIPUR ARTO - WB93( 16-MAR-2017 )"},
    {"name":"JHARGRAM RTO","code":"WB49","value":"49","full_text":"JHARGRAM RTO - WB49( 07-MAR-2017 )"},
    {"name":"KALIMPONG RTO","code":"WB78","value":"78","full_text":"KALIMPONG RTO - WB78( 30-MAR-2017 )"},
    {"name":"KALNA ARTO","code":"WB43","value":"43","full_text":"KALNA ARTO - WB43( 21-FEB-2017 )"},
    {"name":"KALYANI ARTO","code":"WB89","value":"89","full_text":"KALYANI ARTO - WB89( 16-MAR-2017 )"},
    {"name":"KANDI","code":"WB99","value":"99","full_text":"KANDI - WB99( 11-JUL-2024 )"},
    {"name":"KASBA ARTO","code":"WB5","value":"5","full_text":"KASBA ARTO - WB5( 28-SEP-2016 )"},
    {"name":"KATWA ARTO","code":"WB75","value":"75","full_text":"KATWA ARTO - WB75( 04-SEP-2018 )"},
    {"name":"KHARAGPUR ARTO","code":"WB35","value":"35","full_text":"KHARAGPUR ARTO - WB35( 07-MAR-2017 )"},
    {"name":"MALDA RTO","code":"WB65","value":"65","full_text":"MALDA RTO - WB65( 21-MAR-2017 )"},
    {"name":"MANBAZAR","code":"WB80","value":"80","full_text":"MANBAZAR - WB80( 09-JUN-2023 )"},
    {"name":"MATHABHANGA ARTO","code":"WB85","value":"85","full_text":"MATHABHANGA ARTO - WB85( 28-MAR-2017 )"},
    {"name":"MURSHIDABAD RTO","code":"WB57","value":"57","full_text":"MURSHIDABAD RTO - WB57( 23-MAR-2017 )"},
    {"name":"NADIA RTO","code":"WB51","value":"51","full_text":"NADIA RTO - WB51( 06-APR-2017 )"},
    {"name":"PASCHIM BURDWAN RTO","code":"WB37","value":"37","full_text":"PASCHIM BURDWAN RTO - WB37( 04-APR-2017 )"},
    {"name":"PASCHIM MIDNAPORE RTO","code":"WB33","value":"33","full_text":"PASCHIM MIDNAPORE RTO - WB33( 07-MAR-2017 )"},
    {"name":"PURBA BURDWAN RTO","code":"WB41","value":"41","full_text":"PURBA BURDWAN RTO - WB41( 21-FEB-2017 )"},
    {"name":"PURULIA RTO","code":"WB55","value":"55","full_text":"PURULIA RTO - WB55( 16-FEB-2017 )"},
    {"name":"PVD KOLKATA","code":"WB1","value":"1","full_text":"PVD KOLKATA - WB1( 25-JAN-2017 )"},
    {"name":"RAGHUNATHPUR ARTO","code":"WB81","value":"81","full_text":"RAGHUNATHPUR ARTO - WB81( 16-FEB-2017 )"},
    {"name":"RAMPURHAT ARTO","code":"WB45","value":"45","full_text":"RAMPURHAT ARTO - WB45( 28-FEB-2017 )"},
    {"name":"SALTLAKE ARTO","code":"WB7","value":"7","full_text":"SALTLAKE ARTO - WB7( 03-JAN-2017 )"},
    {"name":"SILIGURI ARTO","code":"WB73","value":"73","full_text":"SILIGURI ARTO - WB73( 30-MAR-2017 )"},
    {"name":"SRIRAMPUR ARTO","code":"WB17","value":"17","full_text":"SRIRAMPUR ARTO - WB17( 10-JAN-2017 )"},
    {"name":"STA-Durgapur","code":"WB997","value":"997","full_text":"STA-Durgapur - WB997( 08-MAR-2019 )"},
    {"name":"STA-North Bengal (Siliguri)","code":"WB998","value":"998","full_text":"STA-North Bengal (Siliguri) - WB998( 13-MAR-2019 )"},
    {"name":"STA WEST BENGAL","code":"WB999","value":"999","full_text":"STA WEST BENGAL - WB999( 08-AUG-2018 )"},
    {"name":"TAMLUK RTO","code":"WB29","value":"29","full_text":"TAMLUK RTO - WB29( 09-FEB-2017 )"},
    {"name":"TEHATTA ARTO","code":"WB52","value":"52","full_text":"TEHATTA ARTO - WB52( 08-JUL-2020 )"},
    {"name":"ULUBERIA ARTO","code":"WB13","value":"13","full_text":"ULUBERIA ARTO - WB13( 25-JAN-2017 )"},
    {"name":"UTTAR DINAJPUR RTO","code":"WB59","value":"59","full_text":"UTTAR DINAJPUR RTO - WB59( 04-APR-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Bihar
# ──────────────────────────────────────────────────────────────────────────────
STATE_BR = {
  "state": "Bihar",
  "state_code": "BR",
  "extraction_date": "2025-07-29T13:42:19.603107",
  "total_rtos": 50,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(48/48)"},
    {"name":"ARARIA","code":"BR38","value":"38","full_text":"ARARIA - BR38( 30-JAN-2018 )"},
    {"name":"ARAWAL","code":"BR56","value":"56","full_text":"ARAWAL - BR56( 22-MAY-2017 )"},
    {"name":"AURANGABAD","code":"BR26","value":"26","full_text":"AURANGABAD - BR26( 13-JUN-2017 )"},
    {"name":"BANKA","code":"BR51","value":"51","full_text":"BANKA - BR51( 06-FEB-2018 )"},
    {"name":"BEGUSARAI","code":"BR9","value":"9","full_text":"BEGUSARAI - BR9( 23-JAN-2018 )"},
    {"name":"BETTIAH","code":"BR22","value":"22","full_text":"BETTIAH - BR22( 22-SEP-2017 )"},
    {"name":"BHABHUA","code":"BR45","value":"45","full_text":"BHABHUA - BR45( 23-JAN-2018 )"},
    {"name":"BHAGALPUR","code":"BR10","value":"10","full_text":"BHAGALPUR - BR10( 07-FEB-2018 )"},
    {"name":"BHAGALPUR RTA","code":"BR103","value":"103","full_text":"BHAGALPUR RTA - BR103( 13-DEC-2018 )"},
    {"name":"BHOJPUR","code":"BR3","value":"3","full_text":"BHOJPUR - BR3( 15-FEB-2018 )"},
    {"name":"BUXUR","code":"BR44","value":"44","full_text":"BUXUR - BR44( 01-FEB-2018 )"},
    {"name":"CHAPARA","code":"BR4","value":"4","full_text":"CHAPARA - BR4( 29-JAN-2018 )"},
    {"name":"CHAPRA RTA","code":"BR109","value":"109","full_text":"CHAPRA RTA - BR109( 13-DEC-2018 )"},
    {"name":"DARBHANGA","code":"BR7","value":"7","full_text":"DARBHANGA - BR7( 30-JAN-2018 )"},
    {"name":"DARBHANGA RTA","code":"BR102","value":"102","full_text":"DARBHANGA RTA - BR102( 13-DEC-2018 )"},
    {"name":"GAYA","code":"BR2","value":"2","full_text":"GAYA - BR2( 06-SEP-2017 )"},
    {"name":"GAYA RTA","code":"BR107","value":"107","full_text":"GAYA RTA - BR107( 13-DEC-2018 )"},
    {"name":"GOPALGANJ","code":"BR28","value":"28","full_text":"GOPALGANJ - BR28( 08-JUN-2017 )"},
    {"name":"JAMUI","code":"BR46","value":"46","full_text":"JAMUI - BR46( 07-JUN-2017 )"},
    {"name":"JEHANABAD","code":"BR25","value":"25","full_text":"JEHANABAD - BR25( 26-MAY-2017 )"},
    {"name":"KATIHAR","code":"BR39","value":"39","full_text":"KATIHAR - BR39( 23-JAN-2018 )"},
    {"name":"KHAGARIA","code":"BR34","value":"34","full_text":"KHAGARIA - BR34( 01-FEB-2018 )"},
    {"name":"KISHANGANJ","code":"BR37","value":"37","full_text":"KISHANGANJ - BR37( 07-FEB-2018 )"},
    {"name":"LAKHISARAI","code":"BR53","value":"53","full_text":"LAKHISARAI - BR53( 27-JAN-2017 )"},
    {"name":"MADHEPURA","code":"BR43","value":"43","full_text":"MADHEPURA - BR43( 02-JUN-2017 )"},
    {"name":"MADHUBANI","code":"BR32","value":"32","full_text":"MADHUBANI - BR32( 01-FEB-2018 )"},
    {"name":"MOTIHARI","code":"BR5","value":"5","full_text":"MOTIHARI - BR5( 05-JUL-2017 )"},
    {"name":"M/S MURARI AUTO,Patna","code":"BR201","value":"201","full_text":"M/S MURARI AUTO,Patna - BR201( 19-DEC-2019 )"},
    {"name":"MUNGER","code":"BR8","value":"8","full_text":"MUNGER - BR8( 06-FEB-2018 )"},
    {"name":"MUNGER RTA","code":"BR104","value":"104","full_text":"MUNGER RTA - BR104( 13-DEC-2018 )"},
    {"name":"MUZAFFARPUR","code":"BR6","value":"6","full_text":"MUZAFFARPUR - BR6( 01-FEB-2018 )"},
    {"name":"MUZAFFARPUR RTA","code":"BR106","value":"106","full_text":"MUZAFFARPUR RTA - BR106( 13-DEC-2018 )"},
    {"name":"NALANDA","code":"BR21","value":"21","full_text":"NALANDA - BR21( 01-FEB-2018 )"},
    {"name":"NAWADA","code":"BR27","value":"27","full_text":"NAWADA - BR27( 30-JAN-2018 )"},
    {"name":"PATNA","code":"BR1","value":"1","full_text":"PATNA - BR1( 02-FEB-2018 )"},
    {"name":"PATNA RTA","code":"BR101","value":"101","full_text":"PATNA RTA - BR101( 13-DEC-2018 )"},
    {"name":"PURNEA","code":"BR11","value":"11","full_text":"PURNEA - BR11( 23-JAN-2018 )"},
    {"name":"PURNEA RTA","code":"BR108","value":"108","full_text":"PURNEA RTA - BR108( 13-DEC-2018 )"},
    {"name":"ROHTAS","code":"BR24","value":"24","full_text":"ROHTAS - BR24( 09-FEB-2018 )"},
    {"name":"SAHARSA","code":"BR19","value":"19","full_text":"SAHARSA - BR19( 29-JAN-2018 )"},
    {"name":"SAHARSA RTA","code":"BR105","value":"105","full_text":"SAHARSA RTA - BR105( 13-DEC-2018 )"},
    {"name":"SAMASTIPUR","code":"BR33","value":"33","full_text":"SAMASTIPUR - BR33( 06-JUL-2017 )"},
    {"name":"SHEIKHPURA","code":"BR52","value":"52","full_text":"SHEIKHPURA - BR52( 17-JUL-2017 )"},
    {"name":"SHEOHAR","code":"BR55","value":"55","full_text":"SHEOHAR - BR55( 07-JUN-2017 )"},
    {"name":"SITAMARHI","code":"BR30","value":"30","full_text":"SITAMARHI - BR30( 29-JAN-2018 )"},
    {"name":"SIWAN","code":"BR29","value":"29","full_text":"SIWAN - BR29( 29-JAN-2018 )"},
    {"name":"STA BIHAR","code":"BR999","value":"999","full_text":"STA BIHAR - BR999( 20-NOV-2019 )"},
    {"name":"SUPAUL","code":"BR50","value":"50","full_text":"SUPAUL - BR50( 29-JAN-2018 )"},
    {"name":"VAISHALI","code":"BR31","value":"31","full_text":"VAISHALI - BR31( 13-FEB-2018 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Chhattisgarh
# ──────────────────────────────────────────────────────────────────────────────
STATE_CG = {
  "state": "Chhattisgarh",
  "state_code": "CG",
  "extraction_date": "2025-07-29T13:44:08.606443",
  "total_rtos": 32,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(31/31)"},
    {"name":"AIG(F/P) PHQ","code":"CG3","value":"3","full_text":"AIG(F/P) PHQ - CG3( 22-APR-2025 )"},
    {"name":"Ambikapur RTO","code":"CG15","value":"15","full_text":"Ambikapur RTO - CG15( 27-DEC-2018 )"},
    {"name":"BAIKUNTHPUR DTO","code":"CG16","value":"16","full_text":"BAIKUNTHPUR DTO - CG16( 20-DEC-2018 )"},
    {"name":"Baloda Bazar DTO","code":"CG22","value":"22","full_text":"Baloda Bazar DTO - CG22( 20-SEP-2018 )"},
    {"name":"Balod DTO","code":"CG24","value":"24","full_text":"Balod DTO - CG24( 04-SEP-2018 )"},
    {"name":"Balrampur DTO","code":"CG30","value":"30","full_text":"Balrampur DTO - CG30( 21-DEC-2018 )"},
    {"name":"Bemetara DTO","code":"CG25","value":"25","full_text":"Bemetara DTO - CG25( 20-SEP-2018 )"},
    {"name":"Bijapur DTO","code":"CG20","value":"20","full_text":"Bijapur DTO - CG20( 07-AUG-2018 )"},
    {"name":"Bilaspur RTO","code":"CG10","value":"10","full_text":"Bilaspur RTO - CG10( 29-AUG-2018 )"},
    {"name":"Dantewada DTO","code":"CG18","value":"18","full_text":"Dantewada DTO - CG18( 27-AUG-2018 )"},
    {"name":"Dhamtari DTO","code":"CG5","value":"5","full_text":"Dhamtari DTO - CG5( 31-AUG-2018 )"},
    {"name":"DURG RTO","code":"CG7","value":"7","full_text":"DURG RTO - CG7( 01-OCT-2018 )"},
    {"name":"Gariyaband DTO","code":"CG23","value":"23","full_text":"Gariyaband DTO - CG23( 04-SEP-2018 )"},
    {"name":"Gaurela-Pendra-Marwahi DTO","code":"CG31","value":"31","full_text":"Gaurela-Pendra-Marwahi DTO - CG31( 09-APR-2021 )"},
    {"name":"JAGDALPUR RTO","code":"CG17","value":"17","full_text":"JAGDALPUR RTO - CG17( 01-OCT-2018 )"},
    {"name":"Janjgir Champa DTO","code":"CG11","value":"11","full_text":"Janjgir Champa DTO - CG11( 27-AUG-2018 )"},
    {"name":"Jashpur DTO","code":"CG14","value":"14","full_text":"Jashpur DTO - CG14( 21-DEC-2018 )"},
    {"name":"KANKER DTO","code":"CG19","value":"19","full_text":"KANKER DTO - CG19( 22-SEP-2018 )"},
    {"name":"KAWARDHA DTO","code":"CG9","value":"9","full_text":"KAWARDHA DTO - CG9( 20-SEP-2018 )"},
    {"name":"KONDAGAON DTO","code":"CG27","value":"27","full_text":"KONDAGAON DTO - CG27( 22-SEP-2018 )"},
    {"name":"Korba DTO","code":"CG12","value":"12","full_text":"Korba DTO - CG12( 25-AUG-2018 )"},
    {"name":"Mahasamund DTO","code":"CG6","value":"6","full_text":"Mahasamund DTO - CG6( 27-MAR-2018 )"},
    {"name":"Mungeli DTO","code":"CG28","value":"28","full_text":"Mungeli DTO - CG28( 27-JUL-2018 )"},
    {"name":"Narayanpur DTO","code":"CG21","value":"21","full_text":"Narayanpur DTO - CG21( 07-AUG-2018 )"},
    {"name":"Raigarh DTO","code":"CG13","value":"13","full_text":"Raigarh DTO - CG13( 27-AUG-2018 )"},
    {"name":"Raipur RTO","code":"CG4","value":"4","full_text":"Raipur RTO - CG4( 28-SEP-2018 )"},
    {"name":"Rajnandgaon ARTO","code":"CG8","value":"8","full_text":"Rajnandgaon ARTO - CG8( 30-AUG-2018 )"},
    {"name":"RTA TC NAWA RAIPUR","code":"CG998","value":"998","full_text":"RTA TC NAWA RAIPUR - CG998( 06-JUL-2020 )"},
    {"name":"State Transport Authority","code":"CG99","value":"99","full_text":"State Transport Authority - CG99( 01-JAN-2019 )"},
    {"name":"Sukma DTO","code":"CG26","value":"26","full_text":"Sukma DTO - CG26( 04-SEP-2018 )"},
    {"name":"Surajpur DTO","code":"CG29","value":"29","full_text":"Surajpur DTO - CG29( 20-DEC-2018 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# UT of DNH and DD
# ──────────────────────────────────────────────────────────────────────────────
STATE_UT = {
  "state": "UT of DNH and DD",
  "state_code": "UT",
  "extraction_date": "2025-07-29T13:46:11.957625",
  "total_rtos": 4,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(3/3)"},
    {"name":"DAMAN","code":"DD3","value":"3","full_text":"DAMAN - DD3( 14-DEC-2017 )"},
    {"name":"DIU","code":"DD2","value":"2","full_text":"DIU - DD2( 14-DEC-2017 )"},
    {"name":"SILVASSA","code":"DD1","value":"1","full_text":"SILVASSA - DD1( 20-DEC-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Odisha
# ──────────────────────────────────────────────────────────────────────────────
STATE_OD = {
  "state": "Odisha",
  "state_code": "OD",
  "extraction_date": "2025-07-29T14:24:35.944500",
  "total_rtos": 40,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(39/39)"},
    {"name":"ANGUL RTO","code":"OD19","value":"19","full_text":"ANGUL RTO - OD19( 25-DEC-2017 )"},
    {"name":"ARTO BARBIL","code":"OD901","value":"901","full_text":"ARTO BARBIL - OD901( 04-DEC-2017 )"},
    {"name":"BALASORE RTO","code":"OD1","value":"1","full_text":"BALASORE RTO - OD1( 07-NOV-2017 )"},
    {"name":"BARGARH RTO","code":"OD17","value":"17","full_text":"BARGARH RTO - OD17( 04-DEC-2017 )"},
    {"name":"BHADRAK RTO","code":"OD22","value":"22","full_text":"BHADRAK RTO - OD22( 04-DEC-2017 )"},
    {"name":"BHANJANAGAR RTO","code":"OD32","value":"32","full_text":"BHANJANAGAR RTO - OD32( 04-DEC-2017 )"},
    {"name":"BHUBANESWAR-II RTO","code":"OD33","value":"33","full_text":"BHUBANESWAR-II RTO - OD33( 23-OCT-2017 )"},
    {"name":"BHUBANESWAR RTO","code":"OD2","value":"2","full_text":"BHUBANESWAR RTO - OD2( 22-JAN-2018 )"},
    {"name":"BOLANGIR RTO","code":"OD3","value":"3","full_text":"BOLANGIR RTO - OD3( 25-DEC-2017 )"},
    {"name":"BOUDH RTO","code":"OD27","value":"27","full_text":"BOUDH RTO - OD27( 23-OCT-2017 )"},
    {"name":"CHANDIKHOLE RTO","code":"OD4","value":"4","full_text":"CHANDIKHOLE RTO - OD4( 23-OCT-2017 )"},
    {"name":"CUTTACK RTO","code":"OD5","value":"5","full_text":"CUTTACK RTO - OD5( 31-MAY-2017 )"},
    {"name":"DEOGARH RTO","code":"OD28","value":"28","full_text":"DEOGARH RTO - OD28( 23-OCT-2017 )"},
    {"name":"DHENKANAL RTO","code":"OD6","value":"6","full_text":"DHENKANAL RTO - OD6( 07-NOV-2017 )"},
    {"name":"GAJAPATI RTO","code":"OD20","value":"20","full_text":"GAJAPATI RTO - OD20( 07-NOV-2017 )"},
    {"name":"GANJAM RTO","code":"OD7","value":"7","full_text":"GANJAM RTO - OD7( 04-DEC-2017 )"},
    {"name":"JAGATSINGHPUR RTO","code":"OD21","value":"21","full_text":"JAGATSINGHPUR RTO - OD21( 04-DEC-2017 )"},
    {"name":"JAJPUR RTO","code":"OD34","value":"34","full_text":"JAJPUR RTO - OD34( 23-OCT-2017 )"},
    {"name":"JHARSUGUDA RTO","code":"OD23","value":"23","full_text":"JHARSUGUDA RTO - OD23( 07-NOV-2017 )"},
    {"name":"KALAHANDI RTO","code":"OD8","value":"8","full_text":"KALAHANDI RTO - OD8( 23-OCT-2017 )"},
    {"name":"KENDRAPARA RTO","code":"OD29","value":"29","full_text":"KENDRAPARA RTO - OD29( 23-OCT-2017 )"},
    {"name":"KEONJHAR RTO","code":"OD9","value":"9","full_text":"KEONJHAR RTO - OD9( 04-DEC-2017 )"},
    {"name":"KHORDHA ARTO","code":"OD201","value":"201","full_text":"KHORDHA ARTO - OD201( 20-JAN-2018 )"},
    {"name":"KORAPUT RTO","code":"OD10","value":"10","full_text":"KORAPUT RTO - OD10( 25-DEC-2017 )"},
    {"name":"MALKANAGIRI RTO","code":"OD30","value":"30","full_text":"MALKANAGIRI RTO - OD30( 25-DEC-2017 )"},
    {"name":"MAYURBHANJ RTO","code":"OD11","value":"11","full_text":"MAYURBHANJ RTO - OD11( 08-NOV-2017 )"},
    {"name":"NAWARANGPUR RTO","code":"OD24","value":"24","full_text":"NAWARANGPUR RTO - OD24( 07-NOV-2017 )"},
    {"name":"NAYAGARH RTO","code":"OD25","value":"25","full_text":"NAYAGARH RTO - OD25( 25-DEC-2017 )"},
    {"name":"NUAPADA RTO","code":"OD26","value":"26","full_text":"NUAPADA RTO - OD26( 06-NOV-2017 )"},
    {"name":"PHULBANI RTO","code":"OD12","value":"12","full_text":"PHULBANI RTO - OD12( 23-OCT-2017 )"},
    {"name":"PURI RTO","code":"OD13","value":"13","full_text":"PURI RTO - OD13( 25-DEC-2017 )"},
    {"name":"RAIRANGPUR ARTO","code":"OD111","value":"111","full_text":"RAIRANGPUR ARTO - OD111( 08-NOV-2017 )"},
    {"name":"RAYGADA RTO","code":"OD18","value":"18","full_text":"RAYGADA RTO - OD18( 25-DEC-2017 )"},
    {"name":"ROURKELA RTO","code":"OD14","value":"14","full_text":"ROURKELA RTO - OD14( 25-DEC-2017 )"},
    {"name":"SAMBALPUR RTO","code":"OD15","value":"15","full_text":"SAMBALPUR RTO - OD15( 04-DEC-2017 )"},
    {"name":"SONEPUR RTO","code":"OD31","value":"31","full_text":"SONEPUR RTO - OD31( 08-NOV-2017 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"OD99","value":"99","full_text":"STATE TRANSPORT AUTHORITY - OD99( 24-APR-2018 )"},
    {"name":"SUNDERGARH RTO","code":"OD16","value":"16","full_text":"SUNDERGARH RTO - OD16( 08-NOV-2017 )"},
    {"name":"TALCHER RTO","code":"OD35","value":"35","full_text":"TALCHER RTO - OD35( 25-DEC-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Maharashtra
# ──────────────────────────────────────────────────────────────────────────────
STATE_MH = {
  "state": "Maharashtra",
  "state_code": "MH",
  "extraction_date": "2025-07-29T14:15:06.849762",
  "total_rtos": 62,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(59/59)"},
    {"name":"AKLUJ","code":"MH45","value":"45","full_text":"AKLUJ - MH45( 03-APR-2017 )"},
    {"name":"AMBEJOGAI","code":"MH44","value":"44","full_text":"AMBEJOGAI - MH44( 02-MAY-2017 )"},
    {"name":"AMRAWATI","code":"MH27","value":"27","full_text":"AMRAWATI - MH27( 21-JAN-2017 )"},
    {"name":"BARAMATI","code":"MH42","value":"42","full_text":"BARAMATI - MH42( 10-MAR-2017 )"},
    {"name":"BEED","code":"MH23","value":"23","full_text":"BEED - MH23( 17-MAR-2017 )"},
    {"name":"BHADGAON","code":"MH54","value":"54","full_text":"BHADGAON - MH54( 20-MAR-2024 )"},
    {"name":"BHANDARA","code":"MH36","value":"36","full_text":"BHANDARA - MH36( 12-APR-2017 )"},
    {"name":"BULDHANA","code":"MH28","value":"28","full_text":"BULDHANA - MH28( 07-NOV-2017 )"},
    {"name":"CHALISGAON","code":"MH52","value":"52","full_text":"CHALISGAON - MH52( 05-MAR-2024 )"},
    {"name":"CHHATRAPATI SAMBHAJINAGAR","code":"MH20","value":"20","full_text":"CHHATRAPATI SAMBHAJINAGAR - MH20( 20-OCT-2016 )"},
    {"name":"Chiplun Chiplun Track","code":"MH202","value":"202","full_text":"Chiplun Chiplun Track - MH202( 04-DEC-2019 )"},
    {"name":"DHARASHIV","code":"MH25","value":"25","full_text":"DHARASHIV - MH25( 31-OCT-2017 )"},
    {"name":"DHULE","code":"MH18","value":"18","full_text":"DHULE - MH18( 03-JAN-2017 )"},
    {"name":"DY REGIONAL TRANSPORT OFFICE, HINGOLI","code":"MH38","value":"38","full_text":"DY REGIONAL TRANSPORT OFFICE, HINGOLI - MH38( 15-JUL-2017 )"},
    {"name":"DY RTO RATNAGIRI","code":"MH8","value":"8","full_text":"DY RTO RATNAGIRI - MH8( 10-APR-2017 )"},
    {"name":"GADCHIROLI","code":"MH33","value":"33","full_text":"GADCHIROLI - MH33( 18-APR-2017 )"},
    {"name":"GONDHIA","code":"MH35","value":"35","full_text":"GONDHIA - MH35( 11-APR-2017 )"},
    {"name":"ICHALKARANJI","code":"MH51","value":"51","full_text":"ICHALKARANJI - MH51( 07-MAR-2024 )"},
    {"name":"JALANA","code":"MH21","value":"21","full_text":"JALANA - MH21( 03-AUG-2017 )"},
    {"name":"KALYAN","code":"MH5","value":"5","full_text":"KALYAN - MH5( 11-MAY-2017 )"},
    {"name":"KARAD","code":"MH50","value":"50","full_text":"KARAD - MH50( 20-MAR-2017 )"},
    {"name":"KHAMGAON","code":"MH56","value":"56","full_text":"KHAMGAON - MH56( 15-APR-2025 )"},
    {"name":"KOLHAPUR","code":"MH9","value":"9","full_text":"KOLHAPUR - MH9( 02-MAR-2017 )"},
    {"name":"MALEGAON","code":"MH41","value":"41","full_text":"MALEGAON - MH41( 23-AUG-2017 )"},
    {"name":"MIRA BHAYANDAR","code":"MH58","value":"58","full_text":"MIRA BHAYANDAR - MH58( 07-MAY-2025 )"},
    {"name":"MUMBAI (CENTRAL)","code":"MH1","value":"1","full_text":"MUMBAI (CENTRAL) - MH1( 15-DEC-2016 )"},
    {"name":"MUMBAI (EAST)","code":"MH3","value":"3","full_text":"MUMBAI (EAST) - MH3( 13-DEC-2016 )"},
    {"name":"MUMBAI (WEST)","code":"MH2","value":"2","full_text":"MUMBAI (WEST) - MH2( 21-APR-2017 )"},
    {"name":"NAGPUR (EAST)","code":"MH49","value":"49","full_text":"NAGPUR (EAST) - MH49( 17-APR-2017 )"},
    {"name":"NAGPUR (RURAL)","code":"MH40","value":"40","full_text":"NAGPUR (RURAL) - MH40( 17-JAN-2017 )"},
    {"name":"NAGPUR (U)","code":"MH31","value":"31","full_text":"NAGPUR (U) - MH31( 18-JAN-2017 )"},
    {"name":"NANDED","code":"MH26","value":"26","full_text":"NANDED - MH26( 12-JAN-2017 )"},
    {"name":"NANDURBAR","code":"MH39","value":"39","full_text":"NANDURBAR - MH39( 02-MAY-2017 )"},
    {"name":"NASHIK","code":"MH15","value":"15","full_text":"NASHIK - MH15( 05-JAN-2017 )"},
    {"name":"PANVEL","code":"MH46","value":"46","full_text":"PANVEL - MH46( 31-JAN-2017 )"},
    {"name":"PARBHANI","code":"MH22","value":"22","full_text":"PARBHANI - MH22( 25-APR-2017 )"},
    {"name":"PEN (RAIGAD)","code":"MH6","value":"6","full_text":"PEN (RAIGAD) - MH6( 16-MAY-2017 )"},
    {"name":"PHALTAN","code":"MH53","value":"53","full_text":"PHALTAN - MH53( 03-SEP-2024 )"},
    {"name":"PUNE","code":"MH12","value":"12","full_text":"PUNE - MH12( 25-JAN-2017 )"},
    {"name":"RTO AHEMEDNAGAR","code":"MH16","value":"16","full_text":"RTO AHEMEDNAGAR - MH16( 16-MAR-2017 )"},
    {"name":"RTO AKOLA","code":"MH30","value":"30","full_text":"RTO AKOLA - MH30( 20-FEB-2017 )"},
    {"name":"R.T.O.BORIVALI","code":"MH47","value":"47","full_text":"R.T.O.BORIVALI - MH47( 21-APR-2017 )"},
    {"name":"RTO CHANDRAPUR","code":"MH34","value":"34","full_text":"RTO CHANDRAPUR - MH34( 25-APR-2017 )"},
    {"name":"RTO JALGAON","code":"MH19","value":"19","full_text":"RTO JALGAON - MH19( 24-MAR-2017 )"},
    {"name":"RTO LATUR","code":"MH24","value":"24","full_text":"RTO LATUR - MH24( 15-MAR-2017 )"},
    {"name":"RTO","code":"MH04","value":"203","full_text":"RTO MH04-Mira Bhayander FitnessTrack - MH203( 01-MAY-2022 )"},
    {"name":"RTO PIMPRI CHINCHWAD","code":"MH14","value":"14","full_text":"RTO PIMPRI CHINCHWAD - MH14( 06-FEB-2017 )"},
    {"name":"RTO SATARA","code":"MH11","value":"11","full_text":"RTO SATARA - MH11( 04-MAR-2017 )"},
    {"name":"RTO SOLAPUR","code":"MH13","value":"13","full_text":"RTO SOLAPUR - MH13( 05-APR-2017 )"},
    {"name":"SANGLI","code":"MH10","value":"10","full_text":"SANGLI - MH10( 03-MAR-2017 )"},
    {"name":"SINDHUDURG(KUDAL)","code":"MH7","value":"7","full_text":"SINDHUDURG(KUDAL) - MH7( 10-APR-2017 )"},
    {"name":"SRIRAMPUR","code":"MH17","value":"17","full_text":"SRIRAMPUR - MH17( 22-MAR-2017 )"},
    {"name":"TC OFFICE","code":"MH99","value":"99","full_text":"TC OFFICE - MH99( 06-JUN-2018 )"},
    {"name":"THANE","code":"MH4","value":"4","full_text":"THANE - MH4( 08-MAR-2017 )"},
    {"name":"UDGIR","code":"MH55","value":"55","full_text":"UDGIR - MH55( 28-AUG-2024 )"},
    {"name":"VAIJAPUR","code":"MH57","value":"57","full_text":"VAIJAPUR - MH57( 06-JUN-2025 )"},
    {"name":"VASAI","code":"MH48","value":"48","full_text":"VASAI - MH48( 08-JUN-2017 )"},
    {"name":"VASHI (NEW MUMBAI)","code":"MH43","value":"43","full_text":"VASHI (NEW MUMBAI) - MH43( 07-JUL-2016 )"},
    {"name":"WARDHA","code":"MH32","value":"32","full_text":"WARDHA - MH32( 06-APR-2017 )"},
    {"name":"WASHIM","code":"MH37","value":"37","full_text":"WASHIM - MH37( 11-APR-2017 )"},
    {"name":"YAWATMAL","code":"MH29","value":"29","full_text":"YAWATMAL - MH29( 07-JUL-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Tripura
# ──────────────────────────────────────────────────────────────────────────────
STATE_TR = {
  "state": "Tripura",
  "state_code": "TR",
  "extraction_date": "2025-07-29T14:41:25.020401",
  "total_rtos": 10,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(9/9)"},
    {"name":"DHALAI DTO","code":"TR4","value":"4","full_text":"DHALAI DTO - TR4( 22-DEC-2016 )"},
    {"name":"GOMATI DTO","code":"TR3","value":"3","full_text":"GOMATI DTO - TR3( 23-FEB-2017 )"},
    {"name":"KHOWAI DTO","code":"TR6","value":"6","full_text":"KHOWAI DTO - TR6( 22-FEB-2017 )"},
    {"name":"NORTH TRIPURA DTO","code":"TR5","value":"5","full_text":"NORTH TRIPURA DTO - TR5( 03-MAR-2017 )"},
    {"name":"SEPAHIJALA DTO","code":"TR7","value":"7","full_text":"SEPAHIJALA DTO - TR7( 09-DEC-2016 )"},
    {"name":"SOUTH TRIPURA DTO","code":"TR8","value":"8","full_text":"SOUTH TRIPURA DTO - TR8( 23-FEB-2017 )"},
    {"name":"STA TRIPURA","code":"TR99","value":"99","full_text":"STA TRIPURA - TR99( 01-MAR-2017 )"},
    {"name":"UNAKOTI DTO","code":"TR2","value":"2","full_text":"UNAKOTI DTO - TR2( 03-MAR-2017 )"},
    {"name":"WEST TRIPURA JTC","code":"TR1","value":"1","full_text":"WEST TRIPURA JTC - TR1( 01-MAR-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Uttarakhand
# ──────────────────────────────────────────────────────────────────────────────
STATE_UK = {
  "state": "Uttarakhand",
  "state_code": "UK",
  "extraction_date": "2025-07-29T14:42:57.527604",
  "total_rtos": 22,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(21/21)"},
    {"name":"ALMORA RTO","code":"UK1","value":"1","full_text":"ALMORA RTO - UK1( 30-MAR-2017 )"},
    {"name":"BAGESHWAR ARTO","code":"UK2","value":"2","full_text":"BAGESHWAR ARTO - UK2( 03-MAY-2017 )"},
    {"name":"DEHRADUN RTO","code":"UK7","value":"7","full_text":"DEHRADUN RTO - UK7( 14-AUG-2015 )"},
    {"name":"HALDWANI RTO","code":"UK4","value":"4","full_text":"HALDWANI RTO - UK4( 01-AUG-2016 )"},
    {"name":"HARIDWAR ARTO","code":"UK8","value":"8","full_text":"HARIDWAR ARTO - UK8( 29-JAN-2016 )"},
    {"name":"KARANPRAYAG ARTO","code":"UK11","value":"11","full_text":"KARANPRAYAG ARTO - UK11( 18-APR-2016 )"},
    {"name":"KASHIPUR ARTO","code":"UK18","value":"18","full_text":"KASHIPUR ARTO - UK18( 30-DEC-2015 )"},
    {"name":"KOTDWAR ARTO","code":"UK15","value":"15","full_text":"KOTDWAR ARTO - UK15( 19-JAN-2016 )"},
    {"name":"PAURI RTO","code":"UK12","value":"12","full_text":"PAURI RTO - UK12( 21-APR-2016 )"},
    {"name":"PITHORAGARH ARTO","code":"UK5","value":"5","full_text":"PITHORAGARH ARTO - UK5( 28-MAR-2017 )"},
    {"name":"RAMNAGAR ARTO","code":"UK19","value":"19","full_text":"RAMNAGAR ARTO - UK19( 30-JAN-2017 )"},
    {"name":"RANIKHET ARTO","code":"UK20","value":"20","full_text":"RANIKHET ARTO - UK20( 30-JAN-2017 )"},
    {"name":"RISHIKESH ARTO","code":"UK14","value":"14","full_text":"RISHIKESH ARTO - UK14( 16-DEC-2015 )"},
    {"name":"ROORKEE ARTO","code":"UK17","value":"17","full_text":"ROORKEE ARTO - UK17( 03-OCT-2016 )"},
    {"name":"RUDRAPRAYAG ARTO","code":"UK13","value":"13","full_text":"RUDRAPRAYAG ARTO - UK13( 19-FEB-2016 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"UK111","value":"111","full_text":"STATE TRANSPORT AUTHORITY - UK111( 29-FEB-2016 )"},
    {"name":"TANAKPUR ARTO","code":"UK3","value":"3","full_text":"TANAKPUR ARTO - UK3( 01-FEB-2017 )"},
    {"name":"TEHRI ARTO","code":"UK9","value":"9","full_text":"TEHRI ARTO - UK9( 07-JUN-2016 )"},
    {"name":"UDHAM SINGH NAGAR ARTO","code":"UK6","value":"6","full_text":"UDHAM SINGH NAGAR ARTO - UK6( 29-DEC-2015 )"},
    {"name":"UTTARKASHI ARTO","code":"UK10","value":"10","full_text":"UTTARKASHI ARTO - UK10( 05-MAY-2017 )"},
    {"name":"VIKAS NAGAR ARTO","code":"UK16","value":"16","full_text":"VIKAS NAGAR ARTO - UK16( 16-MAY-2016 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Assam
# ──────────────────────────────────────────────────────────────────────────────
STATE_AS = {
  "state": "Assam",
  "state_code": "AS",
  "extraction_date": "2025-07-29T13:40:01.008529",
  "total_rtos": 37,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(33/33)"},
    {"name":"BARPETA","code":"AS15","value":"15","full_text":"BARPETA - AS15( 29-DEC-2016 )"},
    {"name":"BASKA","code":"AS28","value":"28","full_text":"BASKA - AS28( 13-NOV-2017 )"},
    {"name":"BISWANATH CHARIALI","code":"AS32","value":"32","full_text":"BISWANATH CHARIALI - AS32( 08-AUG-2019 )"},
    {"name":"BONGAIGAON","code":"AS19","value":"19","full_text":"BONGAIGAON - AS19( 24-APR-2017 )"},
    {"name":"CACHAR","code":"AS11","value":"11","full_text":"CACHAR - AS11( 05-MAY-2017 )"},
    {"name":"CHARAIDEO","code":"AS33","value":"33","full_text":"CHARAIDEO - AS33( 17-JAN-2020 )"},
    {"name":"CHIRANG","code":"AS26","value":"26","full_text":"CHIRANG - AS26( 25-SEP-2017 )"},
    {"name":"DARRANG","code":"AS13","value":"13","full_text":"DARRANG - AS13( 04-MAY-2018 )"},
    {"name":"DHEMAJI","code":"AS22","value":"22","full_text":"DHEMAJI - AS22( 05-OCT-2017 )"},
    {"name":"DHUBRI","code":"AS17","value":"17","full_text":"DHUBRI - AS17( 05-MAY-2017 )"},
    {"name":"DIBRUGARH","code":"AS6","value":"6","full_text":"DIBRUGARH - AS6( 16-FEB-2017 )"},
    {"name":"DIMA HASAO","code":"AS8","value":"8","full_text":"DIMA HASAO - AS8( 18-APR-2017 )"},
    {"name":"GOALPARA","code":"AS18","value":"18","full_text":"GOALPARA - AS18( 09-NOV-2016 )"},
    {"name":"GOLAGHAT","code":"AS5","value":"5","full_text":"GOLAGHAT - AS5( 03-MAY-2017 )"},
    {"name":"HAILAKANDI","code":"AS24","value":"24","full_text":"HAILAKANDI - AS24( 11-MAR-2019 )"},
    {"name":"HOJAI","code":"AS31","value":"31","full_text":"HOJAI - AS31( 09-DEC-2019 )"},
    {"name":"JORHAT","code":"AS3","value":"3","full_text":"JORHAT - AS3( 25-APR-2017 )"},
    {"name":"KAMRUP","code":"AS1","value":"1","full_text":"KAMRUP - AS1( 17-NOV-2016 )"},
    {"name":"KAMRUP(RURAL)","code":"AS25","value":"25","full_text":"KAMRUP(RURAL) - AS25( 24-NOV-2016 )"},
    {"name":"KARBI ANGLONG","code":"AS9","value":"9","full_text":"KARBI ANGLONG - AS9( 09-APR-2019 )"},
    {"name":"KARIMGANJ","code":"AS10","value":"10","full_text":"KARIMGANJ - AS10( 20-JUL-2017 )"},
    {"name":"KOKRAJHAR","code":"AS16","value":"16","full_text":"KOKRAJHAR - AS16( 24-APR-2017 )"},
    {"name":"LAKHIMPUR","code":"AS7","value":"7","full_text":"LAKHIMPUR - AS7( 05-OCT-2017 )"},
    {"name":"MAJULI","code":"AS29","value":"29","full_text":"MAJULI - AS29( 09-JUL-2019 )"},
    {"name":"MORIGAON","code":"AS21","value":"21","full_text":"MORIGAON - AS21( 07-APR-2018 )"},
    {"name":"NAGAON","code":"AS2","value":"2","full_text":"NAGAON - AS2( 19-APR-2017 )"},
    {"name":"NALBARI","code":"AS14","value":"14","full_text":"NALBARI - AS14( 15-DEC-2016 )"},
    {"name":"NIAIMT,CACHAR","code":"AS200","value":"200","full_text":"NIAIMT,CACHAR - AS200( 21-OCT-2019 )"},
    {"name":"NIAIMT,HAILAKANDI","code":"AS202","value":"202","full_text":"NIAIMT,HAILAKANDI - AS202( 21-OCT-2019 )"},
    {"name":"NIAIMT,KARIMGANJ","code":"AS201","value":"201","full_text":"NIAIMT,KARIMGANJ - AS201( 21-OCT-2019 )"},
    {"name":"SIVASAGAR","code":"AS4","value":"4","full_text":"SIVASAGAR - AS4( 02-MAY-2017 )"},
    {"name":"SONITPUR","code":"AS12","value":"12","full_text":"SONITPUR - AS12( 05-JAN-2017 )"},
    {"name":"SOUTH SALMARA","code":"AS34","value":"34","full_text":"SOUTH SALMARA - AS34( 20-DEC-2019 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"AS999","value":"999","full_text":"STATE TRANSPORT AUTHORITY - AS999( 24-SEP-2018 )"},
    {"name":"TINSUKIA","code":"AS23","value":"23","full_text":"TINSUKIA - AS23( 23-FEB-2017 )"},
    {"name":"UDALGURI","code":"AS27","value":"27","full_text":"UDALGURI - AS27( 17-AUG-2017 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Rajasthan
# ──────────────────────────────────────────────────────────────────────────────
STATE_RJ = {
  "state": "Rajasthan",
  "state_code": "RJ",
  "extraction_date": "2025-07-29T14:34:02.816735",
  "total_rtos": 143,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(59/59)"},
    {"name":"ABU ROAD DTO","code":"RJ38","value":"38","full_text":"ABU ROAD DTO - RJ38( 07-JAN-2019 )"},
    {"name":"Adinath Fitness Center","code":"RJ260","value":"260","full_text":"Adinath Fitness Center - RJ260( 01-JAN-2021 )"},
    {"name":"Agarwal Fitness Center","code":"RJ225","value":"225","full_text":"Agarwal Fitness Center - RJ225( 15-JAN-2020 )"},
    {"name":"AJMER RTO","code":"RJ1","value":"1","full_text":"AJMER RTO - RJ1( 13-APR-2017 )"},
    {"name":"A&L Company","code":"RJ267","value":"267","full_text":"A&L Company - RJ267( 08-APR-2021 )"},
    {"name":"Alwar Auto Mobile Fitness Center","code":"RJ243","value":"243","full_text":"Alwar Auto Mobile Fitness Center - RJ243( 11-SEP-2020 )"},
    {"name":"Alwar Fitness Center","code":"RJ254","value":"254","full_text":"Alwar Fitness Center - RJ254( 26-NOV-2020 )"},
    {"name":"ALWAR RTO","code":"RJ2","value":"2","full_text":"ALWAR RTO - RJ2( 19-APR-2018 )"},
    {"name":"ARAVALI FITNESS TESTING CENTER","code":"RJ218","value":"218","full_text":"ARAVALI FITNESS TESTING CENTER - RJ218( 02-DEC-2019 )"},
    {"name":"Arihant Vehicle Fitness Center","code":"RJ257","value":"257","full_text":"Arihant Vehicle Fitness Center - RJ257( 07-DEC-2020 )"},
    {"name":"Atharva Enterprises","code":"RJ261","value":"261","full_text":"Atharva Enterprises - RJ261( 05-JAN-2021 )"},
    {"name":"BALAJI ALLIANCE","code":"RJ280","value":"280","full_text":"BALAJI ALLIANCE - RJ280( 07-APR-2022 )"},
    {"name":"BALAJI FITNESS CENTER (BHILWARA)","code":"RJ210","value":"210","full_text":"BALAJI FITNESS CENTER (BHILWARA) - RJ210( 15-OCT-2019 )"},
    {"name":"BALAJI FITNESS CENTER (HANUMANGARH)","code":"RJ209","value":"209","full_text":"BALAJI FITNESS CENTER (HANUMANGARH) - RJ209( 15-OCT-2019 )"},
    {"name":"BALOTRA DTO","code":"RJ39","value":"39","full_text":"BALOTRA DTO - RJ39( 17-JUL-2019 )"},
    {"name":"BANSWARA DTO","code":"RJ3","value":"3","full_text":"BANSWARA DTO - RJ3( 03-MAY-2018 )"},
    {"name":"BANSWARA VEHICLE FITNESS CENTER","code":"RJ276","value":"276","full_text":"BANSWARA VEHICLE FITNESS CENTER - RJ276( 24-MAR-2022 )"},
    {"name":"BARAN DTO","code":"RJ28","value":"28","full_text":"BARAN DTO - RJ28( 09-JAN-2018 )"},
    {"name":"BARMER DTO","code":"RJ4","value":"4","full_text":"BARMER DTO - RJ4( 22-DEC-2017 )"},
    {"name":"BEAWAR DTO","code":"RJ36","value":"36","full_text":"BEAWAR DTO - RJ36( 24-NOV-2017 )"},
    {"name":"BHARATPUR RTO","code":"RJ5","value":"5","full_text":"BHARATPUR RTO - RJ5( 12-JUL-2017 )"},
    {"name":"Bharat Vahan Fitness Center","code":"RJ250","value":"250","full_text":"Bharat Vahan Fitness Center - RJ250( 13-NOV-2020 )"},
    {"name":"BHILWARA DTO","code":"RJ6","value":"6","full_text":"BHILWARA DTO - RJ6( 28-JUN-2017 )"},
    {"name":"BHINMAL DTO","code":"RJ46","value":"46","full_text":"BHINMAL DTO - RJ46( 23-JUL-2019 )"},
    {"name":"BHIWARI DTO","code":"RJ40","value":"40","full_text":"BHIWARI DTO - RJ40( 06-FEB-2018 )"},
    {"name":"BIKANER RTO","code":"RJ7","value":"7","full_text":"BIKANER RTO - RJ7( 02-MAY-2017 )"},
    {"name":"BUNDI DTO","code":"RJ8","value":"8","full_text":"BUNDI DTO - RJ8( 19-DEC-2017 )"},
    {"name":"CHITTORGARH RTO","code":"RJ9","value":"9","full_text":"CHITTORGARH RTO - RJ9( 08-NOV-2017 )"},
    {"name":"CHOMU DTO","code":"RJ41","value":"41","full_text":"CHOMU DTO - RJ41( 20-SEP-2017 )"},
    {"name":"CHURU DTO","code":"RJ10","value":"10","full_text":"CHURU DTO - RJ10( 25-JAN-2018 )"},
    {"name":"DAUSA RTO","code":"RJ29","value":"29","full_text":"DAUSA RTO - RJ29( 20-SEP-2017 )"},
    {"name":"DHOLPUR DTO","code":"RJ11","value":"11","full_text":"DHOLPUR DTO - RJ11( 07-NOV-2017 )"},
    {"name":"DIDWANA DTO","code":"RJ37","value":"37","full_text":"DIDWANA DTO - RJ37( 04-JUN-2018 )"},
    {"name":"DUDU DTO","code":"RJ47","value":"47","full_text":"DUDU DTO - RJ47( 11-APR-2017 )"},
    {"name":"DUDU FITNESS CENTER","code":"RJ281","value":"281","full_text":"DUDU FITNESS CENTER - RJ281( 11-APR-2022 )"},
    {"name":"DUNGARPUR DTO","code":"RJ12","value":"12","full_text":"DUNGARPUR DTO - RJ12( 27-SEP-2017 )"},
    {"name":"EXPLORE IT SERVICES PVT. LTD.","code":"RJ228","value":"228","full_text":"EXPLORE IT SERVICES PVT. LTD. - RJ228( 26-FEB-2020 )"},
    {"name":"FREEDOM MOTORS","code":"RJ224","value":"224","full_text":"FREEDOM MOTORS - RJ224( 10-JAN-2020 )"},
    {"name":"Ganesh Ji Fitness Center","code":"RJ226","value":"226","full_text":"Ganesh Ji Fitness Center - RJ226( 23-JAN-2020 )"},
    {"name":"G.Y. Fitness Center","code":"RJ223","value":"223","full_text":"G.Y. Fitness Center - RJ223( 31-DEC-2019 )"},
    {"name":"HANUMANGARH DTO","code":"RJ31","value":"31","full_text":"HANUMANGARH DTO - RJ31( 30-APR-2018 )"},
    {"name":"Hindustan Automobiles","code":"RJ251","value":"251","full_text":"Hindustan Automobiles - RJ251( 25-NOV-2020 )"},
    {"name":"Indira Vehicle Fitness Centre","code":"RJ269","value":"269","full_text":"Indira Vehicle Fitness Centre - RJ269( 27-MAY-2021 )"},
    {"name":"INFINITY FITNESS CENTER","code":"RJ231","value":"231","full_text":"INFINITY FITNESS CENTER - RJ231( 20-MAR-2020 )"},
    {"name":"JAGATPURA, JAIPUR ARTO","code":"RJ141","value":"141","full_text":"JAGATPURA, JAIPUR ARTO - RJ141( 20-DEC-2016 )"},
    {"name":"Jai Bhawani Fitness Center","code":"RJ236","value":"236","full_text":"Jai Bhawani Fitness Center - RJ236( 20-AUG-2020 )"},
    {"name":"JAIPUR (FIRST) RTO","code":"RJ14","value":"14","full_text":"JAIPUR (FIRST) RTO - RJ14( 28-NOV-2016 )"},
    {"name":"JAIPUR (SECOND) RTO","code":"RJ59","value":"59","full_text":"JAIPUR (SECOND) RTO - RJ59( 19-JAN-2023 )"},
    {"name":"Jaipur Vehicle Fitness and Maintenance Center","code":"RJ234","value":"234","full_text":"Jaipur Vehicle Fitness and Maintenance Center - RJ234( 10-JUL-2020 )"},
    {"name":"JAISALMER DTO","code":"RJ15","value":"15","full_text":"JAISALMER DTO - RJ15( 27-FEB-2018 )"},
    {"name":"JALORE DTO","code":"RJ16","value":"16","full_text":"JALORE DTO - RJ16( 05-OCT-2017 )"},
    {"name":"JALORE FITNESS CENTRE","code":"RJ282","value":"282","full_text":"JALORE FITNESS CENTRE - RJ282( 20-APR-2022 )"},
    {"name":"JHALAWAR DTO","code":"RJ17","value":"17","full_text":"JHALAWAR DTO - RJ17( 09-JAN-2018 )"},
    {"name":"JHUNJHUNU DTO","code":"RJ18","value":"18","full_text":"JHUNJHUNU DTO - RJ18( 16-JAN-2018 )"},
    {"name":"Jodhpur Parivahan Fitness Centre","code":"RJ242","value":"242","full_text":"Jodhpur Parivahan Fitness Centre - RJ242( 11-SEP-2020 )"},
    {"name":"JODHPUR RTO","code":"RJ19","value":"19","full_text":"JODHPUR RTO - RJ19( 27-DEC-2017 )"},
    {"name":"KAROLI DTO","code":"RJ34","value":"34","full_text":"KAROLI DTO - RJ34( 16-JAN-2018 )"},
    {"name":"KEKRI DTO","code":"RJ48","value":"48","full_text":"KEKRI DTO - RJ48( 14-DEC-2017 )"},
    {"name":"KHETRI DTO","code":"RJ53","value":"53","full_text":"KHETRI DTO - RJ53( 13-SEP-2018 )"},
    {"name":"KISHANGARH DTO","code":"RJ42","value":"42","full_text":"KISHANGARH DTO - RJ42( 20-FEB-2018 )"},
    {"name":"KOTA RTO","code":"RJ20","value":"20","full_text":"KOTA RTO - RJ20( 06-JUN-2017 )"},
    {"name":"Kota Vehicle Fitness Center","code":"RJ263","value":"263","full_text":"Kota Vehicle Fitness Center - RJ263( 05-APR-2021 )"},
    {"name":"KOTPUTALI DTO","code":"RJ32","value":"32","full_text":"KOTPUTALI DTO - RJ32( 20-SEP-2017 )"},
    {"name":"Laxmi Parivahan Fitness Center","code":"RJ266","value":"266","full_text":"Laxmi Parivahan Fitness Center - RJ266( 07-APR-2021 )"},
    {"name":"Mahadev Fitness Center","code":"RJ233","value":"233","full_text":"Mahadev Fitness Center - RJ233( 14-JUL-2020 )"},
    {"name":"MAHADEV FITNESS CENTER BHILWARA","code":"RJ274","value":"274","full_text":"MAHADEV FITNESS CENTER BHILWARA - RJ274( 08-MAR-2022 )"},
    {"name":"MAHADEV FITNESS CENTER JODHPUR","code":"RJ273","value":"273","full_text":"MAHADEV FITNESS CENTER JODHPUR - RJ273( 08-MAR-2022 )"},
    {"name":"MAHAVEER JAIN FITNESS CENTRE","code":"RJ229","value":"229","full_text":"MAHAVEER JAIN FITNESS CENTRE - RJ229( 02-MAR-2020 )"},
    {"name":"MAHAVEER PRASAD RAM KISHAN","code":"RJ232","value":"232","full_text":"MAHAVEER PRASAD RAM KISHAN - RJ232( 08-JUN-2020 )"},
    {"name":"Marudhara Transport Company","code":"RJ271","value":"271","full_text":"Marudhara Transport Company - RJ271( 05-JUL-2021 )"},
    {"name":"Marwar Fitness Center","code":"RJ249","value":"249","full_text":"Marwar Fitness Center - RJ249( 13-NOV-2020 )"},
    {"name":"Matsya Fitness Center","code":"RJ220","value":"220","full_text":"Matsya Fitness Center - RJ220( 26-DEC-2019 )"},
    {"name":"M & D Automobile Fitness Center","code":"RJ222","value":"222","full_text":"M & D Automobile Fitness Center - RJ222( 31-DEC-2019 )"},
    {"name":"Meel Motors","code":"RJ230","value":"230","full_text":"Meel Motors - RJ230( 02-MAR-2020 )"},
    {"name":"Meera Fitness Center","code":"RJ247","value":"247","full_text":"Meera Fitness Center - RJ247( 22-OCT-2020 )"},
    {"name":"MEERA FITNESS TESTING CENTER CHITTORGARH","code":"RJ215","value":"215","full_text":"MEERA FITNESS TESTING CENTER CHITTORGARH - RJ215( 06-NOV-2019 )"},
    {"name":"M.K. Fitness Center","code":"RJ239","value":"239","full_text":"M.K. Fitness Center - RJ239( 03-SEP-2020 )"},
    {"name":"M/S Dholpur Fitness Center","code":"RJ201","value":"201","full_text":"M/S Dholpur Fitness Center - RJ201( 14-MAY-2019 )"},
    {"name":"M/S Jagdamba Fitness Center","code":"RJ203","value":"203","full_text":"M/S Jagdamba Fitness Center - RJ203( 30-JUL-2019 )"},
    {"name":"M/S Nandan Fitness Testing Center","code":"RJ204","value":"204","full_text":"M/S Nandan Fitness Testing Center - RJ204( 22-AUG-2019 )"},
    {"name":"M/S OM Fitness & Service Center","code":"RJ202","value":"202","full_text":"M/S OM Fitness & Service Center - RJ202( 25-JUL-2019 )"},
    {"name":"Naganaray Fitness Center","code":"RJ255","value":"255","full_text":"Naganaray Fitness Center - RJ255( 02-DEC-2020 )"},
    {"name":"NAGAUR DTO","code":"RJ21","value":"21","full_text":"NAGAUR DTO - RJ21( 07-NOV-2017 )"},
    {"name":"Navdeep Fitness Test Center","code":"RJ248","value":"248","full_text":"Navdeep Fitness Test Center - RJ248( 02-NOV-2020 )"},
    {"name":"Navdurga Vahan Fitness Center","code":"RJ245","value":"245","full_text":"Navdurga Vahan Fitness Center - RJ245( 30-SEP-2020 )"},
    {"name":"Navkar Shri Fitness Testing Center","code":"RJ216","value":"216","full_text":"Navkar Shri Fitness Testing Center - RJ216( 26-NOV-2019 )"},
    {"name":"NOHAR DTO","code":"RJ49","value":"49","full_text":"NOHAR DTO - RJ49( 01-JUN-2018 )"},
    {"name":"NOKHA DTO","code":"RJ50","value":"50","full_text":"NOKHA DTO - RJ50( 07-FEB-2018 )"},
    {"name":"Nokha Vehicle Fitness Center","code":"RJ253","value":"253","full_text":"Nokha Vehicle Fitness Center - RJ253( 27-NOV-2020 )"},
    {"name":"PALI RTO","code":"RJ22","value":"22","full_text":"PALI RTO - RJ22( 10-APR-2018 )"},
    {"name":"Parasvnath Fitness Center","code":"RJ240","value":"240","full_text":"Parasvnath Fitness Center - RJ240( 03-SEP-2020 )"},
    {"name":"PAWAN VEHICLE FITNESS CENTER PVT LTD","code":"RJ277","value":"277","full_text":"PAWAN VEHICLE FITNESS CENTER PVT LTD - RJ277( 05-APR-2022 )"},
    {"name":"PHALODI DTO","code":"RJ43","value":"43","full_text":"PHALODI DTO - RJ43( 12-SEP-2018 )"},
    {"name":"PIPAR CITY DTO","code":"RJ54","value":"54","full_text":"PIPAR CITY DTO - RJ54( 17-AUG-2021 )"},
    {"name":"POKHRAN DTO","code":"RJ55","value":"55","full_text":"POKHRAN DTO - RJ55( 17-AUG-2021 )"},
    {"name":"PRATAPGARH DTO","code":"RJ35","value":"35","full_text":"PRATAPGARH DTO - RJ35( 07-NOV-2017 )"},
    {"name":"Preksha Parivahan Fitness Center","code":"RJ265","value":"265","full_text":"Preksha Parivahan Fitness Center - RJ265( 08-APR-2021 )"},
    {"name":"Prerna Parivahan Fitness Center","code":"RJ272","value":"272","full_text":"Prerna Parivahan Fitness Center - RJ272( 05-JUL-2021 )"},
    {"name":"RAJASTHAN VEHICLE FITNESS CENTER","code":"RJ283","value":"283","full_text":"RAJASTHAN VEHICLE FITNESS CENTER - RJ283( 21-AUG-2023 )"},
    {"name":"RAJSAMAND DTO","code":"RJ30","value":"30","full_text":"RAJSAMAND DTO - RJ30( 27-AUG-2019 )"},
    {"name":"RAMGANJMANDI DTO","code":"RJ33","value":"33","full_text":"RAMGANJMANDI DTO - RJ33( 22-FEB-2018 )"},
    {"name":"R.K. Fitness Center","code":"RJ221","value":"221","full_text":"R.K. Fitness Center - RJ221( 31-DEC-2019 )"},
    {"name":"Royal Motors","code":"RJ268","value":"268","full_text":"Royal Motors - RJ268( 27-MAY-2021 )"},
    {"name":"SADULSHAHAR DTO","code":"RJ56","value":"56","full_text":"SADULSHAHAR DTO - RJ56( 17-AUG-2021 )"},
    {"name":"SAHAPURA (BHILWARA) DTO","code":"RJ51","value":"51","full_text":"SAHAPURA (BHILWARA) DTO - RJ51( 16-FEB-2018 )"},
    {"name":"SAHAPURA (JAIPUR) DTO","code":"RJ52","value":"52","full_text":"SAHAPURA (JAIPUR) DTO - RJ52( 15-DEC-2017 )"},
    {"name":"SALUMBAR DTO","code":"RJ58","value":"58","full_text":"SALUMBAR DTO - RJ58( 10-OCT-2022 )"},
    {"name":"SAWAI MADHOPUR DTO","code":"RJ25","value":"25","full_text":"SAWAI MADHOPUR DTO - RJ25( 19-JUL-2016 )"},
    {"name":"Schoolnet India Limited","code":"RJ256","value":"256","full_text":"Schoolnet India Limited - RJ256( 27-NOV-2020 )"},
    {"name":"SHAHPURA BHILWARA FITNESS CENTER","code":"RJ275","value":"275","full_text":"SHAHPURA BHILWARA FITNESS CENTER - RJ275( 16-MAR-2022 )"},
    {"name":"SHAHPURA VEHICLE FITNESS CENTER (JAIPUR)","code":"RJ213","value":"213","full_text":"SHAHPURA VEHICLE FITNESS CENTER (JAIPUR) - RJ213( 01-NOV-2019 )"},
    {"name":"Shanti Vehicle Fitness Testing Center","code":"RJ208","value":"208","full_text":"Shanti Vehicle Fitness Testing Center - RJ208( 10-OCT-2019 )"},
    {"name":"Shashank Automobiles","code":"RJ227","value":"227","full_text":"Shashank Automobiles - RJ227( 23-JAN-2020 )"},
    {"name":"SHIV KRIPA FITNESS CENTER PVT LTD","code":"RJ279","value":"279","full_text":"SHIV KRIPA FITNESS CENTER PVT LTD - RJ279( 05-APR-2022 )"},
    {"name":"SHREE BALAJI FITNESS CENTER PALI","code":"RJ241","value":"241","full_text":"SHREE BALAJI FITNESS CENTER PALI - RJ241( 07-SEP-2020 )"},
    {"name":"Shree Fitness Center","code":"RJ211","value":"211","full_text":"Shree Fitness Center - RJ211( 11-OCT-2019 )"},
    {"name":"Shree Kamdhenu Fitness Center","code":"RJ219","value":"219","full_text":"Shree Kamdhenu Fitness Center - RJ219( 26-DEC-2019 )"},
    {"name":"SHREE SHYAM VEHICLE FITNESS CENTER","code":"RJ246","value":"246","full_text":"SHREE SHYAM VEHICLE FITNESS CENTER - RJ246( 08-OCT-2020 )"},
    {"name":"SHRI BALAJI FITNESS CENTER BIKANER","code":"RJ206","value":"206","full_text":"SHRI BALAJI FITNESS CENTER BIKANER - RJ206( 11-SEP-2019 )"},
    {"name":"Shri Bikaner Fitness Center","code":"RJ205","value":"205","full_text":"Shri Bikaner Fitness Center - RJ205( 02-SEP-2019 )"},
    {"name":"Shri Fitness Center","code":"RJ259","value":"259","full_text":"Shri Fitness Center - RJ259( 21-DEC-2020 )"},
    {"name":"Shri Force Fitness Center","code":"RJ217","value":"217","full_text":"Shri Force Fitness Center - RJ217( 03-DEC-2019 )"},
    {"name":"Shri Karni Fitness Center","code":"RJ214","value":"214","full_text":"Shri Karni Fitness Center - RJ214( 04-NOV-2019 )"},
    {"name":"SHRI MAHALAXMI FITNESS CENTER","code":"RJ278","value":"278","full_text":"SHRI MAHALAXMI FITNESS CENTER - RJ278( 05-APR-2022 )"},
    {"name":"Shri Vinayak Auto Fitness Center","code":"RJ252","value":"252","full_text":"Shri Vinayak Auto Fitness Center - RJ252( 27-NOV-2020 )"},
    {"name":"SIKAR RTO","code":"RJ23","value":"23","full_text":"SIKAR RTO - RJ23( 27-SEP-2017 )"},
    {"name":"Sikar Vehicle Fitness Center","code":"RJ212","value":"212","full_text":"Sikar Vehicle Fitness Center - RJ212( 23-OCT-2019 )"},
    {"name":"SIROHI DTO","code":"RJ24","value":"24","full_text":"SIROHI DTO - RJ24( 27-FEB-2018 )"},
    {"name":"Speedline Auto Fitness Private Limited","code":"RJ270","value":"270","full_text":"Speedline Auto Fitness Private Limited - RJ270( 27-MAY-2021 )"},
    {"name":"SRI GANGANAGAR DTO","code":"RJ13","value":"13","full_text":"SRI GANGANAGAR DTO - RJ13( 27-SEP-2017 )"},
    {"name":"SUJANGARH DTO","code":"RJ44","value":"44","full_text":"SUJANGARH DTO - RJ44( 16-FEB-2018 )"},
    {"name":"SUMERPUR DTO","code":"RJ57","value":"57","full_text":"SUMERPUR DTO - RJ57( 17-AUG-2021 )"},
    {"name":"Swarna Shri Fitness Testing Center","code":"RJ207","value":"207","full_text":"Swarna Shri Fitness Testing Center - RJ207( 09-OCT-2019 )"},
    {"name":"TIRUPATI ASSOCIATES","code":"RJ238","value":"238","full_text":"TIRUPATI ASSOCIATES - RJ238( 27-AUG-2020 )"},
    {"name":"TIRUPATI ASSOCIATES MORIJA CHOMU","code":"RJ237","value":"237","full_text":"TIRUPATI ASSOCIATES MORIJA CHOMU - RJ237( 27-AUG-2020 )"},
    {"name":"TIRUPATI FITNESS CENTER","code":"RJ235","value":"235","full_text":"TIRUPATI FITNESS CENTER - RJ235( 22-JUL-2020 )"},
    {"name":"TONK DTO","code":"RJ26","value":"26","full_text":"TONK DTO - RJ26( 07-NOV-2017 )"},
    {"name":"Tonk Fitness Center","code":"RJ244","value":"244","full_text":"Tonk Fitness Center - RJ244( 30-SEP-2020 )"},
    {"name":"Udaipur Fitness Center","code":"RJ262","value":"262","full_text":"Udaipur Fitness Center - RJ262( 05-APR-2021 )"},
    {"name":"UDAIPUR RTO","code":"RJ27","value":"27","full_text":"UDAIPUR RTO - RJ27( 06-JUN-2017 )"},
    {"name":"Vaahan Fitness Center","code":"RJ264","value":"264","full_text":"Vaahan Fitness Center - RJ264( 06-APR-2021 )"},
    {"name":"VATSAL ENTERPRISES","code":"RJ258","value":"258","full_text":"VATSAL ENTERPRISES - RJ258( 18-DEC-2020 )"}
  ]
}

# ──────────────────────────────────────────────────────────────────────────────
# Ladakh
# ──────────────────────────────────────────────────────────────────────────────
STATE_LA = {
  "state": "Ladakh",
  "state_code": "LA",
  "extraction_date": "2025-07-29T14:11:25.042960",
  "total_rtos": 4,
  "rtos": [
    {"name":"All Vahan4 Running Office","code":"ALL","value":"-1","full_text":"All Vahan4 Running Office(3/3)"},
    {"name":"KARGIL ARTO","code":"LA1","value":"1","full_text":"KARGIL ARTO - LA1( 23-JUL-2018 )"},
    {"name":"LEH ARTO","code":"LA2","value":"2","full_text":"LEH ARTO - LA2( 11-MAR-2018 )"},
    {"name":"STATE TRANSPORT AUTHORITY","code":"LA999","value":"999","full_text":"STATE TRANSPORT AUTHORITY - LA999( 04-MAY-2021 )"}
  ]
}

# ──────────────────────────────────────────────────────────────
# NEW: Seed User Agents
# ──────────────────────────────────────────────────────────────
def seed_user_agents(session: Session):
    pool, _ = get_or_create(session, UserAgentPool, name="default_pool")
    session.flush()

    uas = [
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36",
            False, 5
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.5993.117 Safari/537.36",
            False, 3
        ),
        (
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Mobile Safari/537.36",
            True, 2
        ),
    ]

    for ua_string, is_mobile, weight in uas:
        get_or_create(
            session,
            UserAgent,
            pool_id=pool.id,
            ua_string=ua_string,
            defaults=dict(is_mobile=is_mobile, weight=weight)
        )

    print("✅ Seeded user agents")


# ──────────────────────────────────────────────────────────────────────────────
# Normalization
# ──────────────────────────────────────────────────────────────────────────────

def normalize_state_code(name: str, code: str, value: str) -> str:
    """
    Prefer canonical two-letter transport codes.
    Fix known anomalies from the portal payloads.
    """
    name_l = (name or "").lower().strip()
    if "all vahan4 running states" in name_l:
        return "AL"
    # special cases
    if name == "Lakshadweep":
        return "LD"
    if name.startswith("UT of DNH and DD"):
        return "DD"
    if name == "Odisha":
        return "OD"
    # otherwise trust 'code' if it looks like AA
    if code and len(code) in (2,3):
        return code
    # fallback to value
    return value or code


# ──────────────────────────────────────────────────────────────────────────────
# Seed routines
# ──────────────────────────────────────────────────────────────────────────────

def seed_portal(session: Session):
    site, _ = get_or_create(session, PortalSite,
                            name="Vahan Analytics",
                            defaults=dict(
                                base_url="https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml",
                                robots_policy="unknown",
                                notes="PrimeFaces UI; expect CAPTCHA at peak; use jitter/backoff."
                            ))
    session.flush()

    f_y = ensure_portal_field(session, site.id, "y_axis", "yaxisVar", "select")
    f_x = ensure_portal_field(session, site.id, "x_axis", "xaxisVar", "select")
    f_rto = ensure_portal_field(session, site.id, "rto", "selectedRto", "select")
    f_state = ensure_portal_field(session, site.id, "state", "<dynamic primefaces id>", "select")
    f_vehicle = ensure_portal_field(session, site.id, "vehicle_filter", "//label[normalize-space(.)=?]", "checkbox")

    session.flush()
    return dict(site=site, f_state=f_state, f_rto=f_rto, f_x=f_x, f_y=f_y, f_vehicle=f_vehicle)


def seed_axes(session: Session):
    for row in AXIS_ROWS:
        get_or_create(session, AxisFilter, axis=row["axis"], filter=row["filter"])


def seed_vehicle_filters(session: Session):
    for row in VEHICLE_FILTER_ROWS:
        get_or_create(session, VehicleFilter, name=row["name"])


def seed_state_dropdown(session: Session, portal_ids: Dict, all_states_blob: Dict):
    """
    Seeds the STATE dropdown cache (portal_field_option for 'state')
    and inserts/updates real rows in states table (skipping aggregate 'AL').
    """
    f_state = portal_ids["f_state"]
    for s in all_states_blob["states"]:
        raw_code = s.get("code") or ""
        code = normalize_state_code(s["name"], raw_code, s.get("value") or "")
        label = s.get("display_name") or s["name"]
        value_code = s.get("value") or code

        # 1) cache the dropdown option
        ensure_field_option(session, f_state.id, value_code, label, parent_code=None)

        # 2) insert real state (skip the "All ... states")
        if code == "AL" or "All Vahan4 Running States" in s["name"]:
            continue

        st, _ = get_or_create(session, State, code=code,
                              defaults=dict(name=s["name"], total_rto=0))
        st.name = s["name"]  # keep latest pretty name

        session.flush()


def seed_state_rtos(session: Session, portal_ids: Dict, state_blob: Dict):
    """
    Upserts RTOS for a single state.
    - caches every RTO option in portal_field_option (parent_code = state_code)
    - inserts only REAL RTOs into rtos (skips code='ALL' or value='-1')
    - updates states.total_rto = count(real_rtos)
    """
    f_rto = portal_ids["f_rto"]
    s_code_canonical = normalize_state_code(state_blob["state"], state_blob["state_code"], state_blob["state_code"])
    st, _ = get_or_create(session, State, code=s_code_canonical,
                          defaults=dict(name=state_blob["state"], total_rto=0))
    st.name = state_blob["state"]

    session.flush()

    real_count = 0
    for r in state_blob["rtos"]:
        # cache every option (so bot knows how to change selection)
        ensure_field_option(
            session, f_rto.id,
            r.get("value", r["code"]),  # value attribute is what PrimeFaces submits
            r["full_text"],
            parent_code=s_code_canonical
        )

        # skip aggregate "ALL" in the rtos master
        if r.get("code") == "ALL" or r.get("value") == "-1":
            continue

        rto, _ = get_or_create(session, RTO,
                               state_id=st.id, code=r["code"],
                               defaults=dict(
                                   name=r["name"], value=r.get("value"),
                                   full_text=r.get("full_text"), is_active=True
                               ))
        rto.name = r["name"]
        rto.value = r.get("value")
        rto.full_text = r.get("full_text")
        rto.is_active = True
        real_count += 1

    st.total_rto = real_count

def seed_job_templates(session: Session, site: PortalSite):
    """
    Create a few example job templates pointing at the Vahan Analytics site.
    These are just for testing the scheduler/runner; tweak cron_expr as needed.
    """
    templates = [
        dict(
            name="Daily Extraction: Maker & MonthWise",
            site_id=site.id,
            cron_expr="35 12 * * *",         # every day 02:00 pm  IST
            timezone="Asia/Kolkata",
            enabled=True,
            notes="Run jobs with Y=Maker, X=Month Wise for all configured filter sets."
        )
    ]

    created = []
    for t in templates:
        # Use (name, site_id) as a natural key so it’s idempotent
        row, is_new = get_or_create(
            session, JobTemplate,
            name=t["name"], site_id=t["site_id"],
            defaults=dict(
                cron_expr=t["cron_expr"],
                timezone=t.get("timezone", "Asia/Kolkata"),
                enabled=t.get("enabled", True),
                notes=t.get("notes"),
            )
        )
        # Keep the latest config if the row already exists
        row.cron_expr = t["cron_expr"]
        row.timezone = t.get("timezone", "Asia/Kolkata")
        row.enabled = t.get("enabled", True)
        row.notes = t.get("notes")
        created.append((row, is_new))
    return created



def run_seed():
    db: Session = SessionLocal()
    try:
        print("🔧 Seeding portal/site + fields")
        portal_ids = seed_portal(db)

        print("🔧 Seeding axis_filter")
        seed_axes(db)

        print("🔧 Seeding vehicle_filter")
        seed_vehicle_filters(db)

        print("🔧 Seeding user agents")
        seed_user_agents(db)

        print("🔧 Seeding STATE dropdown (36 rows incl. AL aggregate)")
        seed_state_dropdown(db, portal_ids, ALL_STATES_BLOB)

        print("🔧 Seeding RTOS for AN (Andaman & Nicobar)")
        seed_state_rtos(db, portal_ids, STATE_AN)

        print("🔧 Seeding RTOS for AP (Andhra Pradesh)")
        seed_state_rtos(db, portal_ids, STATE_AP)

        print("🔧 Seeding RTOS for KA (Karnataka)")
        seed_state_rtos(db, portal_ids, STATE_KA)

        print("🔧 Seeding RTOS for BR (Bihar)")
        seed_state_rtos(db, portal_ids, STATE_BR)

        print("🔧 Seeding RTOS for CG (Chhattisgarh)")
        seed_state_rtos(db, portal_ids, STATE_CG)

        print("🔧 Seeding RTOS for UP (Uttar Pradesh)")
        seed_state_rtos(db, portal_ids, STATE_UP)

        print("🔧 Seeding RTO for PB (PUNJAB)")
        seed_state_rtos(db, portal_ids, STATE_PB)

        print("🔧 Seeding RTOS for WB (West Bengal)")
        seed_state_rtos(db, portal_ids, STATE_WB)

        print("🔧 Seeding RTOS for DL (Delhi)")
        seed_state_rtos(db, portal_ids, STATE_DL)

        print("🔧 Seeding RTOS for GA (Goa)")
        seed_state_rtos(db, portal_ids, STATE_GA)

        print("🔧 Seeding RTOS for LA (Lakshadweep)")
        seed_state_rtos(db, portal_ids, STATE_LD)

        print("🔧 Seeding RTOS for JK (Jammu & Kashmir)")
        seed_state_rtos(db, portal_ids, STATE_JK)

        print("🔧 Seeding RTOS for GJ (Gujarat)")
        seed_state_rtos(db, portal_ids, STATE_GJ)

        print("🔧 Seeding RTOS for AS (Assam)")
        seed_state_rtos(db, portal_ids, STATE_AS)

        print("🔧 Seeding RTOS for KL (Kerala)")
        seed_state_rtos(db, portal_ids, STATE_KL)

        print("🔧 Seeding RTOS for AR (Arunachal Pradesh)")
        seed_state_rtos(db, portal_ids, STATE_AR)

        print("🔧 Seeding RTOS for SK (Sikkim)")
        seed_state_rtos(db, portal_ids, STATE_SK)

        print("🔧 Seeding RTOS for OD (Odisha)")
        seed_state_rtos(db, portal_ids, STATE_OD)

        print("🔧 Seeding RTOS for TR (Tripura)")
        seed_state_rtos(db, portal_ids, STATE_TR)

        print("🔧 Seeding RTOS for UK (Uttarakhand)")
        seed_state_rtos(db, portal_ids, STATE_UK)

        print("🔧 Seeding RTOS for HP (Himachal Pradesh)")
        seed_state_rtos(db, portal_ids, STATE_HP)

        print("🔧 Seeding RTOS for RJ (Rajasthan)")
        seed_state_rtos(db, portal_ids, STATE_RJ)

        print("🔧 Seeding RTOS for JH (Jharkhand)")
        seed_state_rtos(db, portal_ids, STATE_JH)

        print("🔧 Seeding RTOS for TN (Tamil Nadu)")
        seed_state_rtos(db, portal_ids, STATE_TN)

        print("🔧 Seeding RTOS for CH (Chandigarh)")
        seed_state_rtos(db, portal_ids, STATE_CH)

        print("🔧 Seeding RTOS for UT (UT of DNH and DD)")
        seed_state_rtos(db, portal_ids, STATE_UT)

        print("🔧 Seeding RTOS for MH (Maharashtra)")
        seed_state_rtos(db, portal_ids, STATE_MH)

        print("🔧 Seeding RTOS for MP (Madhya Pradesh)")
        seed_state_rtos(db, portal_ids, STATE_MP)

        print("🔧 Seeding RTOS for MN (Manipur)")
        seed_state_rtos(db, portal_ids, STATE_MN)

        print("🔧 Seeding RTOS for ML (Meghalaya)")
        seed_state_rtos(db, portal_ids, STATE_ML)

        print("🔧 Seeding RTOS for MZ (Mizoram)")
        seed_state_rtos(db, portal_ids, STATE_MZ)

        print("🔧 Seeding RTOS for NL (Nagaland)")
        seed_state_rtos(db, portal_ids, STATE_NL)

        print("🔧 Seeding RTOS for HR (Haryana)")
        seed_state_rtos(db, portal_ids, STATE_HR)

        print("🔧 Seeding RTOS for PY (Puducherry)")
        seed_state_rtos(db, portal_ids, STATE_PY)

        print("🔧 Seeding RTOS for LA (Ladakh)")
        seed_state_rtos(db, portal_ids, STATE_LA)

        print("🔧 Seeding example job templates")
        seed_job_templates(db, portal_ids["site"])

        # If you want to keep a cache of the aggregate “All States” → “All RTOs”:
        # We DO NOT insert these as real states/rtos, but we do cache dropdown options.
        print("ℹ️  Caching aggregate ‘All States’ / ‘All RTOs’ options for fidelity")
        ensure_field_option(db, portal_ids["f_state"].id, "-1", "All Vahan4 Running States (35/36)", None)
        ensure_field_option(db, portal_ids["f_rto"].id, "-1", "All Vahan4 Running Office(1386/1445)", "AL")

        db.commit()
        print("✅ Seed complete.")
    except Exception as e:
        db.rollback()
        print("❌ Seed failed:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
