from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, field_validator
from typing_extensions import Annotated
from bs4 import BeautifulSoup as bs


class IndexedYear(int):
    start_year = 2000
    end_year = 2027

    def __new__(cls, value):
        if not (cls.start_year <= value <= cls.end_year):
            raise ValueError(f'Invalid year: {value}, must be between {cls.start_year} and {cls.end_year}')
        return super(IndexedYear, cls).__new__(cls, value)
    
    def index(self) -> int:
        """Return the zero-based index starting from the year 2000."""
        return self.end_year - self
    
IndexedYearAnnotated = Annotated[int, IndexedYear]
    
class MultiEnumDropdown(BaseModel):
    items: list[Enum]
    id: str
    label: str

    def to_payload_items(self) -> list[dict]:
        sorted_items = sorted(self.items, key=lambda item: list(item.__class__).index(item))
        return {
            self.id: ', '.join([item.value for item in sorted_items]),
            self.id.replace('txtValue', 'divDropDown$ctl01$HiddenIndices'): ','.join([str(list(item.__class__).index(item)) for item in sorted_items])
        }

class UniEnumDropdown(BaseModel):
    item: Enum
    id: str
    label: str

    def to_payload_items(self) -> dict:
        if isinstance(self.item, Enum):
            return {self.id: str(list(self.item.__class__).index(self.item)+1)}
        else:
            raise ValueError(f'Invalid item type: {type(self.item)}')
        
class UniYearDropdown(BaseModel):
    item: IndexedYearAnnotated
    id: str
    label: str

    @field_validator('item', mode='after')
    def parse_item_as_indexed_year(cls, v: str) -> str:
        if isinstance(v, int):
            return IndexedYear(v)
        return v

    def to_payload_items(self) -> dict:
        if isinstance(self.item, IndexedYear):
            return {self.id: str(self.item.index()+1)}
        else:
            raise ValueError(f'Invalid item type: {type(self.item)}')
    
class BoolRadioButton(BaseModel):
    selected: bool
    id: str
    label: str

    def to_payload_items(self) -> list[dict]:
        if isinstance(self.selected, bool):
            return {self.id: f'rb{self.selected}'}
        else:
            raise ValueError(f'Invalid `selected` type: {type(self.selected)}')
    
class NullableText(BaseModel):
    text: Optional[str] = None
    id: str
    label: str

    def to_payload_items(self) -> list[dict[str, Optional[str]]]:
        if self.text is None:
            return {
                self.id: '',
                self.id.replace('txtValue', 'cbNull'): 'on'
            }
        return {
            self.id: self.text,
            self.id.replace('txtValue', 'cbNull'): 'off'
        }
    
class SchemeEnum(str, Enum):
    rego = 'REGO'
    ro = 'RO'

class TechnologyGroupEnum(str, Enum):
    aerothermal = 'Aerothermal'
    biodegradable = 'Biodegradable'
    biogas = 'Biogas'
    biomass = 'Biomass'
    biomass_50kw_dnc_or_less = 'Biomass 50kW DNC or less'
    biomass_using_act = 'Biomass using an Advanced Conversion Technology'
    chp_energy_from_waste = 'CHP Energy from Waste'
    co_firing_biomass_fossil = 'Co-firing of Biomass with Fossil Fuel'
    co_firing_energy_crops = 'Co-firing of Energy Crops'
    filled_storage_hydro = 'Filled Storage Hydro'
    filled_storage_system = 'Filled Storage System'
    fuelled = 'Fuelled'
    geopressure = 'Geopressure'
    geothermal = 'Geothermal'
    hydro = 'Hydro'
    hydro_20mw_dnc_or_less = 'Hydro 20MW DNC or less'
    hydro_50kw_dnc_or_less = 'Hydro 50kW DNC or less'
    hydro_greater_than_20mw_dnc = 'Hydro greater than 20MW DNC'
    hydrothermal = 'Hydrothermal'
    landfill_gas = 'Landfill Gas'
    micro_hydro = 'Micro Hydro'
    ocean_energy = 'Ocean Energy'
    off_shore_wind = 'Off-shore Wind'
    on_shore_wind = 'On-shore Wind'
    photovoltaic = 'Photovoltaic'
    photovoltaic_50kw_dnc_or_less = 'Photovoltaic 50kW DNC or less'
    sewage_gas = 'Sewage Gas'
    solar_and_on_shore_wind = 'Solar and On-shore Wind'
    tidal_flow = 'Tidal Flow'
    tidal_power = 'Tidal Power'
    waste_using_act = 'Waste using an Advanced Conversion Technology'
    wave_power = 'Wave Power'
    wind = 'Wind'
    wind_50kw_dnc_or_less = 'Wind 50kW DNC or less'

