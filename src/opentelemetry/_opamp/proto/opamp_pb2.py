# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: opamp.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import anyvalue_pb2 as anyvalue__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bopamp.proto\x12\x0bopamp.proto\x1a\x0e\x61nyvalue.proto\"\xae\x05\n\rAgentToServer\x12\x14\n\x0cinstance_uid\x18\x01 \x01(\x0c\x12\x14\n\x0csequence_num\x18\x02 \x01(\x04\x12\x38\n\x11\x61gent_description\x18\x03 \x01(\x0b\x32\x1d.opamp.proto.AgentDescription\x12\x14\n\x0c\x63\x61pabilities\x18\x04 \x01(\x04\x12,\n\x06health\x18\x05 \x01(\x0b\x32\x1c.opamp.proto.ComponentHealth\x12\x36\n\x10\x65\x66\x66\x65\x63tive_config\x18\x06 \x01(\x0b\x32\x1c.opamp.proto.EffectiveConfig\x12=\n\x14remote_config_status\x18\x07 \x01(\x0b\x32\x1f.opamp.proto.RemoteConfigStatus\x12\x36\n\x10package_statuses\x18\x08 \x01(\x0b\x32\x1c.opamp.proto.PackageStatuses\x12\x36\n\x10\x61gent_disconnect\x18\t \x01(\x0b\x32\x1c.opamp.proto.AgentDisconnect\x12\r\n\x05\x66lags\x18\n \x01(\x04\x12K\n\x1b\x63onnection_settings_request\x18\x0b \x01(\x0b\x32&.opamp.proto.ConnectionSettingsRequest\x12<\n\x13\x63ustom_capabilities\x18\x0c \x01(\x0b\x32\x1f.opamp.proto.CustomCapabilities\x12\x32\n\x0e\x63ustom_message\x18\r \x01(\x0b\x32\x1a.opamp.proto.CustomMessage\x12>\n\x14\x61vailable_components\x18\x0e \x01(\x0b\x32 .opamp.proto.AvailableComponents\"\x11\n\x0f\x41gentDisconnect\"W\n\x19\x43onnectionSettingsRequest\x12:\n\x05opamp\x18\x01 \x01(\x0b\x32+.opamp.proto.OpAMPConnectionSettingsRequest\"^\n\x1eOpAMPConnectionSettingsRequest\x12<\n\x13\x63\x65rtificate_request\x18\x01 \x01(\x0b\x32\x1f.opamp.proto.CertificateRequest\"!\n\x12\x43\x65rtificateRequest\x12\x0b\n\x03\x63sr\x18\x01 \x01(\x0c\"\xbb\x01\n\x13\x41vailableComponents\x12\x44\n\ncomponents\x18\x01 \x03(\x0b\x32\x30.opamp.proto.AvailableComponents.ComponentsEntry\x12\x0c\n\x04hash\x18\x02 \x01(\x0c\x1aP\n\x0f\x43omponentsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12,\n\x05value\x18\x02 \x01(\x0b\x32\x1d.opamp.proto.ComponentDetails:\x02\x38\x01\"\xe1\x01\n\x10\x43omponentDetails\x12\'\n\x08metadata\x18\x01 \x03(\x0b\x32\x15.opamp.proto.KeyValue\x12M\n\x11sub_component_map\x18\x02 \x03(\x0b\x32\x32.opamp.proto.ComponentDetails.SubComponentMapEntry\x1aU\n\x14SubComponentMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12,\n\x05value\x18\x02 \x01(\x0b\x32\x1d.opamp.proto.ComponentDetails:\x02\x38\x01\"\xa1\x04\n\rServerToAgent\x12\x14\n\x0cinstance_uid\x18\x01 \x01(\x0c\x12\x38\n\x0e\x65rror_response\x18\x02 \x01(\x0b\x32 .opamp.proto.ServerErrorResponse\x12\x35\n\rremote_config\x18\x03 \x01(\x0b\x32\x1e.opamp.proto.AgentRemoteConfig\x12\x42\n\x13\x63onnection_settings\x18\x04 \x01(\x0b\x32%.opamp.proto.ConnectionSettingsOffers\x12:\n\x12packages_available\x18\x05 \x01(\x0b\x32\x1e.opamp.proto.PackagesAvailable\x12\r\n\x05\x66lags\x18\x06 \x01(\x04\x12\x14\n\x0c\x63\x61pabilities\x18\x07 \x01(\x04\x12>\n\x14\x61gent_identification\x18\x08 \x01(\x0b\x32 .opamp.proto.AgentIdentification\x12\x32\n\x07\x63ommand\x18\t \x01(\x0b\x32!.opamp.proto.ServerToAgentCommand\x12<\n\x13\x63ustom_capabilities\x18\n \x01(\x0b\x32\x1f.opamp.proto.CustomCapabilities\x12\x32\n\x0e\x63ustom_message\x18\x0b \x01(\x0b\x32\x1a.opamp.proto.CustomMessage\"\xb4\x01\n\x17OpAMPConnectionSettings\x12\x1c\n\x14\x64\x65stination_endpoint\x18\x01 \x01(\t\x12%\n\x07headers\x18\x02 \x01(\x0b\x32\x14.opamp.proto.Headers\x12\x30\n\x0b\x63\x65rtificate\x18\x03 \x01(\x0b\x32\x1b.opamp.proto.TLSCertificate\x12\"\n\x1aheartbeat_interval_seconds\x18\x04 \x01(\x04\"\x94\x01\n\x1bTelemetryConnectionSettings\x12\x1c\n\x14\x64\x65stination_endpoint\x18\x01 \x01(\t\x12%\n\x07headers\x18\x02 \x01(\x0b\x32\x14.opamp.proto.Headers\x12\x30\n\x0b\x63\x65rtificate\x18\x03 \x01(\x0b\x32\x1b.opamp.proto.TLSCertificate\"\x97\x02\n\x17OtherConnectionSettings\x12\x1c\n\x14\x64\x65stination_endpoint\x18\x01 \x01(\t\x12%\n\x07headers\x18\x02 \x01(\x0b\x32\x14.opamp.proto.Headers\x12\x30\n\x0b\x63\x65rtificate\x18\x03 \x01(\x0b\x32\x1b.opamp.proto.TLSCertificate\x12O\n\x0eother_settings\x18\x04 \x03(\x0b\x32\x37.opamp.proto.OtherConnectionSettings.OtherSettingsEntry\x1a\x34\n\x12OtherSettingsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"/\n\x07Headers\x12$\n\x07headers\x18\x01 \x03(\x0b\x32\x13.opamp.proto.Header\"$\n\x06Header\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"D\n\x0eTLSCertificate\x12\x0c\n\x04\x63\x65rt\x18\x01 \x01(\x0c\x12\x13\n\x0bprivate_key\x18\x02 \x01(\x0c\x12\x0f\n\x07\x63\x61_cert\x18\x03 \x01(\x0c\"\xcd\x03\n\x18\x43onnectionSettingsOffers\x12\x0c\n\x04hash\x18\x01 \x01(\x0c\x12\x33\n\x05opamp\x18\x02 \x01(\x0b\x32$.opamp.proto.OpAMPConnectionSettings\x12=\n\x0bown_metrics\x18\x03 \x01(\x0b\x32(.opamp.proto.TelemetryConnectionSettings\x12<\n\nown_traces\x18\x04 \x01(\x0b\x32(.opamp.proto.TelemetryConnectionSettings\x12:\n\x08own_logs\x18\x05 \x01(\x0b\x32(.opamp.proto.TelemetryConnectionSettings\x12V\n\x11other_connections\x18\x06 \x03(\x0b\x32;.opamp.proto.ConnectionSettingsOffers.OtherConnectionsEntry\x1a]\n\x15OtherConnectionsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x33\n\x05value\x18\x02 \x01(\x0b\x32$.opamp.proto.OtherConnectionSettings:\x02\x38\x01\"\xbe\x01\n\x11PackagesAvailable\x12>\n\x08packages\x18\x01 \x03(\x0b\x32,.opamp.proto.PackagesAvailable.PackagesEntry\x12\x19\n\x11\x61ll_packages_hash\x18\x02 \x01(\x0c\x1aN\n\rPackagesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12,\n\x05value\x18\x02 \x01(\x0b\x32\x1d.opamp.proto.PackageAvailable:\x02\x38\x01\"\x86\x01\n\x10PackageAvailable\x12&\n\x04type\x18\x01 \x01(\x0e\x32\x18.opamp.proto.PackageType\x12\x0f\n\x07version\x18\x02 \x01(\t\x12+\n\x04\x66ile\x18\x03 \x01(\x0b\x32\x1d.opamp.proto.DownloadableFile\x12\x0c\n\x04hash\x18\x04 \x01(\x0c\"x\n\x10\x44ownloadableFile\x12\x14\n\x0c\x64ownload_url\x18\x01 \x01(\t\x12\x14\n\x0c\x63ontent_hash\x18\x02 \x01(\x0c\x12\x11\n\tsignature\x18\x03 \x01(\x0c\x12%\n\x07headers\x18\x04 \x01(\x0b\x32\x14.opamp.proto.Headers\"\x99\x01\n\x13ServerErrorResponse\x12\x32\n\x04type\x18\x01 \x01(\x0e\x32$.opamp.proto.ServerErrorResponseType\x12\x15\n\rerror_message\x18\x02 \x01(\t\x12,\n\nretry_info\x18\x03 \x01(\x0b\x32\x16.opamp.proto.RetryInfoH\x00\x42\t\n\x07\x44\x65tails\",\n\tRetryInfo\x12\x1f\n\x17retry_after_nanoseconds\x18\x01 \x01(\x04\">\n\x14ServerToAgentCommand\x12&\n\x04type\x18\x01 \x01(\x0e\x32\x18.opamp.proto.CommandType\"\x84\x01\n\x10\x41gentDescription\x12\x35\n\x16identifying_attributes\x18\x01 \x03(\x0b\x32\x15.opamp.proto.KeyValue\x12\x39\n\x1anon_identifying_attributes\x18\x02 \x03(\x0b\x32\x15.opamp.proto.KeyValue\"\xb0\x02\n\x0f\x43omponentHealth\x12\x0f\n\x07healthy\x18\x01 \x01(\x08\x12\x1c\n\x14start_time_unix_nano\x18\x02 \x01(\x06\x12\x12\n\nlast_error\x18\x03 \x01(\t\x12\x0e\n\x06status\x18\x04 \x01(\t\x12\x1d\n\x15status_time_unix_nano\x18\x05 \x01(\x06\x12R\n\x14\x63omponent_health_map\x18\x06 \x03(\x0b\x32\x34.opamp.proto.ComponentHealth.ComponentHealthMapEntry\x1aW\n\x17\x43omponentHealthMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12+\n\x05value\x18\x02 \x01(\x0b\x32\x1c.opamp.proto.ComponentHealth:\x02\x38\x01\"B\n\x0f\x45\x66\x66\x65\x63tiveConfig\x12/\n\nconfig_map\x18\x01 \x01(\x0b\x32\x1b.opamp.proto.AgentConfigMap\"\x7f\n\x12RemoteConfigStatus\x12\x1f\n\x17last_remote_config_hash\x18\x01 \x01(\x0c\x12\x31\n\x06status\x18\x02 \x01(\x0e\x32!.opamp.proto.RemoteConfigStatuses\x12\x15\n\rerror_message\x18\x03 \x01(\t\"\xde\x01\n\x0fPackageStatuses\x12<\n\x08packages\x18\x01 \x03(\x0b\x32*.opamp.proto.PackageStatuses.PackagesEntry\x12)\n!server_provided_all_packages_hash\x18\x02 \x01(\x0c\x12\x15\n\rerror_message\x18\x03 \x01(\t\x1aK\n\rPackagesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x1a.opamp.proto.PackageStatus:\x02\x38\x01\"\x93\x02\n\rPackageStatus\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x19\n\x11\x61gent_has_version\x18\x02 \x01(\t\x12\x16\n\x0e\x61gent_has_hash\x18\x03 \x01(\x0c\x12\x1e\n\x16server_offered_version\x18\x04 \x01(\t\x12\x1b\n\x13server_offered_hash\x18\x05 \x01(\x0c\x12.\n\x06status\x18\x06 \x01(\x0e\x32\x1e.opamp.proto.PackageStatusEnum\x12\x15\n\rerror_message\x18\x07 \x01(\t\x12=\n\x10\x64ownload_details\x18\x08 \x01(\x0b\x32#.opamp.proto.PackageDownloadDetails\"U\n\x16PackageDownloadDetails\x12\x18\n\x10\x64ownload_percent\x18\x01 \x01(\x01\x12!\n\x19\x64ownload_bytes_per_second\x18\x02 \x01(\x01\"/\n\x13\x41gentIdentification\x12\x18\n\x10new_instance_uid\x18\x01 \x01(\x0c\"U\n\x11\x41gentRemoteConfig\x12+\n\x06\x63onfig\x18\x01 \x01(\x0b\x32\x1b.opamp.proto.AgentConfigMap\x12\x13\n\x0b\x63onfig_hash\x18\x02 \x01(\x0c\"\xa0\x01\n\x0e\x41gentConfigMap\x12>\n\nconfig_map\x18\x01 \x03(\x0b\x32*.opamp.proto.AgentConfigMap.ConfigMapEntry\x1aN\n\x0e\x43onfigMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12+\n\x05value\x18\x02 \x01(\x0b\x32\x1c.opamp.proto.AgentConfigFile:\x02\x38\x01\"5\n\x0f\x41gentConfigFile\x12\x0c\n\x04\x62ody\x18\x01 \x01(\x0c\x12\x14\n\x0c\x63ontent_type\x18\x02 \x01(\t\"*\n\x12\x43ustomCapabilities\x12\x14\n\x0c\x63\x61pabilities\x18\x01 \x03(\t\"?\n\rCustomMessage\x12\x12\n\ncapability\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c*c\n\x12\x41gentToServerFlags\x12\"\n\x1e\x41gentToServerFlags_Unspecified\x10\x00\x12)\n%AgentToServerFlags_RequestInstanceUid\x10\x01*\x92\x01\n\x12ServerToAgentFlags\x12\"\n\x1eServerToAgentFlags_Unspecified\x10\x00\x12&\n\"ServerToAgentFlags_ReportFullState\x10\x01\x12\x30\n,ServerToAgentFlags_ReportAvailableComponents\x10\x02*\xf7\x02\n\x12ServerCapabilities\x12\"\n\x1eServerCapabilities_Unspecified\x10\x00\x12$\n ServerCapabilities_AcceptsStatus\x10\x01\x12)\n%ServerCapabilities_OffersRemoteConfig\x10\x02\x12-\n)ServerCapabilities_AcceptsEffectiveConfig\x10\x04\x12%\n!ServerCapabilities_OffersPackages\x10\x08\x12,\n(ServerCapabilities_AcceptsPackagesStatus\x10\x10\x12/\n+ServerCapabilities_OffersConnectionSettings\x10 \x12\x37\n3ServerCapabilities_AcceptsConnectionSettingsRequest\x10@*>\n\x0bPackageType\x12\x18\n\x14PackageType_TopLevel\x10\x00\x12\x15\n\x11PackageType_Addon\x10\x01*\x8f\x01\n\x17ServerErrorResponseType\x12#\n\x1fServerErrorResponseType_Unknown\x10\x00\x12&\n\"ServerErrorResponseType_BadRequest\x10\x01\x12\'\n#ServerErrorResponseType_Unavailable\x10\x02*&\n\x0b\x43ommandType\x12\x17\n\x13\x43ommandType_Restart\x10\x00*\xcc\x05\n\x11\x41gentCapabilities\x12!\n\x1d\x41gentCapabilities_Unspecified\x10\x00\x12#\n\x1f\x41gentCapabilities_ReportsStatus\x10\x01\x12)\n%AgentCapabilities_AcceptsRemoteConfig\x10\x02\x12,\n(AgentCapabilities_ReportsEffectiveConfig\x10\x04\x12%\n!AgentCapabilities_AcceptsPackages\x10\x08\x12,\n(AgentCapabilities_ReportsPackageStatuses\x10\x10\x12&\n\"AgentCapabilities_ReportsOwnTraces\x10 \x12\'\n#AgentCapabilities_ReportsOwnMetrics\x10@\x12%\n AgentCapabilities_ReportsOwnLogs\x10\x80\x01\x12\x35\n0AgentCapabilities_AcceptsOpAMPConnectionSettings\x10\x80\x02\x12\x35\n0AgentCapabilities_AcceptsOtherConnectionSettings\x10\x80\x04\x12,\n\'AgentCapabilities_AcceptsRestartCommand\x10\x80\x08\x12$\n\x1f\x41gentCapabilities_ReportsHealth\x10\x80\x10\x12*\n%AgentCapabilities_ReportsRemoteConfig\x10\x80 \x12\'\n\"AgentCapabilities_ReportsHeartbeat\x10\x80@\x12\x32\n,AgentCapabilities_ReportsAvailableComponents\x10\x80\x80\x01*\x9c\x01\n\x14RemoteConfigStatuses\x12\x1e\n\x1aRemoteConfigStatuses_UNSET\x10\x00\x12 \n\x1cRemoteConfigStatuses_APPLIED\x10\x01\x12!\n\x1dRemoteConfigStatuses_APPLYING\x10\x02\x12\x1f\n\x1bRemoteConfigStatuses_FAILED\x10\x03*\xc4\x01\n\x11PackageStatusEnum\x12\x1f\n\x1bPackageStatusEnum_Installed\x10\x00\x12$\n PackageStatusEnum_InstallPending\x10\x01\x12 \n\x1cPackageStatusEnum_Installing\x10\x02\x12#\n\x1fPackageStatusEnum_InstallFailed\x10\x03\x12!\n\x1dPackageStatusEnum_Downloading\x10\x04\x42.Z,github.com/open-telemetry/opamp-go/protobufsb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'opamp_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z,github.com/open-telemetry/opamp-go/protobufs'
  _globals['_AVAILABLECOMPONENTS_COMPONENTSENTRY']._loaded_options = None
  _globals['_AVAILABLECOMPONENTS_COMPONENTSENTRY']._serialized_options = b'8\001'
  _globals['_COMPONENTDETAILS_SUBCOMPONENTMAPENTRY']._loaded_options = None
  _globals['_COMPONENTDETAILS_SUBCOMPONENTMAPENTRY']._serialized_options = b'8\001'
  _globals['_OTHERCONNECTIONSETTINGS_OTHERSETTINGSENTRY']._loaded_options = None
  _globals['_OTHERCONNECTIONSETTINGS_OTHERSETTINGSENTRY']._serialized_options = b'8\001'
  _globals['_CONNECTIONSETTINGSOFFERS_OTHERCONNECTIONSENTRY']._loaded_options = None
  _globals['_CONNECTIONSETTINGSOFFERS_OTHERCONNECTIONSENTRY']._serialized_options = b'8\001'
  _globals['_PACKAGESAVAILABLE_PACKAGESENTRY']._loaded_options = None
  _globals['_PACKAGESAVAILABLE_PACKAGESENTRY']._serialized_options = b'8\001'
  _globals['_COMPONENTHEALTH_COMPONENTHEALTHMAPENTRY']._loaded_options = None
  _globals['_COMPONENTHEALTH_COMPONENTHEALTHMAPENTRY']._serialized_options = b'8\001'
  _globals['_PACKAGESTATUSES_PACKAGESENTRY']._loaded_options = None
  _globals['_PACKAGESTATUSES_PACKAGESENTRY']._serialized_options = b'8\001'
  _globals['_AGENTCONFIGMAP_CONFIGMAPENTRY']._loaded_options = None
  _globals['_AGENTCONFIGMAP_CONFIGMAPENTRY']._serialized_options = b'8\001'
  _globals['_AGENTTOSERVERFLAGS']._serialized_start=5585
  _globals['_AGENTTOSERVERFLAGS']._serialized_end=5684
  _globals['_SERVERTOAGENTFLAGS']._serialized_start=5687
  _globals['_SERVERTOAGENTFLAGS']._serialized_end=5833
  _globals['_SERVERCAPABILITIES']._serialized_start=5836
  _globals['_SERVERCAPABILITIES']._serialized_end=6211
  _globals['_PACKAGETYPE']._serialized_start=6213
  _globals['_PACKAGETYPE']._serialized_end=6275
  _globals['_SERVERERRORRESPONSETYPE']._serialized_start=6278
  _globals['_SERVERERRORRESPONSETYPE']._serialized_end=6421
  _globals['_COMMANDTYPE']._serialized_start=6423
  _globals['_COMMANDTYPE']._serialized_end=6461
  _globals['_AGENTCAPABILITIES']._serialized_start=6464
  _globals['_AGENTCAPABILITIES']._serialized_end=7180
  _globals['_REMOTECONFIGSTATUSES']._serialized_start=7183
  _globals['_REMOTECONFIGSTATUSES']._serialized_end=7339
  _globals['_PACKAGESTATUSENUM']._serialized_start=7342
  _globals['_PACKAGESTATUSENUM']._serialized_end=7538
  _globals['_AGENTTOSERVER']._serialized_start=45
  _globals['_AGENTTOSERVER']._serialized_end=731
  _globals['_AGENTDISCONNECT']._serialized_start=733
  _globals['_AGENTDISCONNECT']._serialized_end=750
  _globals['_CONNECTIONSETTINGSREQUEST']._serialized_start=752
  _globals['_CONNECTIONSETTINGSREQUEST']._serialized_end=839
  _globals['_OPAMPCONNECTIONSETTINGSREQUEST']._serialized_start=841
  _globals['_OPAMPCONNECTIONSETTINGSREQUEST']._serialized_end=935
  _globals['_CERTIFICATEREQUEST']._serialized_start=937
  _globals['_CERTIFICATEREQUEST']._serialized_end=970
  _globals['_AVAILABLECOMPONENTS']._serialized_start=973
  _globals['_AVAILABLECOMPONENTS']._serialized_end=1160
  _globals['_AVAILABLECOMPONENTS_COMPONENTSENTRY']._serialized_start=1080
  _globals['_AVAILABLECOMPONENTS_COMPONENTSENTRY']._serialized_end=1160
  _globals['_COMPONENTDETAILS']._serialized_start=1163
  _globals['_COMPONENTDETAILS']._serialized_end=1388
  _globals['_COMPONENTDETAILS_SUBCOMPONENTMAPENTRY']._serialized_start=1303
  _globals['_COMPONENTDETAILS_SUBCOMPONENTMAPENTRY']._serialized_end=1388
  _globals['_SERVERTOAGENT']._serialized_start=1391
  _globals['_SERVERTOAGENT']._serialized_end=1936
  _globals['_OPAMPCONNECTIONSETTINGS']._serialized_start=1939
  _globals['_OPAMPCONNECTIONSETTINGS']._serialized_end=2119
  _globals['_TELEMETRYCONNECTIONSETTINGS']._serialized_start=2122
  _globals['_TELEMETRYCONNECTIONSETTINGS']._serialized_end=2270
  _globals['_OTHERCONNECTIONSETTINGS']._serialized_start=2273
  _globals['_OTHERCONNECTIONSETTINGS']._serialized_end=2552
  _globals['_OTHERCONNECTIONSETTINGS_OTHERSETTINGSENTRY']._serialized_start=2500
  _globals['_OTHERCONNECTIONSETTINGS_OTHERSETTINGSENTRY']._serialized_end=2552
  _globals['_HEADERS']._serialized_start=2554
  _globals['_HEADERS']._serialized_end=2601
  _globals['_HEADER']._serialized_start=2603
  _globals['_HEADER']._serialized_end=2639
  _globals['_TLSCERTIFICATE']._serialized_start=2641
  _globals['_TLSCERTIFICATE']._serialized_end=2709
  _globals['_CONNECTIONSETTINGSOFFERS']._serialized_start=2712
  _globals['_CONNECTIONSETTINGSOFFERS']._serialized_end=3173
  _globals['_CONNECTIONSETTINGSOFFERS_OTHERCONNECTIONSENTRY']._serialized_start=3080
  _globals['_CONNECTIONSETTINGSOFFERS_OTHERCONNECTIONSENTRY']._serialized_end=3173
  _globals['_PACKAGESAVAILABLE']._serialized_start=3176
  _globals['_PACKAGESAVAILABLE']._serialized_end=3366
  _globals['_PACKAGESAVAILABLE_PACKAGESENTRY']._serialized_start=3288
  _globals['_PACKAGESAVAILABLE_PACKAGESENTRY']._serialized_end=3366
  _globals['_PACKAGEAVAILABLE']._serialized_start=3369
  _globals['_PACKAGEAVAILABLE']._serialized_end=3503
  _globals['_DOWNLOADABLEFILE']._serialized_start=3505
  _globals['_DOWNLOADABLEFILE']._serialized_end=3625
  _globals['_SERVERERRORRESPONSE']._serialized_start=3628
  _globals['_SERVERERRORRESPONSE']._serialized_end=3781
  _globals['_RETRYINFO']._serialized_start=3783
  _globals['_RETRYINFO']._serialized_end=3827
  _globals['_SERVERTOAGENTCOMMAND']._serialized_start=3829
  _globals['_SERVERTOAGENTCOMMAND']._serialized_end=3891
  _globals['_AGENTDESCRIPTION']._serialized_start=3894
  _globals['_AGENTDESCRIPTION']._serialized_end=4026
  _globals['_COMPONENTHEALTH']._serialized_start=4029
  _globals['_COMPONENTHEALTH']._serialized_end=4333
  _globals['_COMPONENTHEALTH_COMPONENTHEALTHMAPENTRY']._serialized_start=4246
  _globals['_COMPONENTHEALTH_COMPONENTHEALTHMAPENTRY']._serialized_end=4333
  _globals['_EFFECTIVECONFIG']._serialized_start=4335
  _globals['_EFFECTIVECONFIG']._serialized_end=4401
  _globals['_REMOTECONFIGSTATUS']._serialized_start=4403
  _globals['_REMOTECONFIGSTATUS']._serialized_end=4530
  _globals['_PACKAGESTATUSES']._serialized_start=4533
  _globals['_PACKAGESTATUSES']._serialized_end=4755
  _globals['_PACKAGESTATUSES_PACKAGESENTRY']._serialized_start=4680
  _globals['_PACKAGESTATUSES_PACKAGESENTRY']._serialized_end=4755
  _globals['_PACKAGESTATUS']._serialized_start=4758
  _globals['_PACKAGESTATUS']._serialized_end=5033
  _globals['_PACKAGEDOWNLOADDETAILS']._serialized_start=5035
  _globals['_PACKAGEDOWNLOADDETAILS']._serialized_end=5120
  _globals['_AGENTIDENTIFICATION']._serialized_start=5122
  _globals['_AGENTIDENTIFICATION']._serialized_end=5169
  _globals['_AGENTREMOTECONFIG']._serialized_start=5171
  _globals['_AGENTREMOTECONFIG']._serialized_end=5256
  _globals['_AGENTCONFIGMAP']._serialized_start=5259
  _globals['_AGENTCONFIGMAP']._serialized_end=5419
  _globals['_AGENTCONFIGMAP_CONFIGMAPENTRY']._serialized_start=5341
  _globals['_AGENTCONFIGMAP_CONFIGMAPENTRY']._serialized_end=5419
  _globals['_AGENTCONFIGFILE']._serialized_start=5421
  _globals['_AGENTCONFIGFILE']._serialized_end=5474
  _globals['_CUSTOMCAPABILITIES']._serialized_start=5476
  _globals['_CUSTOMCAPABILITIES']._serialized_end=5518
  _globals['_CUSTOMMESSAGE']._serialized_start=5520
  _globals['_CUSTOMMESSAGE']._serialized_end=5583
# @@protoc_insertion_point(module_scope)
