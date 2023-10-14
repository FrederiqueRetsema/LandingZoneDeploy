from scripts.landingzone_deploy import *
import pytest

NO_DEPENDENCIES = []

@pytest.mark.find
class FindTests:

    def get_stack(self, stack_name, depends_on):
        stack = {"Name": stack_name, 
                 "FileName": "FileName", 
                 "FileHash": "my-hash", 
                 "Step": None, 
                 "Role": "MyRole", 
                 "Capabilities": [], 
                 "Parameters": [],
                 "DependsOn": depends_on}
        return stack

    def get_account_with_cloudformation_templates(self):
        account = {"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                   "CloudformationTemplates": {'eu-central-1': [self.get_stack("MyStack", NO_DEPENDENCIES)]}}
        return account
        
    def get_account_with_two_regions_and_cloudformation_templates(self):
        account = {"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                   "CloudformationTemplates": {"eu-central-1": [self.get_stack("MyStack-eu-central-1", NO_DEPENDENCIES)],
                                               "eu-west-1": [self.get_stack("MyStack-eu-west-1", NO_DEPENDENCIES)]}}
        return account
            
    def get_two_accounts(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999"}]
        return accounts

    def get_two_accounts_with_two_regions_and_cloudformation_templates(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                   "CloudformationTemplates": {"eu-central-1": [self.get_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                               "eu-west-1": [self.get_stack("MyStack-dev-eu-west-1", NO_DEPENDENCIES)]}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                   "CloudformationTemplates": {"eu-central-1": [self.get_stack("MyStack-master-eu-central-1", NO_DEPENDENCIES)],
                                               "eu-west-1": [self.get_stack("MyStack-master-eu-west-1", NO_DEPENDENCIES)]}}]
        return accounts
        
    def get_four_accounts(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999"},
                    {"Name": "audit", "ProfileName": "my-audit", "Environment": "prod", "AccountId": "888888888888"},
                    {"Name": "log-archive", "ProfileName": "my-log-archive", "Environment": "prod", "AccountId": "777777777777"}]
        return accounts

    def get_four_accounts_with_two_regions_and_dependencies(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                     "CloudformationTemplates": {"eu-central-1": [self.get_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_stack("MyStack-dev-eu-west-1", ["MyStack-master-eu-central-1-4"])]}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                     "CloudformationTemplates": {"eu-central-1": [self.get_stack("MyStack-master-eu-central-1-1", NO_DEPENDENCIES),
                                                                  self.get_stack("MyStack-master-eu-central-1-2", ["MyStack-master-eu-central-1-1"]),
                                                                  self.get_stack("MyStack-master-eu-central-1-3", NO_DEPENDENCIES),
                                                                  self.get_stack("MyStack-master-eu-central-1-4", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_stack("MyStack-master-eu-west-1", ["MyStack-master-eu-central-1-3"])]}}]
        return accounts


    def get_groups(self):
        groups = [{"Name": "AllLandingZoneAccounts", "List": ["master", "audit", "log-archive"]},
                  {"Name": "AllLandingZoneAccountsExceptMaster", "List": ["AllLandingZoneAccounts"], "Except": ["master"]}]
        return groups

    def get_regions(self):
        regions = ["eu-west-1", "eu-central-1", "us-east-1"]
        return regions

    def get_tag_list(self):
        tag_list = [{"Key": "Hash", "Value": "123"}]
        return tag_list
    
    def get_cloudformation_templates(self):
        cloudformation_templates = [{"Name": "MyBucket", 
                                     "FileName": "./tests\\testfiles\\MyBucket.cfn.yaml", 
                                     "FileHash": "8f389d2dc35e194fc53ec2789f18051f", 
                                     "Step": None,
                                     "Role": "MyBucketRole", 
                                     "Capabilities": [], 
                                     "Parameters": [], 
                                     "DependsOn": ["MyBucketRole"]}]
        return cloudformation_templates


    def test_find_account_first_account_based_on_name(self):
        accounts = self.get_two_accounts()
        assert find_account(accounts, "development") == {"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"}

    def test_find_account_second_account_based_on_name(self):
        accounts = self.get_two_accounts()
        assert find_account(accounts, "master") == {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999"}

    def test_find_account_first_account_based_on_profile_name(self):
        accounts = self.get_two_accounts()
        assert find_account(accounts, "my-dev") == {"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"}

    def test_find_account_second_account_based_on_profile_name(self):
        accounts = self.get_two_accounts()
        assert find_account(accounts, "my-master") == {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999"}

    def test_find_account_not_found(self):
        accounts = self.get_two_accounts()
        assert find_account(accounts, "no-account") is None


    def test_find_account_names_based_on_environment_first(self):
        accounts = self.get_two_accounts()
        assert find_account_names_based_on_environment(accounts, "dev") == ["development"]
    
    def test_find_account_names_based_on_environment_second(self):
        accounts = self.get_two_accounts()
        assert find_account_names_based_on_environment(accounts, "prod") == ["master"]
    
    def test_find_account_names_based_on_environment_three_accounts(self):
        accounts = self.get_four_accounts()
        assert find_account_names_based_on_environment(accounts, "prod") == ["master", "audit", "log-archive"]
    
    def test_find_account_names_based_on_environment_no_accounts(self):
        accounts = self.get_four_accounts()
        assert find_account_names_based_on_environment(accounts, "no-env") is None


    def test_find_account_names_based_on_group_name_first(self):
        groups = self.get_groups()
        assert find_account_names_based_on_group_name(groups, "AllLandingZoneAccounts") == ["master", "audit", "log-archive"]

    def test_find_account_names_based_on_group_name_no_group(self):
        groups = self.get_groups()
        assert find_account_names_based_on_group_name(groups, "NotExist") is None

    def test_find_account_names_based_on_account_name_first(self):
        accounts = self.get_four_accounts()
        assert find_account_names_based_on_account_name(accounts, "development") == ["development"]

    def test_find_account_names_based_on_account_name_no_profile(self):
        accounts = self.get_four_accounts()
        assert find_account_names_based_on_account_name(accounts, "my-dev") is None

    def test_find_account_names_based_on_account_name_no_account(self):
        accounts = self.get_four_accounts()
        assert find_account_names_based_on_account_name(accounts, "NotExist") is None


    def test_find_account_names_based_on_profile_name_first(self):
        accounts = self.get_four_accounts()
        assert find_account_names_based_on_profile_name(accounts, "my-dev") == ["development"]

    def test_find_account_names_based_on_profile_name_no_account(self):
        accounts = self.get_four_accounts()
        assert find_account_names_based_on_profile_name(accounts, "development") is None

    def test_find_account_names_based_on_profile_name_no_account(self):
        accounts = self.get_four_accounts()
        assert find_account_names_based_on_profile_name(accounts, "NotExist") is None


    def test_find_region_based_on_region_name_first(self):
        regions = self.get_regions()
        assert find_region_based_on_region_name(regions, "eu-west-1") == ["eu-west-1"]

    def test_find_region_based_on_region_name_no_region(self):
        regions = self.get_regions()
        assert find_region_based_on_region_name(regions, "Ireland") is None

    def test_find_value_in_tag_list_existing_key(self):
        tag_list = self.get_tag_list()
        assert find_value_in_tag_list(tag_list, "Hash") == "123"

    def test_find_value_in_tag_list_not_exists(self):
        tag_list = self.get_tag_list()
        assert find_value_in_tag_list(tag_list, "NotExists") is None


    def test_find_stack_in_cloudformation_templates(self):
        cloudformation_templates = self.get_cloudformation_templates()

        template = find_stack_in_cloudformation_templates(cloudformation_templates, "MyBucket")

        assert template["Name"] == "MyBucket"
        assert template["Role"] == "MyBucketRole"

    def test_find_stack_in_cloudformation_templates_not_exists(self):
        cloudformation_templates = self.get_cloudformation_templates()

        template = find_stack_in_cloudformation_templates(cloudformation_templates, "NoTemplate")

        assert template is None


    def test_find_stack_in_account(self):
        account = self.get_account_with_cloudformation_templates()

        stack = find_stack_in_account(account, "MyStack")

        assert stack == self.get_stack("MyStack", NO_DEPENDENCIES)

    def test_find_stack_in_account_not_exists(self):
        account = self.get_account_with_cloudformation_templates()

        stack = find_stack_in_account(account, "NotExists")

        assert stack is None


    def test_find_stack_in_region_in_account(self):
        account = self.get_account_with_two_regions_and_cloudformation_templates()

        stack = find_stack_in_region_in_account(account, "eu-west-1", "MyStack-eu-west-1")

        assert stack == self.get_stack("MyStack-eu-west-1", NO_DEPENDENCIES)

    def test_find_stack_in_region_in_account_stack_not_exists(self):
        account = self.get_account_with_two_regions_and_cloudformation_templates()

        stack = find_stack_in_region_in_account(account, "eu-west-1", "MyStack-eu-central-1")

        assert stack is None

    def test_find_stack_in_region_in_account_region_not_exists(self):
        account = self.get_account_with_two_regions_and_cloudformation_templates()

        stack = find_stack_in_region_in_account(account, "us-east-1", "MyStack-eu-west-1")

        assert stack is None


    def test_find_stack_in_all_accounts_first_account_first_region(self):
        accounts = self.get_two_accounts_with_two_regions_and_cloudformation_templates()

        stack = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-west-1")

        assert stack == self.get_stack("MyStack-dev-eu-west-1", NO_DEPENDENCIES)

    def test_find_stack_in_all_accounts_second_account_second_region(self):
        accounts = self.get_two_accounts_with_two_regions_and_cloudformation_templates()

        stack = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1")

        assert stack == self.get_stack("MyStack-master-eu-central-1", NO_DEPENDENCIES)

    def test_find_stack_in_all_accounts_not_exists(self):
        accounts = self.get_two_accounts_with_two_regions_and_cloudformation_templates()

        stack = find_stack_in_all_accounts(accounts, "NotExist")

        assert stack is None


    def test_find_dependent_stack_same_templates(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        templates = accounts[1]["CloudformationTemplates"]["eu-central-1"]
        stack_name = "MyStack-master-eu-central-1-2"
        depends_on = "MyStack-master-eu-central-1-1"

        stack = find_dependent_stack(templates, accounts[0], accounts, stack_name, depends_on)

        assert stack["Name"] == depends_on

    def test_find_dependent_stack_same_region(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        templates = accounts[1]["CloudformationTemplates"]["eu-central-1"]
        stack_name = "MyStack-master-eu-west-1"
        depends_on = "MyStack-master-eu-central-1-3"

        stack = find_dependent_stack(templates, accounts[1], accounts, stack_name, depends_on)

        assert stack["Name"] == depends_on

    def test_find_dependent_stack_all_accounts(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        templates = accounts[1]["CloudformationTemplates"]["eu-central-1"]
        stack_name = "MyStack-dev-eu-west-1"
        depends_on = "MyStack-master-eu-central-1-4"

        stack = find_dependent_stack(templates, accounts[1], accounts, stack_name, depends_on)

        assert stack["Name"] == depends_on

    def test_find_dependent_stack_not_found(self, capsys):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        templates = accounts[1]["CloudformationTemplates"]["eu-central-1"]
        stack_name = "MyStack-master-eu-central-1-2"
        depends_on = "NotExists"
        stack = None

        with pytest.raises(DependencyException):
            stack = find_dependent_stack(templates, accounts[1], accounts, stack_name, depends_on)
        captured = capsys.readouterr()

        assert stack is None
        assert "Dependency incorrect: dependency in stack MyStack-master-eu-central-1-2 refers to non existing stack name NotExists" in captured.out


    def test_find_stack_in_account_in_region(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        account_name = "master"
        stack_name = "MyStack-master-eu-central-1-2"

        stack = find_stack_in_region_in_accounts_list(accounts, account_name, "eu-central-1", stack_name)

        assert stack["Name"] == stack_name


    def test_find_stack_in_account_in_incorrect_region(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        account_name = "master"
        stack_name = "MyStack-master-eu-central-1-2"

        stack = find_stack_in_region_in_accounts_list(accounts, account_name, "eu-west-1", stack_name)

        assert stack is None

    def test_find_stack_in_account_in_incorrect_account(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        account_name = "master"
        stack_name = "MyStack-dev-eu-central-1-2"

        stack = find_stack_in_region_in_accounts_list(accounts, account_name, "eu-central-1", stack_name)

        assert stack is None

    def test_find_stack_in_account_in_non_existent_region(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        account_name = "master"
        stack_name = "MyStack-master-eu-central-1-2"

        stack = find_stack_in_region_in_accounts_list(accounts, account_name, "NotExist", stack_name)

        assert stack is None

    def test_find_stack_in_account_in_non_existent_account(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        account_name = "NotExist"
        stack_name = "MyStack-dev-eu-central-1-2"

        stack = find_stack_in_region_in_accounts_list(accounts, account_name, "eu-central-1", stack_name)

        assert stack is None


