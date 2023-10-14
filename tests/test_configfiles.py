from scripts.landingzone_deploy import *
import pytest

TESTFILES_DIR = "./tests/testfiles/"
ACCOUNTS_TESTFILE = TESTFILES_DIR + "accounts.yaml"
GROUPS_TESTFILE = TESTFILES_DIR + "groups.yaml"
LANDINGZONE_CONFIG_TESTFILE = TESTFILES_DIR + "landingzone-config.yaml"

@pytest.mark.configfiles
class ConfigFilesTests:

    def test_read_accounts_from_file(self):
        assert read_accounts_from_file(ACCOUNTS_TESTFILE) == \
                   [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master", "Environment": "prod", "AccountId": "999999999999"}]

    def test_read_groups_from_file(self):
        assert read_groups_from_file(GROUPS_TESTFILE) == \
                   [{"Name": "AllAccounts", "List": ["development", "master"]}] 

    def test_read_landingzone_config_from_file(self):
        assert read_landingzone_config_from_file(LANDINGZONE_CONFIG_TESTFILE) == \
                   {"MaxConcurrentAccounts": 1, 
                    "MaxConcurrentStacksPerAccount": 2, 
                    "WaitTimeInSec": 5, 
                    "Logging": "Info", 
                    "GroupNameAllAccounts": "AllAccounts", 
                    "GroupNameAllRegions": "AllRegions", 
                    "Tags": [{
                        "Key": "LandingZoneResource", 
                        "Value": "True"
                    }], 
                    "AddTags": [{
                        "Key": "Department", 
                        "Value": "ICT"
                    }]} 

@pytest.mark.enrichconfigfiles
class EnrichAccountsTests:

    def test_enrich_accounts_no_enrichment(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"}]

        enrich_accounts(accounts) 
        assert accounts == [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"}]

    def test_enrich_accounts_add_profile_name(self):
        accounts = [{"Name": "master", "Environment": "prod", "AccountId": "999999999999"}]

        enrich_accounts(accounts) 
        assert accounts == [{"Name": "master", "ProfileName": "master", "Environment": "prod", "AccountId": "999999999999"}]

    def test_enrich_accounts_multiple_accounts(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master", "Environment": "prod", "AccountId": "999999999999"}]

        enrich_accounts(accounts)
        assert accounts == [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"},
                            {"Name": "master", "ProfileName": "master", "Environment": "prod", "AccountId": "999999999999"}]
        
    def test_enrich_accounts_without_accounts(self, capsys):
        accounts = []
        with pytest.raises(InvalidConfigFileException) as excinfo:
            enrich_accounts(accounts)
        captured = capsys.readouterr()
        expected_error = "Missing accounts in configuration file"
        assert str(excinfo.value) == expected_error
        assert expected_error in captured.out

@pytest.mark.enrichconfigfiles
class EnrichGroupsTests:

    def test_unfold_list_item_one_item(self):
        groups = [{"Name": "AllAccounts", "List": ["development", "master"]}] 
        assert unfold_list_item(groups, "development") == ["development"]


    def test_unfold_list_item_group(self):
        groups = [{"Name": "AllAccounts", "List": ["development", "master"]}] 
        assert unfold_list_item(groups, "AllAccounts") == ["development", "master"]


    def test_unfold_list_item_not_exist(self):
        groups = [{"Name": "AllAccounts", "List": ["development", "master"]}] 
        assert unfold_list_item(groups, "NotExist") == ["NotExist"]


    def test_unfold_list_item_do_not_nest(self):
        # Nesting should be done by unfold_group_list, not by unfold_list_item
        groups = [{"Name": "AllAccounts", "List": ["AllTestAccounts", "master"]},
                  {"Name": "AllTestAccounts", "List": ["development", "sandbox"]}] 
        assert unfold_list_item(groups, "AllAccounts") == ["AllTestAccounts", "master"]

    
    def test_unfold_group_list_one_item(self):
        groups = [{"Name": "AllAccounts", "List": ["development", "master"]}] 
        assert unfold_group_list(groups, ["development"]) == ["development"] 


    def test_unfold_group_list_group_item(self):
        groups = [{"Name": "AllAccounts", "List": ["development", "master"]}] 
        assert unfold_group_list(groups, ["AllAccounts"]) == ["development", "master"] 


    def test_unfold_group_list_not_exist(self):
        groups = [{"Name": "AllAccounts", "List": ["development", "master"]}] 
        assert unfold_group_list(groups, ["NotExist"]) == ["NotExist"]


    def test_unfold_group_list_nested(self):
        groups = [{"Name": "AllAccounts", "List": ["AllTestAccounts", "master"]},
                  {"Name": "AllTestAccounts", "List": ["development", "sandbox"]}] 
        assert unfold_group_list(groups, ["AllAccounts"]) == ["development", "sandbox", "master"]


    def test_unfold_group_list_nested_groups_in_nested_groups(self):
        groups = [{"Name": "AllAccounts", "List": ["AllWorkloadAccounts", "master"]},
                  {"Name": "AllWorkloadAccounts", "List": ["Application_A_Accounts", "Application_B_Accounts"]},
                  {"Name": "Application_A_Accounts", "List": ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod"]},
                  {"Name": "Application_B_Accounts", "List": ["Application_B_Dev", "Application_B_Staging", "Application_B_Prod"]}] 
        assert unfold_group_list(groups, ["AllAccounts"]) == ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod", 
                                                             "Application_B_Dev", "Application_B_Staging", "Application_B_Prod",
                                                             "master"]


    def test_enrich_groups_no_enrichment(self):
        groups = [{"Name": "AllAccounts", "List": ["development", "master"]}] 
        enrich_groups(groups)

        assert groups == [{"Name": "AllAccounts", "List": ["development", "master"]}]


    def test_enrich_groups_nested_groups(self):
        groups = [{"Name": "AllAccounts", "List": ["AllTestAccounts", "master"]},
                  {"Name": "AllTestAccounts", "List": ["development", "sandbox"]}] 
        enrich_groups(groups)

        assert groups == [{"Name": "AllAccounts", "List": ["development", "sandbox", "master"]},
                          {"Name": "AllTestAccounts", "List": ["development", "sandbox"]}]


    def test_enrich_groups_nested_groups_in_nested_groups(self):
        groups = [{"Name": "AllAccounts", "List": ["AllWorkloadAccounts", "master"]},
                  {"Name": "AllWorkloadAccounts", "List": ["Application_A_Accounts", "Application_B_Accounts"]},
                  {"Name": "Application_A_Accounts", "List": ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod"]},
                  {"Name": "Application_B_Accounts", "List": ["Application_B_Dev", "Application_B_Staging", "Application_B_Prod"]}] 
        enrich_groups(groups)
        assert groups == [{"Name": "AllAccounts", "List": ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod", 
                                                           "Application_B_Dev", "Application_B_Staging", "Application_B_Prod",
                                                           "master"]},
                          {"Name": "AllWorkloadAccounts", "List": ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod", 
                                                                   "Application_B_Dev", "Application_B_Staging", "Application_B_Prod"]},
                          {"Name": "Application_A_Accounts", "List": ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod"]},
                          {"Name": "Application_B_Accounts", "List": ["Application_B_Dev", "Application_B_Staging", "Application_B_Prod"]}]


    def test_enrich_groups_except(self):
        groups = [{"Name": "AllAccounts", "List": ["development", "master"], "Except": ["master"]}]
        enrich_groups(groups)
        assert groups == [{"Name": "AllAccounts", "List": ["development"]}]


    def test_enrich_groups_nested_group_except(self):
        groups = [{"Name": "AllLandingZoneAccounts", "List": ["master", "audit", "log-archive"]},
                  {"Name": "AllLandingZoneAccountsExceptMaster", "List": ["AllLandingZoneAccounts"], "Except": ["master"]}] 
        enrich_groups(groups)

        assert groups == [{"Name": "AllLandingZoneAccounts", "List": ["master", "audit", "log-archive"]},
                          {"Name": "AllLandingZoneAccountsExceptMaster", "List": ["audit", "log-archive"]}]


    def test_enrich_groups_except_nested_group(self):
        groups = [{"Name": "AllApplicationAccounts", "List": ["AllApplication_A_Accounts", "AllApplication_B_Accounts"]},
                  {"Name": "AllApplication_A_Accounts", "List": ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod"]},
                  {"Name": "AllApplication_B_Accounts", "List": ["Application_B_Dev", "Application_B_Staging", "Application_B_Prod"]},
                  {"Name": "AllProdAccounts", "List": ["Application_A_Prod", "Application_B_Prod"]},
                  {"Name": "AllDevAndStagingAccounts", "List": ["AllApplicationAccounts"], "Except": ["AllProdAccounts"]}] 
        enrich_groups(groups)

        assert groups == [{"Name": "AllApplicationAccounts", "List": ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod", 
                                                                      "Application_B_Dev", "Application_B_Staging", "Application_B_Prod"]},
                  {"Name": "AllApplication_A_Accounts", "List": ["Application_A_Dev", "Application_A_Staging", "Application_A_Prod"]},
                  {"Name": "AllApplication_B_Accounts", "List": ["Application_B_Dev", "Application_B_Staging", "Application_B_Prod"]},
                  {"Name": "AllProdAccounts", "List": ["Application_A_Prod", "Application_B_Prod"]},
                  {"Name": "AllDevAndStagingAccounts", "List": ["Application_A_Dev", "Application_A_Staging",
                                                                "Application_B_Dev", "Application_B_Staging"]}] 

    def test_enrich_groups_without_groups(self, capsys):
        groups = []
        with pytest.raises(InvalidConfigFileException) as excinfo:
            enrich_groups(groups)
        captured = capsys.readouterr()
        expected_error = "Missing groups in configuration file"
        assert str(excinfo.value) == expected_error
        assert expected_error in captured.out

@pytest.mark.enrichconfigfiles
class EnrichLandingZoneConfigTests:

    def test_enrich_landingzone_config_defaults(self):
        landingzone_config = {"MaxConcurrentAccounts": 2, 
                              "MaxConcurrentStacksPerAccount": 5,
                              "WaitTimeInSec": 5,
                              "GroupNameAllAccounts": "AllAccounts",
                              "GroupNameAllRegions": "AllRegions",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }]}
        enrich_landingzone_config(landingzone_config)
        assert landingzone_config == {"MaxConcurrentAccounts": 2, 
                                      "MaxConcurrentStacksPerAccount": 5,
                                      "WaitTimeInSec": 5,
                                      "GroupNameAllAccounts": "AllAccounts",
                                      "GroupNameAllRegions": "AllRegions",
                                      "Tags": [{
                                          "Key": "LandingZoneResource", 
                                          "Value": "True"
                                      }],
                                      "DryRun": True,
                                      "AbortWhenStackFails": True,
                                      "LogLevel": "NoExtraLogging",
                                      "AddTags": []                                      
                                      } 

    def test_enrich_landingzone_config_no_defaults(self):
        landingzone_config = {"MaxConcurrentAccounts": 2, 
                              "MaxConcurrentStacksPerAccount": 5,
                              "WaitTimeInSec": 5,
                              "GroupNameAllAccounts": "AllAccounts",
                              "GroupNameAllRegions": "AllRegions",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }],
                              "DryRun": False,
                              "AbortWhenStackFails": False,
                              "LogLevel": "Info",
                              "AddTags": [{
                                  "Key": "Department", 
                                  "Value": "ICT"                                  
                              }]}
        enrich_landingzone_config(landingzone_config)
        assert landingzone_config == {"MaxConcurrentAccounts": 2, 
                                      "MaxConcurrentStacksPerAccount": 5,
                                      "WaitTimeInSec": 5,
                                      "GroupNameAllAccounts": "AllAccounts",
                                      "GroupNameAllRegions": "AllRegions",
                                      "Tags": [{
                                          "Key": "LandingZoneResource", 
                                          "Value": "True"
                                      }],
                                      "DryRun": False,
                                      "AbortWhenStackFails": False,
                                      "LogLevel": "Info",
                                      "AddTags": [{
                                          "Key": "Department", 
                                          "Value": "ICT"                                  
                                      }]}

    def test_enrich_landingzone_config_no_max_concurrent_accounts(self, capsys):
        landingzone_config = {"MaxConcurrentStacksPerAccount": 5,
                              "WaitTimeInSec": 5,
                              "GroupNameAllAccounts": "AllAccounts",
                              "GroupNameAllRegions": "AllRegions",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }]}
        with pytest.raises(InvalidConfigFileException) as excinfo:
            enrich_landingzone_config(landingzone_config)
        captured = capsys.readouterr()

        expected_error = "Parameter MaxConcurrentAccounts missing in configuration file"
        assert str(excinfo.value) == expected_error
        assert expected_error in captured.out


    def test_enrich_landingzone_config_no_max_concurrent_stacks_per_accounts(self, capsys):
        landingzone_config = {"MaxConcurrentAccounts": 5,
                              "WaitTimeInSec": 5,
                              "GroupNameAllAccounts": "AllAccounts",
                              "GroupNameAllRegions": "AllRegions",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }]}
        with pytest.raises(InvalidConfigFileException) as excinfo:
            enrich_landingzone_config(landingzone_config)
        captured = capsys.readouterr()

        expected_error = "Parameter MaxConcurrentStacksPerAccount missing in configuration file"
        assert str(excinfo.value) == expected_error
        assert expected_error in captured.out


    def test_enrich_landingzone_config_no_wait_time_in_sec(self, capsys):
        landingzone_config = {"MaxConcurrentAccounts": 3,
                              "MaxConcurrentStacksPerAccount": 5,
                              "GroupNameAllAccounts": "AllAccounts",
                              "GroupNameAllRegions": "AllRegions",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }]}
        with pytest.raises(InvalidConfigFileException) as excinfo:
            enrich_landingzone_config(landingzone_config)
        captured = capsys.readouterr()

        expected_error = "Parameter WaitTimeInSec missing in configuration file"
        assert str(excinfo.value) == expected_error
        assert expected_error in captured.out


    def test_enrich_landingzone_config_no_group_name_all_accounts(self, capsys):
        landingzone_config = {"MaxConcurrentAccounts": 3,
                              "MaxConcurrentStacksPerAccount": 5,
                              "WaitTimeInSec": 5,
                              "GroupNameAllRegions": "AllRegions",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }]}
        with pytest.raises(InvalidConfigFileException) as excinfo:
            enrich_landingzone_config(landingzone_config)
        captured = capsys.readouterr()

        expected_error = "Parameter GroupNameAllAccounts missing in configuration file"
        assert str(excinfo.value) == expected_error
        assert expected_error in captured.out

 
    def test_enrich_landingzone_config_no_group_name_all_regions(self, capsys):
        landingzone_config = {"MaxConcurrentAccounts": 3,
                              "MaxConcurrentStacksPerAccount": 5,
                              "WaitTimeInSec": 5,
                              "GroupNameAllAccounts": "AllAccounts",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }]}
        with pytest.raises(InvalidConfigFileException) as excinfo:
            enrich_landingzone_config(landingzone_config)
        captured = capsys.readouterr()

        expected_error = "Parameter GroupNameAllRegions missing in configuration file"
        assert str(excinfo.value) == expected_error
        assert expected_error in captured.out


    def test_enrich_landingzone_config_no_group_name_all_regions(self, capsys):
        landingzone_config = {"MaxConcurrentAccounts": 3,
                              "MaxConcurrentStacksPerAccount": 5,
                              "WaitTimeInSec": 5,
                              "GroupNameAllAccounts": "AllAccounts",
                              "GroupNameAllRegions": "AllRegions"}
        with pytest.raises(InvalidConfigFileException) as excinfo:
            enrich_landingzone_config(landingzone_config)
        captured = capsys.readouterr()

        expected_error = "Parameter Tags missing in configuration file"
        assert str(excinfo.value) == expected_error
        assert expected_error in captured.out