class RoOrderEnum(str, Enum):
    na = 'N/A'
    niro = 'NIRO'
    ro = 'RO'
    ros = 'ROS'

class GenerationTypeEnum(str, Enum):
    ad = 'AD'
    advanced_gasification = 'Advanced gasification'
    biomass = 'Biomass (e.g. Plant or animal matter)'
    biomass_using_act = 'Biomass using an Advanced Conversion Technology'
    co_firing_biomass = 'Co-firing of biomass'
    co_firing_biomass_fossil = 'Co-firing of biomass with fossil fuel'
    co_firing_energy_crops = 'Co-firing of energy crops'
    co_firing_regular_bioliquid = 'Co-firing of regular bioliquid'
    dedicated_biomass = 'Dedicated biomass'
    dedicated_biomass_bl = 'Dedicated biomass - BL'
    dedicated_biomass_with_chp = 'Dedicated biomass with CHP'
    dedicated_biomass_with_chp_bl = 'Dedicated biomass with CHP - BL'
    dedicated_energy_crops = 'Dedicated energy crops'
    dedicated_energy_crops_with_chp = 'Dedicated energy crops with CHP'
    electricity_from_landfill_gas = 'Electricity generated from landfill gas'
    electricity_from_sewage_gas = 'Electricity generated from sewage gas'
    energy_from_waste_with_chp = 'Energy from waste with CHP'
    high_range_co_firing = 'High-range co-firing'
    low_range_co_firing_rec = 'Low range co-firing of relevant energy crop'
    low_range_co_firing = 'Low-range co-firing'
    mid_range_co_firing = 'Mid-range co-firing'
    na = 'N/A'
    standard_gasification = 'Standard gasification'
    station_conversion = 'Station conversion'
    station_conversion_bl = 'Station conversion - BL'
    unit_conversion = 'Unit conversion'
    unspecified = 'Unspecified'
    waste_using_act = 'Waste using an Advanced Conversion Technology'

class CountryEnum(str, Enum):
    england = 'England'
    northern_ireland = 'Northern Ireland'
    scotland = 'Scotland'
    wales = 'Wales'

class GeneratingStationEnum(str, Enum):
    all = '<ALL>'

class OutputTypeEnum(str, Enum):
    general = 'General'
    nffo = 'NFFO'
    amo = 'AMO'

class CertificateStatusEnum(str, Enum):
    issued = 'Issued'
    revoked = 'Revoked'
    retired = 'Retired'
    redeemed = 'Redeemed'
    expired = 'Expired'

class CurrentHolderOrganisationNameEnum(str, Enum):
    all = '<ALL>'

class ShowAgentGroupsEnum(str, Enum):
    generating_stations_and_agent_groups = 'Generating Stations and Agent Groups'
    agent_groups = 'Agent Groups'
    generating_stations = 'Generating Stations'

class OutputPeriodMonth(str, Enum):
    jan = 'Jan'
    feb = 'Feb'
    mar = 'Mar'
    apr = 'Apr'
    may = 'May'
    jun = 'Jun'
    jul = 'Jul'
    aug = 'Aug'
    sep = 'Sep'
    oct = 'Oct'
    nov = 'Nov'
    dec = 'Dec'

class PageSizeEnum(str, Enum):
    _25 = '25'
    _50 = '50'
    _100 = '100'
    _200 = '200'
    

class Scheme(MultiEnumDropdown):
    items: list[SchemeEnum] = [enum for enum in SchemeEnum]
    id: str = 'ReportViewer$ctl04$ctl03$txtValue'
    label: str = 'Scheme'

class TechnologyGroup(MultiEnumDropdown):
    items: list[TechnologyGroupEnum] = [enum for enum in TechnologyGroupEnum]
    id: str = 'ReportViewer$ctl04$ctl05$txtValue'
    label: str = 'Technology Group'

class RoOrder(MultiEnumDropdown):
    items: list[RoOrderEnum] = [enum for enum in RoOrderEnum]
    id: str = 'ReportViewer$ctl04$ctl07$txtValue'
    label: str = 'RO Order'

