from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied, ValidationError

from .enums import CALLSIGN_TYPES, CONTINENTS, CTCSS, RF_MODES, BLACKLIST_REASONS
from .utils import CallSignField, CQZoneField, ITUZoneField, ITURegionField, WikidataObjectField, generate_aprs_passcode, point_to_grid, grid_to_point


class BaseModel(models.Model):
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)

    class Meta:
        abstract = True


class LocationBaseModel(BaseModel):
    location = models.PointField(null=True, blank=True)

    class Meta:
        abstract = True

    def _grid(self, high_accuracy: bool = True) -> str:
        if not self.location:
            return ""

        return point_to_grid(self.location, high_accuracy=high_accuracy)

    @property
    def grid(self):
        return self._grid(high_accuracy=True)

    @grid.setter
    def grid(self, grid: str):
        self.location = grid_to_point(grid)

    @property
    def aprs_fi_url(self) -> str:
        return f"https://aprs.fi/#!addr={self.grid}"

    # @property
    # def cq_zone(self) -> int:
    #     raise NotImplementedError
    #
    # @property
    # def itu_zone(self) -> int:
    #     raise NotImplementedError
    #
    # @property
    # def itu_region(self) -> int:
    #     raise NotImplementedError
    #
    # @property
    # def continent(self) -> str:
    #     raise NotImplementedError
    #
    # @property
    # def dxcc(self) -> int:
    #     raise NotImplementedError
    #
    # @property
    # def country(self) -> str:
    #     raise NotImplementedError
    #
    # @property
    # def utc_offset(self) -> int:
    #     raise NotImplementedError


