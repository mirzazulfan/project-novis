# Generated by Django 2.1.7 on 2019-03-19 12:23

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import project_novis.callsign.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressLocationCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('address', models.CharField(db_index=True, max_length=256)),
                ('provider', models.CharField(db_index=True, max_length=64)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='CallSign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('name', project_novis.callsign.utils.CallSignField(db_index=True, max_length=16, unique=True)),
                ('cq_zone', project_novis.callsign.utils.CQZoneField(blank=True, null=True, verbose_name='CQ zone')),
                ('itu_zone', project_novis.callsign.utils.ITUZoneField(blank=True, null=True, verbose_name='ITU zone')),
                ('itu_region', project_novis.callsign.utils.ITURegionField(blank=True, null=True, verbose_name='ITU region')),
                ('type', models.CharField(blank=True, choices=[('beacon', 'Beacon'), ('club', 'Club'), ('educational', 'Educational'), ('experimental', 'Experimental'), ('personal', 'Personal'), ('repeater', 'Repeater'), ('shortwave_listener', 'Shortwave Listener'), ('special_event', 'Special Event')], max_length=32)),
                ('active', models.BooleanField(default=True)),
                ('issued', models.DateField(blank=True, null=True)),
                ('expired', models.DateField(blank=True, null=True)),
                ('license_type', models.CharField(blank=True, max_length=64)),
                ('dstar', models.BooleanField(default=False, verbose_name='D-STAR')),
                ('identifier', models.CharField(blank=True, max_length=128, null=True, unique=True, verbose_name='Optional identifier')),
                ('website', models.URLField(blank=True, max_length=128, null=True)),
                ('comment', models.TextField(blank=True)),
                ('_official_validated', models.BooleanField(default=False, help_text='Callsign is validated by a government agency')),
                ('_location_source', models.CharField(blank=True, choices=[('user', 'User'), ('official', 'Official'), ('unofficial', 'Unofficial'), ('prefix', 'Prefix')], max_length=32)),
                ('lotw_last_activity', models.DateTimeField(blank=True, null=True, verbose_name='LOTW last activity')),
                ('eqsl', models.BooleanField(default=False)),
                ('internal_comment', models.TextField(blank=True)),
                ('source', models.CharField(blank=True, max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CallsignBlacklist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('callsign', project_novis.callsign.utils.CallSignField(db_index=True, max_length=16, unique=True)),
                ('reason', models.CharField(blank=True, choices=[('invalid', 'Invalid Callsign'), ('abuse', 'Abuse'), ('other', 'Other')], max_length=128)),
                ('submitter', models.CharField(blank=True, max_length=128)),
                ('submitter_email', models.EmailField(blank=True, max_length=128)),
                ('message', models.TextField(blank=True)),
                ('approved', models.NullBooleanField(default=None)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CallSignPrefix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(db_index=True, max_length=16, unique=True)),
                ('cq_zone', project_novis.callsign.utils.CQZoneField(blank=True, null=True, verbose_name='CQ zone')),
                ('itu_zone', project_novis.callsign.utils.ITUZoneField(blank=True, null=True, verbose_name='ITU zone')),
                ('itu_region', project_novis.callsign.utils.ITURegionField(blank=True, null=True, verbose_name='ITU region')),
                ('continent', models.CharField(blank=True, choices=[('AF', 'Asia'), ('AN', 'Antarctica'), ('AS', 'Africa'), ('EU', 'Europe'), ('NA', 'North America'), ('OC', 'Oceania'), ('SA', 'South America')], max_length=2)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('utc_offset', models.FloatField(blank=True, null=True, verbose_name='UTC offset')),
                ('type', models.CharField(blank=True, choices=[('beacon', 'Beacon'), ('club', 'Club'), ('educational', 'Educational'), ('experimental', 'Experimental'), ('personal', 'Personal'), ('repeater', 'Repeater'), ('shortwave_listener', 'Shortwave Listener'), ('special_event', 'Special Event')], max_length=32)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('description', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('callsign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='callsign.CallSign')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clubs', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='members', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClublogUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('clublog_first_qso', models.DateTimeField(blank=True, null=True, verbose_name='Clublog first QSO')),
                ('clublog_last_qso', models.DateTimeField(blank=True, null=True, verbose_name='Clublog last QSO')),
                ('clublog_last_upload', models.DateTimeField(blank=True, null=True)),
                ('clublog_oqrs', models.NullBooleanField(verbose_name='Clublog OQRS')),
                ('callsign', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='callsign.CallSign')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(db_index=True, max_length=64, unique=True)),
                ('alpha_2', models.CharField(db_index=True, help_text='ISO 3166-1 alpha-2 – two-letter country code', max_length=2, unique=True)),
                ('alpha_3', models.CharField(db_index=True, help_text='ISO 3166-1 alpha-3 – three-letter country code', max_length=3, unique=True)),
                ('numeric_3', models.CharField(db_index=True, help_text='ISO 3166-1 numeric – three-digit country code', max_length=3, unique=True)),
                ('wikidata_object', project_novis.callsign.utils.WikidataObjectField(db_index=True, unique=True)),
                ('adif_name', models.CharField(blank=True, db_index=True, help_text='Amateur Data Interchange Format (ADIF) country name', max_length=64, null=True, verbose_name='ADIF name')),
                ('geonames_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='Geonames ID')),
                ('osm_relation_id', models.PositiveIntegerField(blank=True, help_text='OpenStreetMap relation ID', null=True, verbose_name='OSM relation ID')),
                ('itu_object_identifier', models.CharField(blank=True, help_text='International Telecommunication Union (ITU) object identifier', max_length=16, null=True, verbose_name='ITU object identifier')),
                ('itu_letter_code', models.CharField(blank=True, help_text='International Telecommunication Union (ITU) letter code', max_length=3, null=True, verbose_name='ITU letter code')),
                ('fips', models.CharField(blank=True, help_text='Federal Information Processing Standards (FIPS) 10-4 standard country code', max_length=2, null=True, verbose_name='FIPS')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DataImport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('start', models.DateTimeField()),
                ('task', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
                ('optional_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('stop', models.DateTimeField(blank=True, null=True)),
                ('callsigns', models.PositiveIntegerField(default=0)),
                ('new_callsigns', models.PositiveIntegerField(default=0)),
                ('updated_callsigns', models.PositiveIntegerField(default=0)),
                ('deleted_callsigns', models.PositiveIntegerField(default=0)),
                ('invalid_callsigns', models.PositiveIntegerField(default=0)),
                ('blacklisted_callsigns', models.PositiveIntegerField(default=0)),
                ('errors', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DMRID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.PositiveIntegerField(db_index=True, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('issued', models.DateTimeField(blank=True, null=True)),
                ('comment', models.TextField(blank=True)),
                ('callsign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dmr_ids', to='callsign.CallSign')),
            ],
            options={
                'verbose_name': 'DMR ID',
            },
        ),
        migrations.CreateModel(
            name='DXCCEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('deleted', models.BooleanField(default=False)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='callsign.Country')),
            ],
            options={
                'verbose_name': 'DXCC Entry',
                'verbose_name_plural': 'DXCC Entries',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('identifier', models.CharField(db_index=True, max_length=128)),
                ('source', models.CharField(db_index=True, max_length=128)),
                ('name', models.CharField(db_index=True, max_length=128)),
                ('address', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=128)),
                ('state', models.CharField(blank=True, max_length=128)),
                ('email', models.EmailField(blank=True, max_length=128, null=True)),
                ('comment', models.TextField(blank=True)),
                ('optional_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('callsigns', models.ManyToManyField(blank=True, to='callsign.CallSign')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='callsign.Country')),
            ],
        ),
        migrations.CreateModel(
            name='QSO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True)),
                ('frequency', models.DecimalField(decimal_places=6, max_digits=18)),
                ('mode', models.CharField(blank=True, choices=[('am', 'AM'), ('fm', 'FM'), ('dstar', 'D-STAR'), ('dmr', 'DMR'), ('ssb', 'SSB'), ('cw', 'CW'), ('psk125', 'PSK125'), ('PSK31', 'PSK31'), ('psk63', 'PSK63'), ('rtty', 'RTTY')], max_length=16)),
                ('comment', models.CharField(blank=True, max_length=128)),
                ('callee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='callee', to='callsign.CallSign')),
                ('caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='caller', to='callsign.CallSign')),
            ],
        ),
        migrations.CreateModel(
            name='Repeater',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('active', models.BooleanField(default=True)),
                ('website', models.URLField(blank=True, max_length=400, null=True)),
                ('altitude', models.FloatField(blank=True, null=True)),
                ('description', models.TextField(blank=True)),
                ('source', models.CharField(blank=True, max_length=256)),
                ('callsign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='callsign.CallSign')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='repeaters', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TelecommunicationAgency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(help_text='English Name', max_length=128, unique=True)),
                ('original_name', models.CharField(blank=True, max_length=128)),
                ('original_name_short', models.CharField(blank=True, max_length=32)),
                ('url', models.URLField(blank=True, max_length=256, null=True, verbose_name='URL')),
                ('description', models.TextField(blank=True, null=True)),
                ('callsign_data_url', models.URLField(blank=True, max_length=256, null=True, verbose_name='Callsign data URL')),
                ('callsign_data_description', models.TextField(blank=True, null=True)),
                ('used_for_official_callsign_import', models.BooleanField(default=False)),
                ('country', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='callsign.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transmitter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('active', models.BooleanField(default=True)),
                ('transmit_frequency', models.DecimalField(decimal_places=6, max_digits=18)),
                ('offset', models.DecimalField(decimal_places=6, max_digits=18)),
                ('mode', models.CharField(choices=[('am', 'AM'), ('fm', 'FM'), ('dstar', 'D-STAR'), ('dmr', 'DMR'), ('ssb', 'SSB'), ('cw', 'CW'), ('psk125', 'PSK125'), ('PSK31', 'PSK31'), ('psk63', 'PSK63'), ('rtty', 'RTTY')], max_length=16)),
                ('pep', models.FloatField(blank=True, help_text='Peak Envelope Power', null=True, verbose_name='PEP')),
                ('description', models.TextField(blank=True, null=True)),
                ('hardware', models.CharField(blank=True, max_length=256)),
                ('ctcss', models.FloatField(blank=True, choices=[(67.0, '67.0 Hz'), (69.3, '69.3 Hz'), (71.9, '71.9 Hz'), (74.4, '74.4 Hz'), (77.0, '77.0 Hz'), (79.7, '79.7 Hz'), (82.5, '82.5 Hz'), (85.4, '85.4 Hz'), (88.5, '88.5 Hz'), (91.5, '91.5 Hz'), (94.8, '94.8 Hz'), (97.4, '97.4 Hz'), (100.0, '100.0 Hz'), (103.5, '103.5 Hz'), (107.2, '107.2 Hz'), (110.9, '110.9 Hz'), (114.8, '114.8 Hz'), (118.8, '118.8 Hz'), (123.0, '123.0 Hz'), (127.3, '127.3 Hz'), (131.8, '131.8 Hz'), (136.5, '136.5 Hz'), (141.3, '141.3 Hz'), (146.2, '146.2 Hz'), (150.0, '150.0 Hz'), (151.4, '151.4 Hz'), (156.7, '156.7 Hz'), (159.8, '159.8 Hz'), (162.2, '162.2 Hz'), (165.5, '165.5 Hz'), (167.9, '167.9 Hz'), (171.3, '171.3 Hz'), (173.8, '173.8 Hz'), (177.3, '177.3 Hz'), (179.9, '179.9 Hz'), (183.5, '183.5 Hz'), (186.2, '186.2 Hz'), (189.9, '189.9 Hz'), (192.8, '192.8 Hz'), (196.6, '196.6 Hz'), (199.5, '199.5 Hz'), (203.5, '203.5 Hz'), (206.5, '206.5 Hz'), (210.7, '210.7 Hz'), (213.8, '213.8 Hz'), (218.1, '218.1 Hz'), (221.3, '221.3 Hz'), (225.7, '225.7 Hz'), (229.1, '229.1 Hz'), (233.6, '233.6 Hz'), (237.1, '237.1 Hz'), (241.8, '241.8 Hz'), (245.5, '245.5 Hz'), (250.3, '250.3 Hz'), (254.1, '254.1 Hz')], help_text='Continuous Tone Coded Squelch System', null=True, verbose_name='CTCSS')),
                ('echolink', models.IntegerField(blank=True, null=True)),
                ('colorcode', models.SmallIntegerField(blank=True, null=True)),
                ('source', models.CharField(blank=True, max_length=256)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transmitters', to=settings.AUTH_USER_MODEL)),
                ('dmr_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transmitters', to='callsign.DMRID', verbose_name='DMR ID')),
                ('repeater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transmitters', to='callsign.Repeater')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='person',
            name='telco_agency',
            field=models.ForeignKey(blank=True, help_text='Related telecommunication agency', null=True, on_delete=django.db.models.deletion.PROTECT, to='callsign.TelecommunicationAgency'),
        ),
        migrations.AddField(
            model_name='callsignprefix',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='callsign.Country'),
        ),
        migrations.AddField(
            model_name='callsignprefix',
            name='dxcc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='callsign.DXCCEntry', verbose_name='DXCC'),
        ),
        migrations.AddField(
            model_name='callsign',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='callsign.Country'),
        ),
        migrations.AddField(
            model_name='callsign',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='callsigns', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='callsign',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='callsign',
            name='prefix',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='callsign.CallSignPrefix'),
        ),
        migrations.AlterUniqueTogether(
            name='addresslocationcache',
            unique_together={('address', 'provider')},
        ),
        migrations.AlterUniqueTogether(
            name='qso',
            unique_together={('caller', 'callee', 'timestamp')},
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together={('identifier', 'source')},
        ),
        migrations.AlterUniqueTogether(
            name='dxccentry',
            unique_together={('name', 'deleted')},
        ),
    ]