class GenerationType(MultiEnumDropdown):
    items: list[GenerationTypeEnum] = [enum for enum in GenerationTypeEnum]
    id: str = 'ReportViewer$ctl04$ctl09$txtValue'
    label: str = 'Generation Type'

class Country(MultiEnumDropdown):
    items: list[CountryEnum] = [enum for enum in CountryEnum]
    id: str = 'ReportViewer$ctl04$ctl11$txtValue'
    label: str = 'Country'

    def to_payload_items(self) -> list[dict]:
        """N.b. the countries have a non-standard index"""
        sorted_items = sorted(self.items, key=lambda item: list(item.__class__).index(item))
        return {
            self.id: ', '.join([item.value.replace(' ', '\xa0') for item in sorted_items]),
            self.id.replace('txtValue', 'divDropDown$ctl01$HiddenIndices'): ','.join([str([2, 4, 5, 7][list(item.__class__).index(item)]) for item in sorted_items])
        }

class GeneratingStation(MultiEnumDropdown):
    items: list[GeneratingStationEnum] = [GeneratingStationEnum.all]
    id: str = 'ReportViewer$ctl04$ctl17$txtValue'
    label: str = 'Generating Station'

class OutputType(MultiEnumDropdown):
    items: list[OutputTypeEnum] = [enum for enum in OutputTypeEnum]
    id: str = 'ReportViewer$ctl04$ctl27$txtValue'
    label: str = 'Output Type'

class CertificateStatus(MultiEnumDropdown):
    items: list[CertificateStatusEnum] = [enum for enum in CertificateStatusEnum]
    id: str = 'ReportViewer$ctl04$ctl31$txtValue'
    label: str = 'Certificate Status'

class CurrentHolderOrganisationName(MultiEnumDropdown):
    items: list[CurrentHolderOrganisationNameEnum] = [CurrentHolderOrganisationNameEnum.all]
    id: str = 'ReportViewer$ctl04$ctl37$txtValue'
    label: str = 'Current Holder Organisation Name'

class ShowAgentGroups(UniEnumDropdown):
    item: ShowAgentGroupsEnum = ShowAgentGroupsEnum.generating_stations_and_agent_groups
    id: str = 'ReportViewer$ctl04$ctl13$ddValue'
    label: str = 'Show Agent Groups'

class OutputPeriodYearFrom(UniYearDropdown):
    item: IndexedYearAnnotated
    id: str = 'ReportViewer$ctl04$ctl19$ddValue'
    label: str = 'Output Period "Year From"'

class OutputPeriodYearTo(UniYearDropdown):
    item: IndexedYearAnnotated
    id: str = 'ReportViewer$ctl04$ctl21$ddValue'
    label: str = 'Output Period "Year To"'

class OutputPeriodMonthFrom(UniEnumDropdown):
    item: OutputPeriodMonth
    id: str = 'ReportViewer$ctl04$ctl23$ddValue'
    label: str = 'Output Period "Month From"'

class OutputPeriodMonthTo(UniEnumDropdown):
    item: OutputPeriodMonth
    id: str = 'ReportViewer$ctl04$ctl25$ddValue'
    label: str = 'Output Period "Month To"'

class PageSize(UniEnumDropdown):
    item: PageSizeEnum
    id: str = 'ReportViewer$ctl04$ctl39$ddValue'
    label: str = 'Page Size'

class ShowAllOrganisations(BoolRadioButton):
    selected: bool = True
    id: str = 'ReportViewer$ctl04$ctl35$ReportViewer_ctl04_ctl35'
    label: str = 'Show All Organisations'

class ShowAllGenerators(BoolRadioButton):
    selected: bool = True
    id: str = 'ReportViewer$ctl04$ctl15$ReportViewer_ctl04_ctl15'
    label: str = 'Show All Generators'
    
class AccreditationNo(NullableText):
    text: Optional[str] = None
    id: str = 'ReportViewer$ctl04$ctl29$txtValue'
    label: str = 'Accreditation No'

class CertificateNo(NullableText):
    text: Optional[str] = None
    id: str = 'ReportViewer$ctl04$ctl33$txtValue'
    label: str = 'Certificate No.'


