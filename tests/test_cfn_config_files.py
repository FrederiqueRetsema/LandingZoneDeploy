from scripts.landingzone_deploy import *
import pytest

CLOUDFORMATION_TESTFILE = "./tests/testfiles/MyBucket.cfn.yaml"
CLOUDFORMATION_CONFIG_TESTFILE = "./tests/testfiles/MyBucket.config.yaml"
CLOUDFORMATION_CONFIG_TESTFILES = "./tests/**/*.config.yaml"
CLOUDFORMATION_DEFAULT_STACK_NAME = "MyBucket"

@pytest.mark.cfn_config_files
class Boto3Tests:

    def get_accounts(self):
        accounts = [{"Name": "development", "ProfileName": "my-development", "Environment": "dev", "AccountId": "111111111111", "CloudformationTemplates": 
                         {"eu-west-1": [], "eu-central-1": []}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "dev", "AccountId": "111111111111", "CloudformationTemplates": 
                         {"eu-west-1": [], "eu-central-1": []}}]
        return accounts

    def get_accounts_without_cloudformation_templates(self):
        accounts = [{"Name": "development", "ProfileName": "my-development", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "dev", "AccountId": "111111111111"}]
        return accounts

    def get_landingzone_config(self):
        landingzone_config = {"DefaultAccounts": ["development", "master"], 
                              "DefaultRegions": ["eu-west-1", "eu-central-1"], 
                              "Tags": [{"Key": "LandingZoneResource", "Value": "True"}]}
        return landingzone_config

    def get_groups(self):
        groups = [{"Name": "AllLandingZoneAccounts", "List": ["master", "development"]}]
        return groups

    def get_regions(self):
        regions = ["eu-west-1", "eu-central-1"]
        return regions

    def test_add_stack_to_accounts_one_account_one_region(self):
        accounts = self.get_accounts()

        file_name = "./templates\\Windows\\Parameter.cfn.yaml"
        stack_name = "Parameter"
        file_hash = "myhash"
        role = "myrole"
        capabilities = ["CAPABILITY_NAMED_IAM"]
        parameters = [{"Key": "MyParameter", "Value": "MyValue"}]
        depends_on = ["OtherStack"]
        account_names = ["development"]
        region_names = ["eu-west-1"]

        add_stack_to_accounts(accounts, file_name, stack_name, file_hash, role, capabilities, parameters, depends_on, account_names, region_names)

        assert accounts[0]['CloudformationTemplates']['eu-west-1'] == \
                [{"Name": stack_name, 
                  "FileName": file_name, 
                  "FileHash": file_hash, 
                  "Step": None, 
                  "Role": role, 
                  "Capabilities": capabilities, 
                  "Parameters": parameters,
                  "DependsOn": depends_on}]
        assert accounts[0]['CloudformationTemplates']['eu-central-1'] == []
        assert accounts[1]['CloudformationTemplates']['eu-west-1'] == []
        assert accounts[1]['CloudformationTemplates']['eu-central-1'] == []

    def test_add_stack_to_accounts_one_account_multiple_regions(self):
        accounts = self.get_accounts()

        file_name = "./templates\\Windows\\Parameter.cfn.yaml"
        stack_name = "Parameter"
        file_hash = "myhash"
        role = "myrole"
        capabilities = ["CAPABILITY_NAMED_IAM"]
        parameters = [{"Key": "MyParameter", "Value": "MyValue"}]
        depends_on = ["OtherStack"]
        account_names = ["development"]
        region_names = ["eu-west-1", "eu-central-1"]

        add_stack_to_accounts(accounts, file_name, stack_name, file_hash, role, capabilities, parameters, depends_on, account_names, region_names)

        assert accounts[0]['CloudformationTemplates']['eu-west-1'] == \
                [{"Name": stack_name, 
                  "FileName": file_name, 
                  "FileHash": file_hash, 
                  "Step": None, 
                  "Role": role, 
                  "Capabilities": capabilities, 
                  "Parameters": parameters,
                  "DependsOn": depends_on}]
        assert accounts[0]['CloudformationTemplates']['eu-central-1'] == \
                [{"Name": stack_name, 
                  "FileName": file_name, 
                  "FileHash": file_hash, 
                  "Step": None, 
                  "Role": role, 
                  "Capabilities": capabilities, 
                  "Parameters": parameters,
                  "DependsOn": depends_on}]
        assert accounts[1]['CloudformationTemplates']['eu-west-1'] == []
        assert accounts[1]['CloudformationTemplates']['eu-central-1'] == []

    def test_add_stack_to_accounts_multiple_accounts_multiple_regions(self):
        accounts = self.get_accounts()

        file_name = "./templates\\Windows\\Parameter.cfn.yaml"
        stack_name = "Parameter"
        file_hash = "myhash"
        role = "myrole"
        capabilities = ["CAPABILITY_NAMED_IAM"]
        parameters = [{"Key": "MyParameter", "Value": "MyValue"}]
        depends_on = ["OtherStack"]
        account_names = ["development", "master"]
        region_names = ["eu-west-1", "eu-central-1"]

        add_stack_to_accounts(accounts, file_name, stack_name, file_hash, role, capabilities, parameters, depends_on, account_names, region_names)

        assert accounts[0]['CloudformationTemplates']['eu-west-1'] == \
                [{"Name": stack_name, 
                  "FileName": file_name, 
                  "FileHash": file_hash, 
                  "Step": None, 
                  "Role": role, 
                  "Capabilities": capabilities, 
                  "Parameters": parameters,
                  "DependsOn": depends_on}]
        assert accounts[0]['CloudformationTemplates']['eu-central-1'] == \
                [{"Name": stack_name, 
                  "FileName": file_name, 
                  "FileHash": file_hash, 
                  "Step": None, 
                  "Role": role, 
                  "Capabilities": capabilities, 
                  "Parameters": parameters,
                  "DependsOn": depends_on}]
        assert accounts[1]['CloudformationTemplates']['eu-west-1'] == \
                [{"Name": stack_name, 
                  "FileName": file_name, 
                  "FileHash": file_hash, 
                  "Step": None, 
                  "Role": role, 
                  "Capabilities": capabilities, 
                  "Parameters": parameters,
                  "DependsOn": depends_on}]
        assert accounts[1]['CloudformationTemplates']['eu-central-1'] == \
                [{"Name": stack_name, 
                  "FileName": file_name, 
                  "FileHash": file_hash, 
                  "Step": None, 
                  "Role": role, 
                  "Capabilities": capabilities, 
                  "Parameters": parameters,
                  "DependsOn": depends_on}]

    def test_determine_cloudformation_name_from_config_filename_windows(self):
        assert determine_cloudformation_file_name_from_config_filename("./templates\\Windows\\MyFilename.config.yaml") == \
               {"dir":"./templates\\Windows\\", "filename_without_extension": "MyFilename"}

    def test_get_file_hash_file_exists(self):
        assert get_file_hash(CLOUDFORMATION_TESTFILE) != "0"

    def test_get_file_hash_file_doesnt_exist(self):
        assert get_file_hash("file_that_doesnt_exist") == "0"

    def test_init_cloudformation_templates(self):
        accounts = self.get_accounts_without_cloudformation_templates()
        landingzone_config = self.get_landingzone_config()

        init_cloudformation_templates(accounts, landingzone_config)

        assert accounts[0]["CloudformationTemplates"]["eu-west-1"] == []
        assert accounts[0]["CloudformationTemplates"]["eu-central-1"] == []

    def test_check_cloudformation_config_valid(self):
        accounts = self.get_accounts_without_cloudformation_templates()
        regions = self.get_regions()

        check_cloudformation_config(accounts, regions, ["master", "development"], ["eu-west-1", "eu-central-1"])

        assert True

    def test_check_cloudformation_config_account_does_not_exist(self, capsys):
        accounts = self.get_accounts_without_cloudformation_templates()
        regions = self.get_regions()

        with pytest.raises(InvalidConfigFileException):
            check_cloudformation_config(accounts, regions, ["account-1", "development"], ["eu-west-1", "eu-central-1"])
        captured = capsys.readouterr()
        assert "Account account-1 does not exist" in captured.out

    def test_check_cloudformation_config_region_does_not_exist(self, capsys):
        accounts = self.get_accounts_without_cloudformation_templates()
        regions = self.get_regions()

        with pytest.raises(InvalidConfigFileException):
            check_cloudformation_config(accounts, regions, ["master", "development"], ["eu-west-1", "us-east-1"])
        captured = capsys.readouterr()
        assert "Region us-east-1 does not exist" in captured.out

    def test_parse_cloudformation_config_no_defaults_in_config(self):
        landingzone_config = self.get_landingzone_config()
        groups = self.get_groups()

        file_name = CLOUDFORMATION_CONFIG_TESTFILE
        stack_name_param = "MyStackName"
        role_param = "MyRole"
        depends_on_param = ["DependsOn"]
        capabilities_param = ["CAPABILITY_NAMED_IAM"]
        parameters_param = [{
                      "Key": "MyKey",
                      "Value": "MyValue"
                  }]
        accounts_to_param = ["account-1", "account-2"]
        regions_to_param = ["eu-west-1", "eu-central-1"]
        deploy_to_param = {
                      "Accounts": accounts_to_param,
                      "Regions": regions_to_param
                  }
        file_hash_param = "NotNull"
        config_param = {"StackName": stack_name_param,
                  "Role": role_param,
                  "DependsOn": depends_on_param,
                  "Capabilities": capabilities_param,
                  "Parameters": parameters_param,
                  "DeployTo": deploy_to_param,
                  "FileHash": file_hash_param
                  }

        (cloudformation_filename, stack_name, file_hash, role, capabilities, parameters, depends_on, to_accounts, to_regions) = \
            parse_cloudformation_config(landingzone_config, groups, file_name, config_param)

        assert cloudformation_filename == CLOUDFORMATION_TESTFILE
        assert stack_name == stack_name_param
        assert file_hash != "0"
        assert role == role_param
        assert capabilities == capabilities_param
        assert parameters == parameters_param
        assert depends_on == depends_on_param
        assert to_accounts == accounts_to_param
        assert to_regions == regions_to_param

    def test_parse_cloudformation_config_with_defaults_deploy_to_accounts_in_config(self):
        landingzone_config = self.get_landingzone_config()
        groups = self.get_groups()

        file_name = CLOUDFORMATION_CONFIG_TESTFILE
        accounts_to_param = ["account-1"]
        deploy_to_param = {
                      "Accounts": accounts_to_param
                  }
        config_param = {"DeployTo": deploy_to_param}

        (cloudformation_filename, stack_name, file_hash, role, capabilities, parameters, depends_on, to_accounts, to_regions) = \
            parse_cloudformation_config(landingzone_config, groups, file_name, config_param)

        assert cloudformation_filename == CLOUDFORMATION_TESTFILE
        assert stack_name == CLOUDFORMATION_DEFAULT_STACK_NAME
        assert file_hash != "0"
        assert role == ""
        assert capabilities == []
        assert parameters == []
        assert depends_on == []
        assert to_accounts == accounts_to_param
        assert to_regions == landingzone_config["DefaultRegions"]

    def test_parse_cloudformation_config_with_defaults_deploy_to_regions_in_config(self):
        landingzone_config = self.get_landingzone_config()
        groups = self.get_groups()

        file_name = CLOUDFORMATION_CONFIG_TESTFILE
        regions_param = ["us-east-1"]
        deploy_to_param = {
                      "Regions": regions_param
                  }
        config_param = {"DeployTo": deploy_to_param}

        (cloudformation_filename, stack_name, file_hash, role, capabilities, parameters, depends_on, to_accounts, to_regions) = \
            parse_cloudformation_config(landingzone_config, groups, file_name, config_param)

        assert cloudformation_filename == CLOUDFORMATION_TESTFILE
        assert stack_name == CLOUDFORMATION_DEFAULT_STACK_NAME
        assert file_hash != "0"
        assert role == ""
        assert capabilities == []
        assert parameters == []
        assert depends_on == []
        assert to_accounts == landingzone_config["DefaultAccounts"]
        assert to_regions == ["us-east-1"]

    def test_parse_cloudformation_config_with_defaults_no_deploy_to(self):
        landingzone_config = self.get_landingzone_config()
        groups = self.get_groups()

        file_name = CLOUDFORMATION_CONFIG_TESTFILE
        config_param = {"StackName": "MyStackName"}

        (cloudformation_filename, stack_name, file_hash, role, capabilities, parameters, depends_on, to_accounts, to_regions) = \
            parse_cloudformation_config(landingzone_config, groups, file_name, config_param)

        assert cloudformation_filename == CLOUDFORMATION_TESTFILE
        assert stack_name == "MyStackName"
        assert file_hash != "0"
        assert role == ""
        assert capabilities == []
        assert parameters == []
        assert depends_on == []
        assert to_accounts == landingzone_config["DefaultAccounts"]
        assert to_regions == landingzone_config["DefaultRegions"]

    def test_get_cloudformation_templates_test_stdout(self, capsys):
        accounts = self.get_accounts()
        groups = self.get_groups()
        landingzone_config = self.get_landingzone_config()

        get_cloudformation_templates(accounts, groups, landingzone_config, CLOUDFORMATION_CONFIG_TESTFILES)
        captured = capsys.readouterr()

        assert "MyBucket.config.yaml" in captured.out

    def test_get_cloudformation_templates_test_parsing(self):
        accounts = self.get_accounts()
        groups = self.get_groups()
        landingzone_config = self.get_landingzone_config()

        get_cloudformation_templates(accounts, groups, landingzone_config, CLOUDFORMATION_CONFIG_TESTFILES)

        assert accounts[0]["CloudformationTemplates"]["eu-west-1"] == []
        assert accounts[0]["CloudformationTemplates"]["eu-central-1"][0]['Name'] == "MyBucket"

    def test_get_cloudformation_templates_test_non_existing_files(self, capsys):
        accounts = self.get_accounts()
        groups = self.get_groups()
        landingzone_config = self.get_landingzone_config()

        get_cloudformation_templates(accounts, groups, landingzone_config, "./NonExistingDir/abc.config.yaml")

        # Will not get error messages, this is dealt with within the glob module
        assert True

