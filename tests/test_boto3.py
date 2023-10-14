from scripts.landingzone_deploy import *

from unittest import mock
import pytest


@pytest.mark.boto3
class Boto3Tests:

    def get_one_landingzone_stack(self):
        one_stack =  {
            "Stacks": [
                {
                    "StackName": "TestStack",
                    "StackStatus": "CREATE_COMPLETE",
                    "Tags": [{
                        "Key": "LandingZoneResource",
                        "Value": "True"
                    }, {
                        "Key": "FileHash",
                        "Value": "hash-value"
                    }, {
                        "Key": "Step",
                        "Value": "0"
                    }]
                }]}

        return one_stack

    def get_one_landingzone_stack_two_tags(self):
        one_stack =  {
            "Stacks": [
                {
                    "StackName": "TestStack",
                    "StackStatus": "CREATE_COMPLETE",
                    "Tags": [{
                        "Key": "LandingZoneResource",
                        "Value": "True"
                    },{
                        "Key": "ShoudHaveThisTagToo",
                        "Value": "True"
                    }, {
                        "Key": "FileHash",
                        "Value": "hash-value"
                    }, {
                        "Key": "Step",
                        "Value": "0"
                    }]
                }]}

        return one_stack
    
    def get_one_stack_in_landingzone_format(self):

        return {"Name": "TestStack", "FileHash": "hash-value", "Step": "0", "Status": "CREATE_COMPLETE"}

    def get_one_non_landingzone_stack(self):
        one_stack =  {
            "Stacks": [
                {
                    "StackName": "TestStack",
                    "StackStatus": "CREATE_COMPLETE",
                    "Tags": []
                }]}

        return one_stack
    
    def get_two_landingzone_stacks_with_next_token(self):
        two_stacks =  [{
            "Stacks": [
                {
                    "StackName": "TestStack",
                    "StackStatus": "CREATE_COMPLETE",
                    "Tags": [{
                        "Key": "LandingZoneResource",
                        "Value": "True"
                    }, {
                        "Key": "FileHash",
                        "Value": "hash-value"
                    }, {
                        "Key": "Step",
                        "Value": "0"
                    }],
                }],
                "NextToken": "MyToken"
            },{
           "Stacks": [
                {
                    "StackName": "SecondStack",
                    "StackStatus": "CREATE_COMPLETE",
                    "Tags": [{
                        "Key": "LandingZoneResource",
                        "Value": "True"
                    }, {
                        "Key": "FileHash",
                        "Value": "other-hash-value"
                    }, {
                        "Key": "Step",
                        "Value": "1"
                    }]
                }]}
            ]

        return two_stacks

    def get_two_landingzone_stacks_with_next_token_in_landingzone_format(self):

        return [{"Name": "TestStack", "FileHash": "hash-value", "Step": "0", "Status": "CREATE_COMPLETE"},
                {"Name": "SecondStack", "FileHash": "other-hash-value", "Step": "1", "Status": "CREATE_COMPLETE"}]

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
                              "AddTags": [],
                              "DefaultRegions": ["eu-west-1", "eu-central-1"]
                             }
        return landingzone_config

    def get_plan_item_create_without_role(self):
        plan_item = {"Action": "Create", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0}
        return plan_item

    def get_plan_item_create_with_role(self):
        plan_item = {"Action": "Create", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0}
        return plan_item

    def get_plan(self):
        plan = [{"Action": "Update", "Name": "MyStack-dev-eu-west-1", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 0},
                {"Action": "Create", "Name": "MyStack-dev-eu-west-1-2", "FileName": "FileName", "Account": "development", "Region": "eu-west-1", "Role": "MyRole", "Capabilities": [], "Parameters": [], "FileHash": "my-hash", "Step": 1},
                {"Action": "Delete", "Name": "MyStack-master-eu-west-1-3", "Account": "master", "Region": "eu-west-1", "Step": 3}]
        return plan

    def get_current_deployments(self):        
        return [self.get_plan_item_create_without_role()]

    def get_mock_objects_describe_stacks(self, mock_session_class, describe_stacks):
        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_client.describe_stacks.return_value = describe_stacks
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object
       
        return (mock_session_object, mock_client, mock_session_class)

    def get_mock_objects_describe_stacks_multiple_calls(self, mock_session_class, describe_stacks_list):
        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_client.describe_stacks.side_effect = describe_stacks_list
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object
       
        return (mock_session_object, mock_client, mock_session_class)

    def get_mock_objects_describe_stacks_stackname_does_not_exist(self, mock_session_class, stack_name):
        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_client.describe_stacks.side_effect = Exception("Stack with id {} does not exist".format(stack_name))
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object

        return (mock_session_object, mock_client, mock_session_class)

    def get_mock_objects_create_stack(self, mock_session_class):
        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_client.create_stack.return_value = {}
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object
       
        return (mock_session_object, mock_client, mock_session_class)

    def get_mock_objects_update_stack(self, mock_session_class):
        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_client.update_stack.return_value = {}
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object
       
        return (mock_session_object, mock_client, mock_session_class)

    def get_mock_objects_delete_stack(self, mock_session_class):
        mock_session_object = mock.Mock()
        mock_client = mock.Mock()
        mock_client.delete_stack.return_value = {}
        mock_session_object.client.return_value = mock_client
        mock_session_class.return_value = mock_session_object
       
        return (mock_session_object, mock_client, mock_session_class)

    def get_test_data_one_account(self):
        accounts = [{"Name": "development", "ProfileName": "my-development", "Environment": "dev", "AccountId": "111111111111"}]
        landingzone_config = {"DefaultRegions": ["eu-west-1"], "Tags": [{"Key": "LandingZoneResource", "Value": "True"}]}

        return (accounts, landingzone_config)


    # See also: https://stackoverflow.com/questions/67502338/how-to-mock-the-boto3-client-session-requests-for-secretsmanager-to-either-retur
    @mock.patch("boto3.session.Session")
    def test_init_cloudformation(self, mock_session_class):

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, self.get_one_landingzone_stack())
        (accounts, landingzone_config) = self.get_test_data_one_account()

        init_cloudformation(accounts, landingzone_config)

        assert accounts[0][('cloudformation', 'eu-west-1')] == mock_client


    @mock.patch("boto3.session.Session")
    def test_describe_deployed_stacks_trace(self, mock_session_class, capsys):

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, self.get_one_landingzone_stack())
        (accounts, landingzone_config) = self.get_test_data_one_account()
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        describe_deployed_stacks(accounts, landingzone_config)

        captured = capsys.readouterr()
        assert "Describe stacks in account development - region eu-west-1" in captured.out

    @mock.patch("boto3.session.Session")
    def test_describe_deployed_stacks_stack(self, mock_session_class, capsys):

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, self.get_one_landingzone_stack())
        (accounts, landingzone_config) = self.get_test_data_one_account()
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        describe_deployed_stacks(accounts, landingzone_config)

        assert accounts[0]["DeployedStacks"]["eu-west-1"] == [self.get_one_stack_in_landingzone_format()]

    @mock.patch("boto3.session.Session")
    def test_describe_deployed_stacks_no_lz_stack_no_tags(self, mock_session_class, capsys):

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, self.get_one_non_landingzone_stack())
        (accounts, landingzone_config) = self.get_test_data_one_account()
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        describe_deployed_stacks(accounts, landingzone_config)

        assert accounts[0]["DeployedStacks"]["eu-west-1"] == []

    @mock.patch("boto3.session.Session")
    def test_describe_deployed_stacks_no_lz_stack_all_tags(self, mock_session_class, capsys):

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, self.get_one_landingzone_stack_two_tags())
        (accounts, landingzone_config) = self.get_test_data_one_account()

        accounts[0][('cloudformation', 'eu-west-1')] = mock_client
        landingzone_config['Tags'] = [{
            "Key": "LandingZoneResource",
            "Value": "True"
        },{
            "Key": "ShoudHaveThisTagToo",
            "Value": "True"
        }]

        describe_deployed_stacks(accounts, landingzone_config)

        assert accounts[0]["DeployedStacks"]["eu-west-1"] == [self.get_one_stack_in_landingzone_format()]

    @mock.patch("boto3.session.Session")
    def test_describe_deployed_stacks_no_lz_stack_not_all_tags(self, mock_session_class, capsys):

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, self.get_one_landingzone_stack())
        (accounts, landingzone_config) = self.get_test_data_one_account()

        accounts[0][('cloudformation', 'eu-west-1')] = mock_client
        landingzone_config['Tags'] = [{
            "Key": "LandingZoneResource",
            "Value": "True"
        },{
            "Key": "ShoudHaveThisTagToo",
            "Value": "True"
        }]

        describe_deployed_stacks(accounts, landingzone_config)

        assert accounts[0]["DeployedStacks"]["eu-west-1"] == []

    @mock.patch("boto3.session.Session")
    def test_describe_deployed_stacks_next_token(self, mock_session_class):

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks_multiple_calls(mock_session_class, self.get_two_landingzone_stacks_with_next_token())
        (accounts, landingzone_config) = self.get_test_data_one_account()
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        describe_deployed_stacks(accounts, landingzone_config)

        assert accounts[0]["DeployedStacks"]["eu-west-1"] == self.get_two_landingzone_stacks_with_next_token_in_landingzone_format()
        mock_client.describe_stacks.assert_called_with(NextToken="MyToken")


    @mock.patch("builtins.open", mock.mock_open(read_data = "CloudformationContent"))
    @mock.patch("boto3.session.Session")
    def test_execute_create_without_role_defaults(self, mock_session_class):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan_item = self.get_plan_item_create_without_role()

        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_create_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_create(accounts, plan_item, landingzone_config)

        mock_client.create_stack.assert_called_with(StackName=stack_name, 
                                                    Tags=[{"Key": "LandingZoneResource","Value": "True"},
                                                          {"Key": "FileHash", "Value": "my-hash"},
                                                          {"Key": "Step", "Value": "0"}],
                                                    TemplateBody="CloudformationContent",
                                                    Capabilities=[],
                                                    Parameters=[])

    @mock.patch("builtins.open", mock.mock_open(read_data = "CloudformationContent"))
    @mock.patch("boto3.session.Session")
    def test_execute_create_with_role_defaults(self, mock_session_class):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan_item = self.get_plan_item_create_with_role()

        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_create_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_create(accounts, plan_item, landingzone_config)

        mock_client.create_stack.assert_called_with(StackName=stack_name, 
                                                    Tags=[{"Key": "LandingZoneResource","Value": "True"},
                                                          {"Key": "FileHash", "Value": "my-hash"},
                                                          {"Key": "Step", "Value": "0"}],
                                                    TemplateBody="CloudformationContent",
                                                    Capabilities=[],
                                                    Parameters=[],
                                                    RoleARN=get_role_arn(find_account(accounts, "development"), plan_item["Role"]))

    @mock.patch("builtins.open", mock.mock_open(read_data = "-={development}=-"))
    @mock.patch("boto3.session.Session")
    def test_execute_create_with_account_name_replacement_and_non_defaults(self, mock_session_class):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan_item = self.get_plan_item_create_with_role()
        plan_item["Parameters"] = ["parameters"]
        plan_item["Capabilities"] = ["capabilities"]

        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_create_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_create(accounts, plan_item, landingzone_config)

        mock_client.create_stack.assert_called_with(StackName=stack_name, 
                                                    Tags=[{"Key": "LandingZoneResource","Value": "True"},
                                                          {"Key": "FileHash", "Value": "my-hash"},
                                                          {"Key": "Step", "Value": "0"}],
                                                    TemplateBody="-=111111111111=-",
                                                    Capabilities=["capabilities"],
                                                    Parameters=["parameters"],
                                                    RoleARN=get_role_arn(find_account(accounts, "development"), plan_item["Role"]))

    @mock.patch("builtins.open", mock.mock_open(read_data = "TestContent"))
    @mock.patch("boto3.session.Session")
    def test_execute_create_with_extra_tags(self, mock_session_class):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan_item = self.get_plan_item_create_with_role()
        landingzone_config["AddTags"] = [{"Key": "ExtraTag", "Value": "Important"}]
        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_create_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_create(accounts, plan_item, landingzone_config)

        mock_client.create_stack.assert_called_with(StackName=stack_name, 
                                                    Tags=[{"Key": "LandingZoneResource","Value": "True"},
                                                          {"Key": "ExtraTag", "Value": "Important"},
                                                          {"Key": "FileHash", "Value": "my-hash"},
                                                          {"Key": "Step", "Value": "0"}],
                                                    TemplateBody="TestContent",
                                                    Capabilities=[],
                                                    Parameters=[],
                                                    RoleARN=get_role_arn(find_account(accounts, "development"), plan_item["Role"]))

    @mock.patch("builtins.open", mock.mock_open(read_data = "CloudformationContent"))
    @mock.patch("boto3.session.Session")
    def test_execute_update_without_role_defaults(self, mock_session_class):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan_item = self.get_plan_item_create_without_role()
        plan_item["Action"] = "Update"

        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_update_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_update(accounts, plan_item, landingzone_config)

        mock_client.update_stack.assert_called_with(StackName=stack_name, 
                                                    Tags=[{"Key": "LandingZoneResource","Value": "True"},
                                                          {"Key": "FileHash", "Value": "my-hash"},
                                                          {"Key": "Step", "Value": "0"}],
                                                    TemplateBody="CloudformationContent",
                                                    Capabilities=[],
                                                    Parameters=[])

    @mock.patch("builtins.open", mock.mock_open(read_data = "CloudformationContent"))
    @mock.patch("boto3.session.Session")
    def test_execute_update_with_role_defaults(self, mock_session_class):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan_item = self.get_plan_item_create_with_role()
        plan_item["Action"] = "Update"

        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_update_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_update(accounts, plan_item, landingzone_config)

        mock_client.update_stack.assert_called_with(StackName=stack_name, 
                                                    Tags=[{"Key": "LandingZoneResource","Value": "True"},
                                                          {"Key": "FileHash", "Value": "my-hash"},
                                                          {"Key": "Step", "Value": "0"}],
                                                    TemplateBody="CloudformationContent",
                                                    Capabilities=[],
                                                    Parameters=[],
                                                    RoleARN=get_role_arn(find_account(accounts, "development"), plan_item["Role"]))

    @mock.patch("builtins.open", mock.mock_open(read_data = "-={development}=-"))
    @mock.patch("boto3.session.Session")
    def test_execute_update_with_account_name_replacement_and_non_defaults(self, mock_session_class):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan_item = self.get_plan_item_create_with_role()
        plan_item["Action"] = "Update"
        plan_item["Parameters"] = ["parameters"]
        plan_item["Capabilities"] = ["capabilities"]

        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_update_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_update(accounts, plan_item, landingzone_config)

        mock_client.update_stack.assert_called_with(StackName=stack_name, 
                                                    Tags=[{"Key": "LandingZoneResource","Value": "True"},
                                                          {"Key": "FileHash", "Value": "my-hash"},
                                                          {"Key": "Step", "Value": "0"}],
                                                    TemplateBody="-=111111111111=-",
                                                    Capabilities=["capabilities"],
                                                    Parameters=["parameters"],
                                                    RoleARN=get_role_arn(find_account(accounts, "development"), plan_item["Role"]))

    @mock.patch("builtins.open", mock.mock_open(read_data = "TestContent"))
    @mock.patch("boto3.session.Session")
    def test_execute_update_with_extra_tags(self, mock_session_class):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan_item = self.get_plan_item_create_with_role()
        plan_item["Action"] = "Update"
        landingzone_config["AddTags"] = [{"Key": "ExtraTag", "Value": "Important"}]
        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_update_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_update(accounts, plan_item, landingzone_config)

        mock_client.update_stack.assert_called_with(StackName=stack_name, 
                                                    Tags=[{"Key": "LandingZoneResource","Value": "True"},
                                                          {"Key": "ExtraTag", "Value": "Important"},
                                                          {"Key": "FileHash", "Value": "my-hash"},
                                                          {"Key": "Step", "Value": "0"}],
                                                    TemplateBody="TestContent",
                                                    Capabilities=[],
                                                    Parameters=[],
                                                    RoleARN=get_role_arn(find_account(accounts, "development"), plan_item["Role"]))

    @mock.patch("boto3.session.Session")
    def test_execute_delete(self, mock_session_class):
        accounts = self.get_two_accounts()
        plan_item = self.get_plan_item_create_without_role()
        plan_item["Action"] = "Delete"

        stack_name = plan_item["Name"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_delete_stack(mock_session_class)
        accounts[0][('cloudformation', 'eu-west-1')] = mock_client

        execute_delete(accounts, plan_item)

        mock_client.delete_stack.assert_called_with(StackName=stack_name)

    @mock.patch("boto3.session.Session")
    def test_check_current_deployments_delete_exception(self, mock_session_class, capsys):
        accounts = self.get_two_accounts()
        current_deployments = self.get_current_deployments()
        landingzone_config = self.get_landingzone_config()

        current_deployments[0]["Action"] = "Delete"

        stack_name = current_deployments[0]["Name"]
        account_name = current_deployments[0]["Account"]
        region = current_deployments[0]["Region"]

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks_stackname_does_not_exist(mock_session_class, stack_name)
        accounts[0][('cloudformation', region)] = mock_client

        check_current_deployments(accounts, current_deployments, landingzone_config)
        captured = capsys.readouterr()
        print(captured)
        assert "Status delete stack {} in account {} in region {}: stack deleted".format(stack_name, account_name, region) in captured.out

    @mock.patch("boto3.session.Session")
    @pytest.mark.parametrize('msg', ["CREATE_COMPLETE", "UPDATE_COMPLETE", "DELETE_COMPLETE"])
    def test_check_current_deployments_status_create_complete(self, mock_session_class, capsys, msg):
        accounts = self.get_two_accounts()
        current_deployments = self.get_current_deployments()
        landingzone_config = self.get_landingzone_config()

        stack_name = current_deployments[0]["Name"]
        account_name = current_deployments[0]["Account"]
        region = current_deployments[0]["Region"]

        landingzone_stack = self.get_one_landingzone_stack()
        landingzone_stack["Stacks"][0]["StackStatus"] = msg

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, landingzone_stack)
        accounts[0][('cloudformation', region)] = mock_client

        check_current_deployments(accounts, current_deployments, landingzone_config)
        captured = capsys.readouterr()
        print(captured)
        assert "Status create stack {} in account {} in region {}: {}".format(stack_name, account_name, region, msg) in captured.out
        assert current_deployments == []

    @mock.patch("boto3.session.Session")
    @pytest.mark.parametrize('msg', ["CREATE_FAILED", "ROLLBACK_COMPLETE", "ROLLBACK_FAILED", "UPDATE_FAILED", "UPDATE_ROLLBACK_COMPLETE", "UPDATE_ROLLBACK_FAILED", "DELETE_FAILED"])
    def test_check_current_deployments_status_create_failed(self, mock_session_class, capsys, msg):
        accounts = self.get_two_accounts()
        current_deployments = self.get_current_deployments()
        landingzone_config = self.get_landingzone_config()
        landingzone_config["AbortWhenStackFails"] = False

        stack_name = current_deployments[0]["Name"]
        account_name = current_deployments[0]["Account"]
        region = current_deployments[0]["Region"]

        landingzone_stack = self.get_one_landingzone_stack()
        landingzone_stack["Stacks"][0]["StackStatus"] = msg

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, landingzone_stack)
        accounts[0][('cloudformation', region)] = mock_client

        check_current_deployments(accounts, current_deployments, landingzone_config)
        captured = capsys.readouterr()
        print(captured)
        assert "Status create stack {} in account {} in region {}: {}".format(stack_name, account_name, region, msg) in captured.out
        assert "continue" in captured.out
    
    @mock.patch("boto3.session.Session")
    @mock.patch("builtins.open", mock.mock_open(read_data = "TestContent"))
    @pytest.mark.parametrize('msg', ["CREATE_COMPLETE"])
    def test_execute_plan_new_step(self, mock_session_class, capsys, msg):
        accounts = self.get_two_accounts()
        landingzone_config = self.get_landingzone_config()
        plan = self.get_plan()

        # First item is step 0, second item is not step 0: we want to go directly to step 1 to enforce message "Step 0 finished, new step: 1"
        plan.remove(plan[0])
        first_step = plan[0]["Step"]
 
        landingzone_stack = self.get_one_landingzone_stack()
        landingzone_stack["Stacks"][0]["StackStatus"] = "CREATE_COMPLETE"

        (mock_session_object, mock_client, mock_session_class) = self.get_mock_objects_describe_stacks(mock_session_class, landingzone_stack)
        accounts[0][('cloudformation', "eu-west-1")] = mock_client
        accounts[1][('cloudformation', "eu-west-1")] = mock_client

        execute_plan(accounts, plan, landingzone_config)
        captured = capsys.readouterr()
        print(captured)
        assert "Step 0 finished, new step: {}".format(first_step) in captured.out
        assert "> Create stack MyStack-dev-eu-west-1-2 in account development in region eu-west-1" in captured.out
        assert "Step {}: 1 changes in 1 accounts are being deployed".format(first_step) in captured.out