class CertificatesFilter(BaseModel):
    scheme: Scheme = Scheme()
    technology_group: TechnologyGroup = TechnologyGroup()
    ro_order: RoOrder = RoOrder()
    generation_type: GenerationType = GenerationType()
    country: Country = Country()
    generating_station: GeneratingStation = GeneratingStation()
    output_type: OutputType = OutputType()
    certificate_status: CertificateStatus = CertificateStatus()
    current_holder_organisation_name: CurrentHolderOrganisationName = CurrentHolderOrganisationName()
    show_agent_groups: ShowAgentGroups = ShowAgentGroups(item=ShowAgentGroupsEnum.generating_stations_and_agent_groups)
    output_year_from: OutputPeriodYearFrom = OutputPeriodYearFrom(item=2024)
    output_year_to: OutputPeriodYearTo = OutputPeriodYearTo(item=2025)
    output_month_from: OutputPeriodMonthFrom = OutputPeriodMonthFrom(item=OutputPeriodMonth.apr)
    output_month_to: OutputPeriodMonthTo = OutputPeriodMonthTo(item=OutputPeriodMonth.mar)
    page_size: PageSize = PageSize(item=PageSizeEnum._25)
    show_all_organisations: ShowAllOrganisations = ShowAllOrganisations(selected=True)
    show_all_generators: ShowAllGenerators = ShowAllGenerators(selected=True)
    accreditation_no: AccreditationNo = AccreditationNo()
    certificate_no: CertificateNo = CertificateNo()

    def to_payload_items(
        self, 
        soup_in_1: bs, 
        soup_in_2: Optional[bs] = None, 
        stage: Literal[1, 2] = 1
    ) -> dict[str, Optional[str]]:
        def get_hidden_inputs(soup: bs) -> dict[str, Optional[str]]:
            hidden_inputs = [
                input_elem 
                for input_elem 
                in soup.find_all('input', type='hidden')
                if 'id' in input_elem.attrs and 'HiddenIndices' not in input_elem['id']
            ]

            return {
                hidden_input['id'].replace('_', '$').replace('$$', '__'): (hidden_input['value'] if 'value' in hidden_input.attrs else '')
                for hidden_input
                in hidden_inputs
            }
        
        payload = {}

        for _, field_value in self:
            payload.update(field_value.to_payload_items())
        
        payload.update(get_hidden_inputs(soup_in_1))

        payload.update({
            '__ASYNCPOST': 'true',
            'ReportViewer$ctl11': 'standards',
            'ReportViewer$ctl05$ctl00$CurrentPage': '1',
            'ReportViewer$ctl09$VisibilityState$ctl00': 'ReportPage',
        })

        if stage == 1:
            payload.pop('ReportViewer$ctl10')
            payload.update({
                'ReportViewer$ctl04$ctl00': 'View Report',
                'ScriptManager1': 'ScriptManager1|ReportViewer$ctl04$ctl00',
            })
        elif stage == 2:
            assert soup_in_2 is not None, '`soup_in_2` must not be None if `stage`==2'
            payload.update({
                '__VIEWSTATE': str(soup_in_2).split('__VIEWSTATE')[1].lstrip('|').split('|')[0],
                '__EVENTTARGET': 'ReportViewer$ctl09$Reserved_AsyncLoadTarget',
                'ScriptManager1': 'ScriptManager1|ReportViewer$ctl09$Reserved_AsyncLoadTarget',
                'ReportViewer$ctl10': 'ltr',
            })
        else:
            raise ValueError('`stage` should be 1 or 2')


        for param_key in [
            'ReportViewer$ToggleParam$store',
            'ReportViewer$ctl03$ctl00',
            'ReportViewer$ctl03$ctl01',
            'ReportViewer$ctl04$ctl29$txtValue',
            'ReportViewer$ctl04$ctl33$txtValue',
            'ReportViewer$ctl05$ctl00$CurrentPage',
            'ReportViewer$ctl07$store',
            'ReportViewer$ctl08$ClientClickedId',
            'ReportViewer$ctl09$ScrollPosition',
            'hdnCookieAcceptanceRefreshDate',
            'hdnCookieAcceptanceRefreshDay',
            'hdnCookieAcceptanceRefreshMonth',
            'hdnCookieConsent'
            ]:
                if param_key in payload:
                    payload.pop(param_key)

        payload['ReportViewer$ctl04$ctl05$txtValue'] = payload['ReportViewer$ctl04$ctl05$txtValue'].replace(" ", "\xa0").replace(',\xa0', ', ')
        payload['ReportViewer$ctl04$ctl09$txtValue'] = payload['ReportViewer$ctl04$ctl09$txtValue'].replace(" ", "\xa0").replace(',\xa0', ', ')
        payload['ReportViewer$ctl09$VisibilityState$ctl00'] = 'None'

        return payload
