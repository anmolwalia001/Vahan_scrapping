# db/seed.py
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
    UserAgentPool, UserAgent, ProxyPool, ProxyEndpoint
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
    {"name":"Little Andaman","code":"AN207","value":"207","full_text":"Little Andaman  - AN207( 17-FEB-2025 )"},
    {"name":"Mayabunder","code":"AN203","value":"203","full_text":"Mayabunder - AN203( 09-NOV-2021 )"},
    {"name":"Port Blair DTO","code":"AN1","value":"1","full_text":"Port Blair DTO - AN1( 15-AUG-2020 )"},
    {"name":"Rangat","code":"AN202","value":"202","full_text":"Rangat - AN202( 17-NOV-2021 )"},
    {"name":"Swaraj Dweep","code":"AN206","value":"206","full_text":"Swaraj Dweep - AN206( 29-NOV-2021 )"}
  ]
}

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
    {"name":"MAYUR VIHAR","code":"DL7","value":"7","full_text":"MAYUR VIHAR  - DL7( 29-JUN-2015 )"},
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


def seed_proxies(session: Session):
    pool, _ = get_or_create(session, ProxyPool, name="default_proxy_pool")
    session.flush()  # ensure pool.id is available

    proxies = [
        # Example: "http://user:pass@host:port" OR "http://host:port"
        ("http://123.45.67.89:8080", 5),
        ("http://98.76.54.32:3128", 3),
    ]

    for endpoint, weight in proxies:
        get_or_create(
            session,
            ProxyEndpoint,
            pool_id=pool.id,
            endpoint=endpoint,
            defaults=dict(is_active=True, weight=weight, last_used_at=None)
        )

    print("✅ Seeded proxies")




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

        print("🔧 Seeding proxies")
        seed_proxies(db)

        print("🔧 Seeding STATE dropdown (36 rows incl. AL aggregate)")
        seed_state_dropdown(db, portal_ids, ALL_STATES_BLOB)

        print("🔧 Seeding RTOS for AN (Andaman & Nicobar)")
        seed_state_rtos(db, portal_ids, STATE_AN)

        print("🔧 Seeding RTOS for AP (Andhra Pradesh) [partial list you pasted]")
        seed_state_rtos(db, portal_ids, STATE_AP)

        print("🔧 Seeding RTOS for DL (Delhi)")
        seed_state_rtos(db, portal_ids, STATE_DL)

        print("🔧 Seeding RTOS for GA (Goa)")
        seed_state_rtos(db, portal_ids, STATE_GA)

        print("🔧 Seeding RTOS for GJ (Gujarat)")
        seed_state_rtos(db, portal_ids, STATE_GJ)


        print("🔧 Seeding RTOS for LA (Ladakh)")
        seed_state_rtos(db, portal_ids, STATE_LA)

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
