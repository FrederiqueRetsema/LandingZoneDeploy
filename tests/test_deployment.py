from scripts.landingzone_deploy import *

from unittest import mock
import pytest

CLOUDFORMATION_TESTFILE = "./tests/testfiles/MyBucket.cfn.yaml"

@pytest.mark.deployment
class DeploymentTests:

    def get_two_accounts(self):
        accounts = [{"Name": "development", "ProfileName": "my-dev", "Environment": "dev", "AccountId": "111111111111"},
                    {"Name": "master", "ProfileName": "my-master", "Environment": "prod", "AccountId": "999999999999"}]
        return accounts

    def get_landingzone_config(self):
        landingzone_config = {"MaxConcurrentAccounts": 1, 
                              "MaxConcurrentStacksPerAccount": 2,
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

    def get_plan(self):
        plan = [{"Action": "Update", "Name": "MyStack-dev-eu-central-1", "FileName": "FileName", "Account": "development", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0},
                {"Action": "Create", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 1},
                {"Action": "Delete", "Name": "MyStack-master-eu-central-1-3", "Account": "master", "Region": "eu-central-1", "Step": 3}]
        return plan

    def get_1_current_deployments(self):
        current_deployments = [{"Action": "Update", "Name": "MyStack-dev-eu-central-1", "FileName": "FileName", "Account": "development", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0}]
        return current_deployments

    def get_5_current_deployments(self):
        current_deployments = [
            {"Action": "Update", "Name": "MyStack-master-eu-central-1-1", "FileName": "FileName", "Account": "master", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0},
            {"Action": "Insert", "Name": "MyStack-dev-eu-central-1-2", "FileName": "FileName", "Account": "development", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0},
            {"Action": "Insert", "Name": "MyStack-dev-eu-central-1-3", "FileName": "FileName", "Account": "development", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0},
            {"Action": "Insert", "Name": "MyStack-dev-eu-central-1-4", "FileName": "FileName", "Account": "development", "Region": "eu-central-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0},
            {"Action": "Insert", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0}
        ]
        return current_deployments

    def test_determine_current_step_when_there_are_deployments(self):
        plan = self.get_plan()
        current_deployments = self.get_1_current_deployments()
        
        step = determine_current_step(current_deployments, plan)

        assert step == 0

    def test_determine_current_step_when_there_are_no_deployments(self):
        plan = self.get_plan()
        plan.remove(plan[0])
        current_deployments = []
        
        step = determine_current_step(current_deployments, plan)

        assert step == 1

    def test_determine_current_step_when_there_are_no_deployments_and_there_is_no_plan(self):
        plan = []
        current_deployments = []
        
        step = determine_current_step(current_deployments, plan)

        assert step == 0

    def test_replace_account_names_in_template_body_account_name(self):
        accounts = self.get_two_accounts()

        original_text = "-={development}=-"
        new_text = replace_account_names_in_template_body(accounts, original_text)

        assert new_text == "-=111111111111=-"

    def test_replace_account_names_in_template_body_profile_name(self):
        accounts = self.get_two_accounts()

        original_text = ">>{my-master}<<"
        new_text = replace_account_names_in_template_body(accounts, original_text)

        assert new_text == ">>999999999999<<"

    def test_replace_account_names_in_template_body_dont_touch_aws_replacements(self):
        accounts = self.get_two_accounts()

        original_text = "${AWS::AccountId}"
        new_text = replace_account_names_in_template_body(accounts, original_text)

        assert new_text == "${AWS::AccountId}"

    def test_get_template_body(self):
        content = get_template_body(CLOUDFORMATION_TESTFILE)

        assert "AWS::S3::BucketPolicy" in content
        assert "{development}" in content

    def test_get_template_body_error(self, capsys):

        content = get_template_body("./NoExistentFile/nothing.txt")
        captured = capsys.readouterr()
        assert "[Errno 2] No such file or directory: './NoExistentFile/nothing.txt'" in captured.out
        assert content == ""

    def test_get_role_arn(self):
        accounts = self.get_two_accounts()
        account = accounts[0]

        assert get_role_arn(account, "MyRole") == "arn:aws:iam::111111111111:role/MyRole"

    def test_determine_1_concurrent_accounts(self):
        concurrent_deployments = self.get_1_current_deployments()

        concurrent_accounts = determine_concurrent_accounts(concurrent_deployments)

        assert len(concurrent_accounts) == 1

    def test_determine_2_concurrent_accounts(self):
        concurrent_deployments = self.get_5_current_deployments()

        concurrent_accounts = determine_concurrent_accounts(concurrent_deployments)
        print(concurrent_accounts)

        assert len(concurrent_accounts) == 2

    def test_determine_1_concurrent_stacks_per_account(self):
        concurrent_deployments = self.get_1_current_deployments()

        concurrent_stacks = determine_concurrent_stacks_per_account(concurrent_deployments)

        assert len(concurrent_stacks) == 1
        assert concurrent_stacks["development"] == 1

    def test_determine_2_concurrent_stacks_per_account(self):
        concurrent_deployments = self.get_5_current_deployments()

        concurrent_stacks = determine_concurrent_stacks_per_account(concurrent_deployments)
        print(concurrent_stacks)

        assert len(concurrent_stacks) == 2
        assert concurrent_stacks["master"] == 1
        assert concurrent_stacks["development"] == 4    

    def test_wait_for_now(self, capsys):
        current_deployments = self.get_5_current_deployments()
        plan = self.get_plan()

        wait_for_now(1, current_deployments, plan)
        captured = capsys.readouterr()
        assert "Step 0: 5 changes in 2 accounts are being deployed. Step 0: 1 changes waiting. Step 1: 1 changes waiting." in captured.out

    def test_execute_plan_break(self, capsys):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan = []

        execute_plan(accounts, plan, landingzone_config)
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_execute_plan_break(self, capsys):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan = []

        execute_plan(accounts, plan, landingzone_config)
        captured = capsys.readouterr()
        assert captured.out == ""

     # Mind that other tests for execute_plan are in the test_boto3.py file.
     