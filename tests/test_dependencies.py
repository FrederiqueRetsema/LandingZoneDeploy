from scripts.landingzone_deploy import *
import pytest

NO_DEPENDENCIES = []
@pytest.mark.find
class FindTests:

    def get_cloudformation_stack(self, stack_name, depends_on):
        stack = {"Name": stack_name, 
                 "FileName": "FileName", 
                 "FileHash": "my-hash", 
                 "Step": None, 
                 "Role": "MyRole", 
                 "Capabilities": [], 
                 "Parameters": [],
                 "DependsOn": depends_on}
        return stack
    
    def get_deployed_stack(self, stack_name, file_hash):
        stack = {"Name": stack_name, 
                 "FileHash": file_hash,
                 "Status": "CREATE_COMPLETE"}
        return stack

    def get_account_with_cloudformation_templates(self):
        account = {"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                   "CloudformationTemplates": {'eu-central-1': [self.get_cloudformation_stack("MyStack", NO_DEPENDENCIES)]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}}
        return account
        
    def get_account_with_two_regions_and_cloudformation_templates(self):
        account = {"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                   "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-eu-central-1", NO_DEPENDENCIES)],
                                               "eu-west-1": [self.get_cloudformation_stack("MyStack-eu-west-1", NO_DEPENDENCIES)]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}}
        return account
            
    def get_two_accounts(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999"}]
        return accounts

    def get_two_accounts_with_two_regions_and_cloudformation_templates(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                   "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                               "eu-west-1": [self.get_cloudformation_stack("MyStack-dev-eu-west-1", NO_DEPENDENCIES)]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                   "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-master-eu-central-1", NO_DEPENDENCIES)],
                                               "eu-west-1": [self.get_cloudformation_stack("MyStack-master-eu-west-1", NO_DEPENDENCIES)]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}}]
        return accounts
        
    def get_four_accounts(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999"},
                    {"Name": "audit", "ProfileName": "my-audit", "Environment": "prod", "AccountId": "888888888888"},
                    {"Name": "log-archive", "ProfileName": "my-log-archive", "Environment": "prod", "AccountId": "777777777777"}]
        return accounts

    def get_four_accounts_with_two_regions_and_dependencies(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-dev-eu-west-1", ["MyStack-master-eu-central-1-4"])]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-master-eu-central-1-1", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-2", ["MyStack-master-eu-central-1-1"]),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-3", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-4", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-master-eu-west-1", ["MyStack-master-eu-central-1-3"])]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}}]
        return accounts

    def get_four_accounts_with_two_regions_and_one_stack_with_two_dependencies(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-dev-eu-west-1", NO_DEPENDENCIES)]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-master-eu-central-1-1", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-2", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-3", ["MyStack-master-eu-central-1-1", "MyStack-master-eu-central-1-2"])],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-master-eu-west-1", NO_DEPENDENCIES)]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}}]
        return accounts

    def get_four_accounts_with_multiple_stacks_dependent_on_one_stack_over_accounts_and_regions(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-dev-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-master-eu-central-1-1", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-2", ["MyStack-master-eu-central-1-1"]),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-3", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-master-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}}]
        return accounts

    def get_four_accounts_with_nested_dependencies_over_regions_and_accounts(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-dev-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-master-eu-central-1-1", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-2", ["MyStack-dev-eu-west-1"]),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-3", ["MyStack-master-eu-central-1-2", "MyStack-master-eu-west-1"])],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-master-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [], "eu-central-1": []}}]
        return accounts

    def get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-dev-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [self.get_deployed_stack("MyStack-dev-eu-west-1", "0")], 
                                      "eu-central-1": [self.get_deployed_stack("MyStack-dev-eu-central-1", "0")]}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-master-eu-central-1-1", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-2", ["MyStack-dev-eu-west-1"]),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-3", ["MyStack-master-eu-central-1-2", "MyStack-master-eu-west-1"])],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-master-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [self.get_deployed_stack("MyStack-master-eu-west-1", "0")], 
                                      "eu-central-1": [self.get_deployed_stack("MyStack-master-eu-central-1-1", "0"), 
                                                       self.get_deployed_stack("MyStack-master-eu-central-1-2", "0"),
                                                       self.get_deployed_stack("MyStack-master-eu-central-1-3", "0")]}}]
        return accounts

    def get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks_no_update(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-dev-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [self.get_deployed_stack("MyStack-dev-eu-west-1", "my-hash")], 
                                      "eu-central-1": [self.get_deployed_stack("MyStack-dev-eu-central-1", "my-hash")]}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-master-eu-central-1-1", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-2", ["MyStack-dev-eu-west-1"]),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-3", ["MyStack-master-eu-central-1-2", "MyStack-master-eu-west-1"])],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-master-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [self.get_deployed_stack("MyStack-master-eu-west-1", "my-hash")], 
                                      "eu-central-1": [self.get_deployed_stack("MyStack-master-eu-central-1-1", "my-hash"), 
                                                       self.get_deployed_stack("MyStack-master-eu-central-1-2", "my-hash"),
                                                       self.get_deployed_stack("MyStack-master-eu-central-1-3", "my-hash")]}}]
        return accounts

    def get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks_combination_create_update_delete(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-dev-eu-central-1", NO_DEPENDENCIES)],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-dev-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [], 
                                      "eu-central-1": [self.get_deployed_stack("MyStack-dev-eu-central-1", "other-hash")]}},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999",
                     "CloudformationTemplates": {"eu-central-1": [self.get_cloudformation_stack("MyStack-master-eu-central-1-1", NO_DEPENDENCIES),
                                                                  self.get_cloudformation_stack("MyStack-master-eu-central-1-2", ["MyStack-dev-eu-west-1"])],
                                                 "eu-west-1": [self.get_cloudformation_stack("MyStack-master-eu-west-1", ["MyStack-master-eu-central-1-1"])]},
                   "DeployedStacks": {"eu-west-1": [self.get_deployed_stack("MyStack-master-eu-west-1", "my-hash")], 
                                      "eu-central-1": [self.get_deployed_stack("MyStack-master-eu-central-1-1", "my-hash"), 
                                                       self.get_deployed_stack("MyStack-master-eu-central-1-2", "my-hash"),
                                                       self.get_deployed_stack("MyStack-master-eu-central-1-3", "my-hash")]}}]
        return accounts


    def get_groups(self):
        groups = [{"Name": "AllLandingZoneAccounts", "List": ["master", "audit", "log-archive"]},
                  {"Name": "AllLandingZoneAccountsExceptMaster", "List": ["AllLandingZoneAccounts"], "Except": ["master"]}]
        return groups

    def get_landingzone_config(self):
        landingzone_config = {"MaxConcurrentAccounts": 2, 
                              "MaxConcurrentStacksPerAccount": 5,
                              "WaitTimeInSec": 1,
                              "GroupNameAllAccounts": "AllAccounts",
                              "GroupNameAllRegions": "AllRegions",
                              "Tags": [{
                                  "Key": "LandingZoneResource", 
                                  "Value": "True"
                              }],
                              "DefaultRegions": ["eu-west-1", "eu-central-1"]
                             }
        return landingzone_config

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
    
    def get_plan(self):
        plan = [{"Action": "Update", "Name": "MyStack-dev-eu-central-1", "FileName": "FileName", "Account": "development", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0},
                {"Action": "Create", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 1},
                {"Action": "Delete", "Name": "MyStack-master-eu-central-1-3", "Account": "master", "Region": "eu-central-1", "Step": 3}]
        return plan


    def test_determine_dependent_on_within_account_and_region_between_regions_between_accounts(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()

        determine_dependent_on(accounts)

        print(accounts)
        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")
        mystack_master_eu_central_1_3 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-3")
        mystack_master_eu_central_1_4 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-4")

        assert mystack_master_eu_central_1_1["DependentOn"] == [("master", "eu-central-1", "MyStack-master-eu-central-1-2")]
        assert mystack_master_eu_central_1_3["DependentOn"] == [("master", "eu-west-1", "MyStack-master-eu-west-1")]
        assert mystack_master_eu_central_1_4["DependentOn"] == [("development", "eu-west-1", "MyStack-dev-eu-west-1")]

    def test_determine_dependent_on_one_stack_with_two_dependencies(self):
        accounts = self.get_four_accounts_with_two_regions_and_one_stack_with_two_dependencies()

        determine_dependent_on(accounts)

        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")
        mystack_master_eu_central_1_2 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-2")

        assert mystack_master_eu_central_1_1["DependentOn"] == [("master", "eu-central-1", "MyStack-master-eu-central-1-3")]
        assert mystack_master_eu_central_1_2["DependentOn"] == [("master", "eu-central-1", "MyStack-master-eu-central-1-3")]


    def test_determine_dependent_on_multiple_stacks_dependent_on_one_stack_over_accounts_and_regions(self):
        accounts = self.get_four_accounts_with_multiple_stacks_dependent_on_one_stack_over_accounts_and_regions()

        determine_dependent_on(accounts)

        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")

        assert mystack_master_eu_central_1_1["DependentOn"] == [("development", "eu-west-1", "MyStack-dev-eu-west-1"),
                                                                ("master", "eu-central-1", "MyStack-master-eu-central-1-2"),
                                                                ("master", "eu-west-1", "MyStack-master-eu-west-1")]

    def test_determine_dependent_on_nested_dependencies_over_regions_and_accounts(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts()

        determine_dependent_on(accounts)

        mystack_development_eu_west_1_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-west-1")
        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")
        mystack_master_eu_central_1_2 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-2")
        mystack_master_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-west-1")

        assert mystack_development_eu_west_1_1["DependentOn"] == [("master", "eu-central-1", "MyStack-master-eu-central-1-2")]
        assert mystack_master_eu_central_1_1["DependentOn"] == [("development", "eu-west-1", "MyStack-dev-eu-west-1"),
                                                                ("master", "eu-west-1", "MyStack-master-eu-west-1")]
        assert mystack_master_eu_central_1_2["DependentOn"] == [("master", "eu-central-1", "MyStack-master-eu-central-1-3")]
        assert mystack_master_eu_west_1["DependentOn"] == [("master", "eu-central-1", "MyStack-master-eu-central-1-3")]

    def test_set_deployment_order_four_accounts_with_two_regions_and_dependencies(self):
        accounts = self.get_four_accounts_with_two_regions_and_dependencies()
        landingzone_config = self.get_landingzone_config()

        determine_dependent_on(accounts)
        set_deployment_order(accounts, 0, landingzone_config)
        print(accounts)

        for account in accounts:
            for region in account["CloudformationTemplates"]:
                for template in account["CloudformationTemplates"][region]:
                    assert template["Step"] != None

        mystack_dev_eu_central_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-central-1")
        mystack_dev_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-west-1")
        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")
        mystack_master_eu_central_1_2 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-2")
        mystack_master_eu_central_1_3 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-3")
        mystack_master_eu_central_1_4 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-4")
        mystack_master_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-west-1")

        assert mystack_dev_eu_central_1["Step"] == 0
        assert mystack_dev_eu_west_1["Step"] == 1

        assert mystack_master_eu_central_1_1["Step"] == 0
        assert mystack_master_eu_central_1_2["Step"] == 1
        assert mystack_master_eu_central_1_3["Step"] == 0
        assert mystack_master_eu_central_1_4["Step"] == 0
        assert mystack_master_eu_west_1["Step"] == 1
        assert landingzone_config["HighestStep"] == 2

    def test_set_deployment_order_four_accounts_with_two_regions_and_one_stack_with_two_dependencies(self):
        accounts = self.get_four_accounts_with_two_regions_and_one_stack_with_two_dependencies()
        landingzone_config = self.get_landingzone_config()

        determine_dependent_on(accounts)
        set_deployment_order(accounts, 0, landingzone_config)

        for account in accounts:
            for region in account["CloudformationTemplates"]:
                for template in account["CloudformationTemplates"][region]:
                    assert template["Step"] != None

        mystack_dev_eu_central_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-central-1")
        mystack_dev_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-west-1")
        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")
        mystack_master_eu_central_1_2 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-2")
        mystack_master_eu_central_1_3 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-3")
        mystack_master_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-west-1")

        assert mystack_dev_eu_central_1["Step"] == 0
        assert mystack_dev_eu_west_1["Step"] == 0

        assert mystack_master_eu_central_1_1["Step"] == 0
        assert mystack_master_eu_central_1_2["Step"] == 0
        assert mystack_master_eu_central_1_3["Step"] == 1
        assert mystack_master_eu_west_1["Step"] == 0
        assert landingzone_config["HighestStep"] == 2

    def test_set_deployment_order_four_accounts_with_multiple_stacks_dependent_on_one_stack_over_accounts_and_regions(self):
        accounts = self.get_four_accounts_with_multiple_stacks_dependent_on_one_stack_over_accounts_and_regions()
        landingzone_config = self.get_landingzone_config()

        determine_dependent_on(accounts)
        set_deployment_order(accounts, 0, landingzone_config)

        for account in accounts:
            for region in account["CloudformationTemplates"]:
                for template in account["CloudformationTemplates"][region]:
                    assert template["Step"] != None

        mystack_dev_eu_central_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-central-1")
        mystack_dev_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-west-1")
        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")
        mystack_master_eu_central_1_2 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-2")
        mystack_master_eu_central_1_3 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-3")
        mystack_master_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-west-1")

        assert mystack_dev_eu_central_1["Step"] == 0
        assert mystack_dev_eu_west_1["Step"] == 1

        assert mystack_master_eu_central_1_1["Step"] == 0
        assert mystack_master_eu_central_1_2["Step"] == 1
        assert mystack_master_eu_central_1_3["Step"] == 0
        assert mystack_master_eu_west_1["Step"] == 1
        assert landingzone_config["HighestStep"] == 2

    def test_set_deployment_order_four_accounts_with_nested_dependencies_over_regions_and_accounts(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts()
        landingzone_config = self.get_landingzone_config()

        determine_dependent_on(accounts)
        set_deployment_order(accounts, 0, landingzone_config)
        print(accounts)

        for account in accounts:
            for region in account["CloudformationTemplates"]:
                for template in account["CloudformationTemplates"][region]:
                    assert template["Step"] != None

        mystack_dev_eu_central_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-central-1")
        mystack_dev_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-west-1")
        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")
        mystack_master_eu_central_1_2 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-2")
        mystack_master_eu_central_1_3 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-3")
        mystack_master_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-west-1")

        assert mystack_dev_eu_central_1["Step"] == 0
        assert mystack_dev_eu_west_1["Step"] == 1

        assert mystack_master_eu_central_1_1["Step"] == 0
        assert mystack_master_eu_central_1_2["Step"] == 2
        assert mystack_master_eu_central_1_3["Step"] == 3
        assert mystack_master_eu_west_1["Step"] == 1
        assert landingzone_config["HighestStep"] == 4

    def test_determine_deployment_order(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts()
        landingzone_config = self.get_landingzone_config()

        determine_deployment_order(accounts, landingzone_config)

        for account in accounts:
            for region in account["CloudformationTemplates"]:
                for template in account["CloudformationTemplates"][region]:
                    assert template["Step"] != None

        mystack_dev_eu_central_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-central-1")
        mystack_dev_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-dev-eu-west-1")
        mystack_master_eu_central_1_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-1")
        mystack_master_eu_central_1_2 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-2")
        mystack_master_eu_central_1_3 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-central-1-3")
        mystack_master_eu_west_1 = find_stack_in_all_accounts(accounts, "MyStack-master-eu-west-1")

        assert mystack_dev_eu_central_1["Step"] == 0
        assert mystack_dev_eu_west_1["Step"] == 1

        assert mystack_master_eu_central_1_1["Step"] == 0
        assert mystack_master_eu_central_1_2["Step"] == 2
        assert mystack_master_eu_central_1_3["Step"] == 3
        assert mystack_master_eu_west_1["Step"] == 1
        assert landingzone_config["HighestStep"] == 4

    def test_plan_create_stack(self):
        account = self.get_account_with_cloudformation_templates()

        region = "eu-west-1"
        stack_name = "TestStack"
        file_name = "MyFile"
        role = "MyRole"
        capabilities = []
        parameters = [{
            "Key": "MyKey",
            "Value": "MyValue"
        }]
        file_hash = "MyHash"
        step = 0

        plan = plan_create_stack(account, region, stack_name, file_name, role, capabilities, parameters, file_hash, step)

        assert plan == [{
            "Action": "Create",
            "Name": stack_name,
            "FileName": file_name,
            "Account": account["Name"],
            "Region": region,
            "Role": role,
            "Capabilities": capabilities,
            "Parameters": parameters,
            "FileHash": file_hash,
            "Step": step,
        }]

    def test_plan_update_stack(self):
        account = self.get_account_with_cloudformation_templates()

        region = "eu-west-2"
        stack_name = "UpdateStack"
        file_name = "MyFile2"
        role = "MyRole2"
        capabilities = ["CAPABILITIES_NAMED_IAM"]
        parameters = []
        file_hash = "MyHash2"
        step = 1

        plan = plan_update_stack(account, region, stack_name, file_name, role, capabilities, parameters, file_hash, step)

        assert plan == [{
            "Action": "Update",
            "Name": stack_name,
            "FileName": file_name,
            "Account": account["Name"],
            "Region": region,
            "Role": role,
            "Capabilities": capabilities,
            "Parameters": parameters,
            "FileHash": file_hash,
            "Step": step,
        }]

    def test_plan_delete_stack(self):
        account = self.get_account_with_cloudformation_templates()

        region = "eu-west-3"
        stack_name = "DeleteStack"
        step = 1

        plan = plan_delete_stack(account, region, stack_name, step)

        assert plan ==  [{"Action": "Delete", "Name": stack_name, "Account": account["Name"], "Region": region, "Step": step}]


    def test_plan_change_landingzone_create(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts()
        landingzone_config = self.get_landingzone_config()

        determine_deployment_order(accounts, landingzone_config)

        plan = plan_change_landingzone(accounts, landingzone_config)

        for step in plan:
            assert step["Action"] == "Create"

        assert len(plan) > 1

    def test_plan_change_landingzone_create(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts()
        landingzone_config = self.get_landingzone_config()

        determine_deployment_order(accounts, landingzone_config)

        plan = plan_change_landingzone(accounts, landingzone_config)

        for step in plan:
            assert step["Action"] == "Create"

        assert len(plan) > 1

    def test_plan_change_landingzone_update(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks()
        landingzone_config = self.get_landingzone_config()

        determine_deployment_order(accounts, landingzone_config)

        plan = plan_change_landingzone(accounts, landingzone_config)

        for step in plan:
            print(step)
            assert step["Action"] == "Update"

        assert len(plan) > 1
               
    def test_plan_change_landingzone_no_update(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks_no_update()
        landingzone_config = self.get_landingzone_config()

        determine_deployment_order(accounts, landingzone_config)

        plan = plan_change_landingzone(accounts, landingzone_config)
        print(plan)

        assert plan == []
               

    def test_plan_change_landingzone_delete(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks()
        landingzone_config = self.get_landingzone_config()

        for account in accounts:
            for region in account["CloudformationTemplates"]:
                account["CloudformationTemplates"][region] = []


        determine_deployment_order(accounts, landingzone_config)

        plan = plan_change_landingzone(accounts, landingzone_config)
        print(plan)

        for step in plan:
            assert step["Action"] == "Delete"

        assert len(plan) > 1
               
    def test_plan_change_landingzone_combination_create_update_delete(self):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks_combination_create_update_delete()
        landingzone_config = self.get_landingzone_config()

        determine_deployment_order(accounts, landingzone_config)
        print(accounts)

        plan = plan_change_landingzone(accounts, landingzone_config)

        assert len(plan) > 1
        assert plan[0] == {"Action": "Update", "Name": "MyStack-dev-eu-central-1", "FileName": "FileName", "Account": "development", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0}
        assert plan[1] == {"Action": "Create", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 1}
        assert plan[2] == {"Action": "Delete", "Name": "MyStack-master-eu-central-1-3", "Account": "master", "Region": "eu-central-1", "Step": 3}


    def test_limit_number_of_accounts_no_change(self):
        plan = self.get_plan()
        landingzone_config = self.get_landingzone_config()
        landingzone_config["SpecifiedAccountsOnly"] = []
        landingzone_config["SpecifiedRegionsOnly"] = []
        
        limit_number_of_accounts(plan, landingzone_config)

        assert plan == [{"Action": "Update", "Name": "MyStack-dev-eu-central-1", "FileName": "FileName", "Account": "development", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0},
                        {"Action": "Create", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 1},
                        {"Action": "Delete", "Name": "MyStack-master-eu-central-1-3", "Account": "master", "Region": "eu-central-1", "Step": 3}]

    def test_limit_number_of_accounts_only_master(self):
        plan = self.get_plan()
        landingzone_config = self.get_landingzone_config()
        landingzone_config["SpecifiedAccountsOnly"] = ["master"]
        landingzone_config["SpecifiedRegionsOnly"] = []
        
        limit_number_of_accounts(plan, landingzone_config)

        assert plan == [{"Action": "Delete", "Name": "MyStack-master-eu-central-1-3", "Account": "master", "Region": "eu-central-1", "Step": 3}]

    def test_limit_number_of_accounts_only_eu_west_1(self):
        plan = self.get_plan()
        landingzone_config = self.get_landingzone_config()
        landingzone_config["SpecifiedAccountsOnly"] = []
        landingzone_config["SpecifiedRegionsOnly"] = ["eu-west-1"]
        
        limit_number_of_accounts(plan, landingzone_config)

        assert plan == [{"Action": "Create", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 1}]

    def test_limit_number_of_accounts_nothing_left_accounts(self):
        plan = self.get_plan()
        landingzone_config = self.get_landingzone_config()
        landingzone_config["SpecifiedAccountsOnly"] = ["account-1"]
        landingzone_config["SpecifiedRegionsOnly"] = []
        
        limit_number_of_accounts(plan, landingzone_config)

        assert plan == []

    def test_limit_number_of_accounts_nothing_left_regions(self):
        plan = self.get_plan()
        landingzone_config = self.get_landingzone_config()
        landingzone_config["SpecifiedAccountsOnly"] = []
        landingzone_config["SpecifiedRegionsOnly"] = ["us-east-1"]
        
        limit_number_of_accounts(plan, landingzone_config)

        assert plan == []

    def test_print_plan(self, capsys):
        plan = self.get_plan()
        
        print_plan(plan)
        captured = capsys.readouterr()

        assert "DryRun: Step 0 - Update - MyStack-dev-eu-central-1 in account development in region eu-central-1" in captured.out
        assert "DryRun: Step 1 - Create - MyStack-dev-eu-west-1 in account development in region eu-west-1" in captured.out
        assert "DryRun: Step 3 - Delete - MyStack-master-eu-central-1-3 in account master in region eu-central-1" in captured.out
    
    def test_print_all_stacks(self, capsys):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks()
        
        print_all_stacks(accounts)
        captured = capsys.readouterr()

        assert "MyStack-dev-eu-west-1 in account development in region eu-west-1 has status CREATE_COMPLETE" in captured.out
        assert "MyStack-dev-eu-central-1 in account development in region eu-central-1 has status CREATE_COMPLETE" in captured.out
        assert "MyStack-master-eu-west-1 in account master in region eu-west-1 has status CREATE_COMPLETE" in captured.out
        assert "MyStack-master-eu-central-1-1 in account master in region eu-central-1 has status CREATE_COMPLETE" in captured.out
        assert "MyStack-master-eu-central-1-2 in account master in region eu-central-1 has status CREATE_COMPLETE" in captured.out
        assert "MyStack-master-eu-central-1-3 in account master in region eu-central-1 has status CREATE_COMPLETE" in captured.out
        assert "MyStack-master-eu-central-1-3 in account master in region eu-central-1 has status CREATE_COMPLETE" in captured.out

    def test_print_stacks_with_errors(self, capsys):
        accounts = self.get_four_accounts_with_nested_dependencies_over_regions_and_accounts_and_deployed_stacks()

        status = ["CREATE_COMPLETE", "ROLLBACK_COMPLETE", "UPDATE_ROLLBACK_COMPLETE", "UPDATE_FAILED", "ROLLBACK_FAILED", "UPDATE_ROLLBACK_FAILED"]
        counter = 0
        for account in accounts:
            for region in account["DeployedStacks"]:
                for stack in account["DeployedStacks"][region]:
                    stack["Status"] = status[counter]
                    counter += 1
                    

        print_stacks_with_errors(accounts)        
        captured = capsys.readouterr()
        print(captured)

        assert "MyStack-master-eu-central-1-1 in account master in region eu-central-1 has status UPDATE_FAILED" in captured.out
        assert "MyStack-master-eu-west-1 in account master in region eu-west-1 has status UPDATE_ROLLBACK_COMPLETE" in captured.out
        assert "MyStack-master-eu-central-1-1 in account master in region eu-central-1 has status UPDATE_FAILED" in captured.out
        assert "MyStack-master-eu-central-1-2 in account master in region eu-central-1 has status ROLLBACK_FAILED" in captured.out
        assert "MyStack-master-eu-central-1-3 in account master in region eu-central-1 has status UPDATE_ROLLBACK_FAILED" in captured.out
