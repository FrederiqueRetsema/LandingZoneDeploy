from scripts.landingzone_deploy import *
import pytest

@pytest.mark.commandline_parameters
class CommandlineParametersTests:

    def get_default_accounts_groups_landingzone_config(self):
        accounts = [{"Name": "development", "ProfileName": "my-development", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master",      "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999"},
                    {"Name": "audit",       "ProfileName": "my-audit", "Environment": "prod", "AccountId": "888888888888"},
                    {"Name": "log-archive", "ProfileName": "my-log-archive", "Environment": "prod", "AccountId": "777777777777"}]
        groups = [{"Name": "AllAccounts",     "List": ["development", "master", "audit", "log-archive"]},
                  {"Name": "AllProdAccounts", "List": ["master", "audit", "log-archive"]},
                  {"Name": "AllTestAccounts", "List": ["development"]}] 
        landingzone_config = {"MaxConcurrentAccounts": 2, 
                              "MaxConcurrentStacksPerAccount": 5,
                              "WaitTimeInSec": 5,
                              "GroupNameAllAccounts": "AllAccounts",
                              "GroupNameAllRegions": "AllRegions",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }],
                              "DefaultRegions": ["eu-west-1", "eu-central-1"]
                             }
        return (accounts, groups, landingzone_config)

    def test_get_commandline_arguments_h(self, capsys):
        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        with pytest.raises(SystemExit):
            get_commandline_arguments(accounts, groups, landingzone_config, ["-h"]) 
        captured = capsys.readouterr() 
        assert "When -e, -g, -a, -p are used in combination" in captured.out

    def test_get_commandline_arguments_help(self, capsys):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        with pytest.raises(SystemExit):
            get_commandline_arguments(accounts, groups, landingzone_config, ["--help"]) 
        captured = capsys.readouterr() 
        assert "Change resources in the landing zone" in captured.out

    def test_get_commandline_arguments_no_dry_run(self):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        get_commandline_arguments(accounts, groups, landingzone_config, ["--no-dry-run"]) 
        assert landingzone_config['DryRun'] == False

    def test_get_commandline_arguments_no_no_dry_run(self):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        get_commandline_arguments(accounts, groups, landingzone_config, []) 
        assert landingzone_config['DryRun'] == True


    def test_get_commandline_arguments_no_abort_when_stack_fails(self):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        get_commandline_arguments(accounts, groups, landingzone_config, ["--no-abort-when-stack-fails"]) 
        assert landingzone_config['AbortWhenStackFails'] == False

    def test_get_commandline_arguments_no_no_abort_when_stack_fails(self):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        get_commandline_arguments(accounts, groups, landingzone_config, []) 
        assert landingzone_config['AbortWhenStackFails'] == True

    
    @pytest.mark.parametrize('params', [
        ({"switch":"-e",            "value": "dev",            "output": ["development"]}),
        ({"switch":"--environment", "value": "dev",            "output": ["development"]}),
        ({"switch": "-g",           "value": "AllAccounts",    "output": ["development", "master", "audit", "log-archive"]}),
        ({"switch": "--group",      "value": "AllAccounts",    "output": ["development", "master", "audit", "log-archive"]}),
        ({"switch": "-a",           "value": "development",    "output": ["development"]}),
        ({"switch": "--account",    "value": "development",    "output": ["development"]}),
        ({"switch": "-p",           "value": "my-development", "output": ["development"]}),
        ({"switch": "--profile",    "value": "my-development", "output": ["development"]})
    ])
    def test_get_commandline_arguments_with_one_value(self, params):
        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value"]]) 
        assert landingzone_config["SpecifiedAccountsOnly"] == params["output"]

    @pytest.mark.parametrize('params', [
        ({"switch": "-e",            "value1": "dev",             "value2": "prod",            "output": ["development", "master", "audit", "log-archive"]}),
        ({"switch": "--environment", "value1": "dev",             "value2": "prod",            "output": ["development", "master", "audit", "log-archive"]}),
        ({"switch": "-g",            "value1": "AllProdAccounts", "value2": "AllTestAccounts", "output": ["master", "audit", "log-archive", "development"]}),
        ({"switch": "--group",       "value1": "AllProdAccounts", "value2": "AllTestAccounts", "output": ["master", "audit", "log-archive", "development"]}),
        ({"switch": "-a",            "value1": "development",     "value2": "audit",           "output": ["development", "audit"]}),
        ({"switch": "--account",     "value1": "development",     "value2": "audit",           "output": ["development", "audit"]}),
        ({"switch": "-p",            "value1": "my-development",  "value2": "my-audit",        "output": ["development", "audit"]}),
        ({"switch": "--profile",     "value1": "my-development",  "value2": "my-audit",        "output": ["development", "audit"]})
    ])
    def test_get_commandline_arguments_with_two_values(self, params):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value1"], params["value2"]]) 
        assert landingzone_config["SpecifiedAccountsOnly"] == params["output"]
    
    @pytest.mark.parametrize('params', [
        ({"switch":"-e",            "value": "NotExists", "output": "Environment"}),
        ({"switch":"--environment", "value": "NotExists", "output": "Environment"}),
        ({"switch":"-g",            "value": "NotExists", "output": "Group"}),
        ({"switch":"--group",       "value": "NotExists", "output": "Group"}),
        ({"switch":"-a",            "value": "NotExists", "output": "Account"}),
        ({"switch":"--account",     "value": "NotExists", "output": "Account"}),
        ({"switch":"-p",            "value": "NotExists", "output": "Profile"}),
        ({"switch":"--profile",     "value": "NotExists", "output": "Profile"})
    ])
    def test_get_commandline_arguments_with_value_not_exists(self, capsys, params):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        with pytest.raises(InvalidParameterException):
            get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value"]]) 
        captured = capsys.readouterr()
        assert "{} {} not configured".format(params["output"], params["value"]) in captured.out

    @pytest.mark.parametrize('params', [
        ({"switch":"-e",            "value1": "dev",             "value2": "NotExists", "value3": "prod",            "output": "Environment"}),
        ({"switch":"--environment", "value1": "dev",             "value2": "NotExists", "value3": "prod",            "output": "Environment"}),
        ({"switch":"-g",            "value1": "AllProdAccounts", "value2": "NotExists", "value3": "AllTestAccounts", "output": "Group"}),
        ({"switch":"--group",       "value1": "AllProdAccounts", "value2": "NotExists", "value3": "AllTestAccounts", "output": "Group"}),
        ({"switch":"-a",            "value1": "development",     "value2": "NotExists", "value3": "audit",           "output": "Account"}),
        ({"switch":"--account",     "value1": "development",     "value2": "NotExists", "value3": "audit",           "output": "Account"}),
        ({"switch":"-p",            "value1": "my-development",  "value2": "NotExists", "value3": "my-audit",        "output": "Profile"}),
        ({"switch":"--profile",     "value1": "my-development",  "value2": "NotExists", "value3": "my-audit",        "output": "Profile"})
    ])
    def test_get_commandline_arguments_with_value_not_exists_in_combination_with_existing_environment(self, capsys, params):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        with pytest.raises(InvalidParameterException):
            get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value1"], params["value2"], params["value3"]]) 
        captured = capsys.readouterr()
        assert "{} {} not configured".format(params["output"], params["value2"]) in captured.out

    @pytest.mark.parametrize('params', [
        ({"switch":"-a",            "value": "my-development", "output": "Account"}),
        ({"switch":"--account",     "value": "my-development", "output": "Account"}),
        ({"switch":"-p",            "value": "development",    "output": "Profile"}),
        ({"switch":"--profile",     "value": "development",    "output": "Profile"})
    ])
    def test_get_commandline_arguments_account_is_no_profile_vv(self, capsys, params):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        with pytest.raises(InvalidParameterException):
            get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value"]]) 
        captured = capsys.readouterr()
        assert "{} {} not configured".format(params["output"], params["value"]) in captured.out



    @pytest.mark.parametrize('params', [
        ({"switch":"-r",       "value": "eu-west-1", "output": ["eu-west-1"]}),
        ({"switch":"--region", "value": "eu-west-1", "output": ["eu-west-1"]})])
    def test_get_commandline_arguments_region_one(self, params):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value"]]) 
        assert landingzone_config["SpecifiedRegionsOnly"] == params["output"]

    @pytest.mark.parametrize('params', [
        ({"switch":"-r",       "value1": "eu-west-1", "value2": "eu-central-1", "output": ["eu-west-1", "eu-central-1"]}),
        ({"switch":"--region", "value1": "eu-west-1", "value2": "eu-central-1", "output": ["eu-west-1", "eu-central-1"]})])
    def test_get_commandline_arguments_region_two(self, params):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value1"], params["value2"]]) 
        assert landingzone_config["SpecifiedRegionsOnly"] == params["output"]

    @pytest.mark.parametrize('params', [
        ({"switch":"-r",       "value": "NotExists", "output": "Region"}),
        ({"switch":"--region", "value": "NotExists", "output": "Region"})])
    def test_get_commandline_arguments_region_not_exists(self, capsys, params):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        with pytest.raises(InvalidParameterException):
            get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value"]]) 
        captured = capsys.readouterr()
        assert "{} {} not configured".format(params["output"], params["value"]) in captured.out

    @pytest.mark.parametrize('params', [
        ({"switch":"-r",       "value1": "eu-west-1", "value2": "NotExists", "value3": "eu-central-1", "type": "Region"}),
        ({"switch":"--region", "value1": "eu-west-1", "value2": "NotExists", "value3": "eu-central-1", "type": "Region"})])
    def test_get_commandline_arguments_region_not_exists_in_combination_with_existing_regions(self, capsys, params):

        (accounts, groups, landingzone_config) = self.get_default_accounts_groups_landingzone_config()
        with pytest.raises(InvalidParameterException):
            get_commandline_arguments(accounts, groups, landingzone_config, [params["switch"], params["value1"], params["value2"], params["value3"]]) 
        captured = capsys.readouterr()
        assert "{} {} not configured".format(params["type"], params["value2"]) in captured.out