class Country(BaseModel):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    alpha_2 = models.CharField(max_length=2, unique=True, db_index=True)
    alpha_3 = models.CharField(max_length=3, unique=True, db_index=True)
    numeric_3 = models.CharField(max_length=3, unique=True, db_index=True)
    wikidata_object = WikidataObjectField(unique=True, db_index=True)

    # Additional Information
    adif_name = models.CharField("ADIF name", max_length=64, db_index=True, blank=True, null=True)
    geonames_id = models.PositiveIntegerField("Geonames ID", null=True, blank=True)
    osm_relation_id = models.PositiveIntegerField("OSM relation ID", null=True, blank=True)
    itu_object_identifier = models.CharField("ITU object identifier", max_length=16, blank=True, null=True)
    itu_letter_code = models.CharField("ITU letter code", max_length=3, blank=True, null=True)
    fips = models.CharField("FIPS", max_length=2, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    @property
    def wikidata_url(self) -> str:
        return f"https://www.wikidata.org/wiki/{self.wikidata_object}"

    @property
    def geonames_url(self) -> str:
        if self.geonames_id:
            return f"https://www.geonames.org/{self.geonames_id}"
        else:
            return ""

    @property
    def osm_relation_url(self) -> str:
        if self.osm_relation_id:
            return f"https://www.openstreetmap.org/relation/{self.osm_relation_id}"
        else:
            return ""

    @property
    def world_fact_book_url(self) -> str:
        if self.fips:
            return f"https://www.cia.gov/library/publications/the-world-factbook/geos/{self.fips}.html"
        else:
            return ""


class DXCCEntry(BaseModel):
    name = models.CharField(max_length=64, db_index=True)
    deleted = models.BooleanField(default=False)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "DXCC Entry"
        verbose_name_plural = "DXCC Entries"
        unique_together = ("name", "deleted")


class CallSignPrefix(BaseModel):
    name = models.CharField(max_length=16, unique=True, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True)
    dxcc = models.ForeignKey(DXCCEntry, on_delete=models.PROTECT, null=True, blank=True)
    cq_zone = CQZoneField("CQ zone", null=True, blank=True)
    itu_zone = ITUZoneField("ITU zone", null=True, blank=True)
    itu_region = ITURegionField("ITU region", null=True, blank=True)
    continent = models.CharField(choices=CONTINENTS, max_length=2, blank=True)
    location = models.PointField(null=True, blank=True)
    utc_offset = models.FloatField("UTC offset", null=True, blank=True)
    type = models.CharField(choices=CALLSIGN_TYPES, max_length=32, blank=True)

    def __str__(self) -> str:
        return self.name


class CallSignManager(models.Manager):
    def create_callsign(self, callsign: str, check_blacklist: bool = True):
        # Check if callsign is blacklisted
        if check_blacklist and CallsignBlacklist.objects.filter(callsign=callsign).exists():
            raise ValidationError("callsign is blacklisted")

        callsign = self.create(name=callsign)
        callsign.set_default_meta_data()
        callsign.save()
        return callsign


class CallSign(LocationBaseModel):
    name = CallSignField(unique=True, db_index=True)
    prefix = models.ForeignKey(CallSignPrefix, on_delete=models.PROTECT, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True)
    cq_zone = CQZoneField("CQ zone", null=True, blank=True)
    itu_zone = ITUZoneField("ITU zone", null=True, blank=True)
    itu_region = ITURegionField("ITU region", null=True, blank=True)
    type = models.CharField(choices=CALLSIGN_TYPES, max_length=32, blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    issued = models.DateField(null=True, blank=True)
    expired = models.DateField(null=True, blank=True)
    license_type = models.CharField(max_length=64, blank=True)
    dstar = models.BooleanField("D-STAR", default=False)
    identifier = models.CharField(_("Optional identifier"), max_length=128, unique=True, blank=True, null=True)
    website = models.URLField(max_length=128, blank=True, null=True)
    comment = models.TextField(blank=True)
    _official_validated = models.BooleanField(default=False, help_text="Callsign is validated by a government agency")

    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name="callsigns")
    internal_comment = models.TextField(blank=True)
    source = models.CharField(max_length=256, blank=True)
    objects = CallSignManager()

    # TODO(elnappo) make sure a user can not change his name after validation

    def __str__(self) -> str:
        return self.name

    def set_default_meta_data(self):
        call_sign = self.name
        while call_sign:
            if CallSignPrefix.objects.filter(name=call_sign).exists():
                prefix = CallSignPrefix.objects.get(name=call_sign)
                self.prefix = prefix
                self.country = prefix.country
                self.cq_zone = prefix.cq_zone
                self.itu_zone = prefix.itu_zone
                self.location = prefix.location
                break
            else:
                call_sign = call_sign[:-1]

    def get_absolute_url(self):
        return reverse('callsign:callsign-html-detail', args=[self.name])

    @property
    def aprs_passcode(self) -> int:
        if self.official_validated == "false" or self.type == "shortwave_listener":
            # Not a good idea to raise an exception here?
            raise PermissionDenied("callsign is not official assigned or is shortwave listener")
        return generate_aprs_passcode(self.name)

    @property
    def official_validated(self) -> str:
        if self.country and self.country.telecommunicationagency.used_for_official_callsign_import and self._official_validated:
            return "true"
        elif self.country and self.country.telecommunicationagency.used_for_official_callsign_import and not self._official_validated:
            return "false"
        else:
            return "unknown"

    @property
    def location_source(self) -> str:
        if self.location == self.prefix.location:
            return "prefix"
        else:
            return "user"

    @property
    def grid(self):
        if self.location_source == "prefix":
            return self._grid(high_accuracy=False)
        else:
            return self._grid(high_accuracy=True)

    @property
    def eqsl_profile_url(self) -> str:
        return f"https://www.eqsl.cc/Member.cfm?{ self.name }"

    @property
    def clublog_profile_url(self) -> str:
        return f"https://secure.clublog.org/logsearch/{ self.name }"

    @property
    def dxheat_profile_url(self) -> str:
        return f"https://dxheat.com/db/{ self.name }"

    @property
    def aprsfi_profile_url(self) -> str:
        return f"https://aprs.fi/info/?call={ self.name }"

    @property
    def pskreporter_profile_url(self) -> str:
        return f"http://www.pskreporter.de/table?call={ self.name }"

    @property
    def qrz_profile_url(self) -> str:
        return f"https://www.qrz.com/db/{ self.name }"

    @property
    def hamqth_profile_url(self) -> str:
        return f"https://www.hamqth.com/{ self.name }"

    @property
    def hamcall_profile_url(self) -> str:
        return f"https://hamcall.net/call?callsign={ self.name }"




class DMRID(BaseModel):
    name = models.PositiveIntegerField(unique=True, db_index=True)
    callsign = models.ForeignKey(CallSign, related_name='dmr_ids', on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    issued = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    @property
    def brandmeister_profile_url(self) -> str:
        if self.callsign:
            return f"https://brandmeister.network/index.php?page=profile&call={ self.callsign.name }"
        else:
            return ""

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = _("DMR ID")


class Club(BaseModel):
    callsign = models.ForeignKey(CallSign, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    members = models.ManyToManyField(get_user_model(), related_name="members")
    website = models.URLField(blank=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name="clubs")

    def __str__(self) -> str:
        return self.callsign.name


class LOTWUser(BaseModel):
    callsign = models.OneToOneField(CallSign, on_delete=models.CASCADE)
    lotw_last_activity = models.DateTimeField("LOTW last activity")

    def __str__(self) -> str:
        return self.callsign.name


class ClublogUser(BaseModel):
    callsign = models.OneToOneField(CallSign, on_delete=models.CASCADE)
    clublog_first_qso = models.DateTimeField("Clublog first QSO", blank=True, null=True)
    clublog_last_qso = models.DateTimeField("Clublog last QSO", blank=True, null=True)
    clublog_last_upload = models.DateTimeField(blank=True, null=True)
    clublog_oqrs = models.NullBooleanField("Clublog OQRS", lank=True, null=True)

    @property
    def profile_url(self) -> str:
        return self.callsign.clublog_profile_url

    def __str__(self) -> str:
        return self.callsign.name


class EQSLUser(BaseModel):
    callsign = models.OneToOneField(CallSign, on_delete=models.CASCADE)

    @property
    def profile_url(self) -> str:
        return self.callsign.eqsl_profile_url

    def __str__(self) -> str:
        return self.callsign.name


class Repeater(BaseModel):
    callsign = models.ForeignKey(CallSign, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    website = models.URLField(max_length=400, blank=True, null=True)
    altitude = models.FloatField(blank=True, null=True)
    location = models.PointField(blank=True, null=True)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name="repeaters")
    source = models.CharField(max_length=256, blank=True)

    def __str__(self) -> str:
        return self.callsign.name


class Transmitter(BaseModel):
    repeater = models.ForeignKey(Repeater, on_delete=models.CASCADE, related_name='transmitters')
    active = models.BooleanField(default=True)
    transmit_frequency = models.DecimalField(max_digits=18, decimal_places=6)
    offset = models.DecimalField(max_digits=18, decimal_places=6)
    mode = models.CharField(max_length=16, choices=RF_MODES)
    pep = models.FloatField("PEP", null=True, blank=True, help_text="Peak Envelope Power")
    description = models.TextField(blank=True, null=True)
    hardware = models.CharField(max_length=256, blank=True)

    # Analog
    ctcss = models.FloatField("CTCSS", choices=CTCSS, blank=True, null=True, help_text="Continuous Tone Coded Squelch System")
    echolink = models.IntegerField(blank=True, null=True)

    # Digital
    dmr_id = models.ForeignKey(DMRID, on_delete=models.PROTECT, related_name="transmitters", verbose_name="DMR ID", blank=True, null=True)
    colorcode = models.SmallIntegerField(blank=True, null=True)

    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name="transmitters")
    source = models.CharField(max_length=256, blank=True)

    @property
    def receive_frequency(self) -> Decimal:
        return self.transmit_frequency + self.offset

    @property
    def brandmeister_repeater_url(self) -> str:
        if self.dmr_id:
            return f"https://brandmeister.network/index.php?page=repeater&id={ self.dmr_id.name }"
        else:
            return ""

    def __str__(self) -> str:
        return f"{ self.repeater.callsign.name } at { self.transmit_frequency } MHz"


class TelecommunicationAgency(BaseModel):
    name = models.CharField(max_length=64, unique=True)
    country = models.OneToOneField(Country, on_delete=models.PROTECT)
    url = models.URLField("URL", max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    callsign_data_url = models.URLField("Callsign data URL", max_length=256, blank=True, null=True)
    callsign_data_description = models.TextField(blank=True, null=True)
    used_for_official_callsign_import = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Person(LocationBaseModel):
    identifier = models.CharField(max_length=128, db_index=True)
    source = models.CharField(max_length=128, db_index=True)
    callsigns = models.ManyToManyField(CallSign, blank=True)
    name = models.CharField(max_length=128, db_index=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True)
    email = models.EmailField(max_length=128, blank=True, null=True)
    telco_agency = models.ForeignKey(TelecommunicationAgency, on_delete=models.PROTECT, null=True, blank=True, help_text="Related telecommunication agency")
    comment = models.TextField(blank=True)
    optional_data = JSONField(blank=True, null=True)

    class Meta:
        unique_together = ("identifier", "source")

    def __str__(self) -> str:
        return self.name


class DataImport(BaseModel):
    start = models.DateTimeField()
    task = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    optional_data = JSONField(blank=True, null=True)

    stop = models.DateTimeField(blank=True, null=True)
    callsigns = models.PositiveIntegerField(default=0)
    new_callsigns = models.PositiveIntegerField(default=0)
    updated_callsigns = models.PositiveIntegerField(default=0)
    deleted_callsigns = models.PositiveIntegerField(default=0)
    invalid_callsigns = models.PositiveIntegerField(default=0)
    blacklisted_callsigns = models.PositiveIntegerField(default=0)
    errors = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.task}-{self.start}"

    @property
    def finished(self) -> bool:
        return bool(self.stop)

    @property
    def duration(self) -> timedelta:
        if self.stop:
            return self.stop - self.start
        else:
            return timedelta(0)


class CallsignBlacklist(BaseModel):
    callsign = CallSignField(unique=True, db_index=True)
    reason = models.CharField(max_length=128, choices=BLACKLIST_REASONS, blank=True)
    submitter = models.CharField(max_length=128, blank=True)
    submitter_email = models.EmailField(max_length=128, blank=True)
    message = models.TextField(blank=True)
    approved = models.NullBooleanField(default=None)
    comment = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.callsign

    @property
    def submitter_email_link(self) -> str:
        if self.submitter_email:
            return f"{self.submitter_email_link}?subject={self.callsign}%20Blacklist%20Request&body=Hello%20{self.submitter},%0Athank%20your%20for%20your%20request,%20"
        else:
            return ""


class AddressLocationCache(BaseModel):
    address = models.CharField(max_length=256, db_index=True)
    provider = models.CharField(max_length=64, db_index=True)
    location = models.PointField()

    class Meta:
        unique_together = ("address", "provider")

    def __str__(self) -> str:
        return self.address
