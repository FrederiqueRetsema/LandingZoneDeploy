import os
import time
import glob
import argparse

import boto3
import yaml
import hashlib

CONFIG_DIR = "./config/"

ACCOUNTS_FILENAME = CONFIG_DIR + "accounts.yaml"
GROUPS_FILENAME = CONFIG_DIR + "groups.yaml"
LANDINGZONE_CONFIG_FILENAME = CONFIG_DIR + "landingzone-config.yaml"

CLOUDFORMATION_CONFIG_FILES = "./templates/**/*.config.yaml"

class InvalidConfigFileException(Exception):
    pass

class InvalidParameterException(Exception):
    pass


class DependencyException(Exception):
    pass

def trace(string):
    print(time.strftime("%H:%M:%S"), string)


def read_accounts_from_file(accounts_filename):
    with open(accounts_filename, "r") as file:
        accounts = yaml.safe_load(file)

    return accounts["Accounts"]


def read_groups_from_file(groups_filename):
    with open(groups_filename, "r") as file:
        groups = yaml.safe_load(file)

    return groups["Groups"]


def read_landingzone_config_from_file(landingzone_config_filename):
    with open(landingzone_config_filename, "r") as file:
        landingzone_config = yaml.safe_load(file)

    return landingzone_config["LandingZoneConfig"]


def enrich_accounts(accounts):
    if accounts == []:
        error_msg = "Missing accounts in configuration file"
        trace(error_msg)
        raise InvalidConfigFileException(error_msg)

    for account in accounts:
        if "ProfileName" not in account:
            account["ProfileName"] = account["Name"]


def unfold_list_item(groups, listitem):
    list_items = []
    for group in groups:
        if listitem == group["Name"]:
            list_items = group["List"]

    if list_items == []:
        list_items = [listitem]

    return list_items


def unfold_group_list(groups, list_to_unfold):

    while True:
        old_list = list_to_unfold

        new_list_items = []
        for list_item in list_to_unfold:
            new_list_items += unfold_list_item(groups, list_item)

        list_to_unfold = new_list_items
        if old_list == list_to_unfold:
            break

    return list_to_unfold


def enrich_groups(groups):
    if groups == []:
        error_msg = "Missing groups in configuration file"
        trace(error_msg)
        raise InvalidConfigFileException(error_msg)

    for group in groups:
        group["List"] = unfold_group_list(groups, group["List"])

        if "Except" in group:
            group["Except"] = unfold_group_list(groups, group["Except"])

            for except_item in group["Except"]:
                if except_item in group["List"]:
                    group["List"].remove(except_item)

            del group["Except"]


def enrich_landingzone_config(landingzone_config):
    if not "MaxConcurrentAccounts" in landingzone_config:
        error_msg = "Parameter MaxConcurrentAccounts missing in configuration file"
        trace(error_msg)
        raise InvalidConfigFileException(error_msg)
    if not "MaxConcurrentStacksPerAccount" in landingzone_config:
        error_msg = "Parameter MaxConcurrentStacksPerAccount missing in configuration file"
        trace(error_msg)
        raise InvalidConfigFileException(error_msg)
    if not "WaitTimeInSec" in landingzone_config:
        error_msg = "Parameter WaitTimeInSec missing in configuration file"
        trace(error_msg)
        raise InvalidConfigFileException(error_msg)
    if not "GroupNameAllAccounts" in landingzone_config:
        error_msg = "Parameter GroupNameAllAccounts missing in configuration file"
        trace(error_msg)
        raise InvalidConfigFileException(error_msg)
    if not "GroupNameAllRegions" in landingzone_config:
        error_msg = "Parameter GroupNameAllRegions missing in configuration file"
        trace(error_msg)
        raise InvalidConfigFileException(error_msg)
    if not "Tags" in landingzone_config:
        error_msg = "Parameter Tags missing in configuration file"
        trace(error_msg)
        raise InvalidConfigFileException(error_msg)

    if not "DryRun" in landingzone_config:
        landingzone_config["DryRun"] = True
    if not "AbortWhenStackFails" in landingzone_config:
        landingzone_config["AbortWhenStackFails"] = True
    if not "LogLevel" in landingzone_config:
        landingzone_config["LogLevel"] = "NoExtraLogging"
    if not "AddTags" in landingzone_config:
        landingzone_config["AddTags"] = []    


def find_account(accounts, account_name):
    for account in accounts:
        if account["Name"] == account_name:
            return account
        if account["ProfileName"] == account_name:
            return account

    return None


def find_account_names_based_on_environment(accounts, environment_name):
    specific_accounts = []
    for account in accounts:
        if account["Environment"] == environment_name:
            specific_accounts += [account["Name"]]

    if specific_accounts != []:
        return specific_accounts
    else:
        return None


def find_account_names_based_on_group_name(groups, group_name):
    groups = unfold_group_list(groups, [group_name])
    if groups != [group_name]:
        return groups
    else:
        return None


def find_account_names_based_on_account_name(accounts, account_name):
    account = find_account(accounts, account_name)
    if account is not None and account['Name'] == account_name:
        return [account_name]

    return None


def find_account_names_based_on_profile_name(accounts, profile_name):
    account = find_account(accounts, profile_name)
    if account is not None and account['ProfileName'] == profile_name:
        return [account['Name']]

    return None


def find_region_based_on_region_name(regions, region_name):
    if region_name in regions:
        return [region_name]
    return None


def find_value_in_tag_list(tag_list, keyname):
    for tag in tag_list:
        if tag["Key"] == keyname:
            return tag["Value"]

    return None


def find_stack_in_cloudformation_templates(cloudformation_templates, stack_name):
    for template in cloudformation_templates:
        if template["Name"] == stack_name:
            return template
    return None


def find_stack_in_account(account, stack_name):
    for region in account["CloudformationTemplates"]:
        for stack in account["CloudformationTemplates"][region]:
            if stack["Name"] == stack_name:
                return stack
    return None


def find_stack_in_region_in_account(account, region, stack_name):
    if region in account["CloudformationTemplates"]:
        for template in account["CloudformationTemplates"][region]:
            if template["Name"] == stack_name:
                return template
    return None


def find_stack_in_all_accounts(accounts, stack_name):
    for account in accounts:
        for region in account["CloudformationTemplates"]:
            for template in account["CloudformationTemplates"][region]:
                if template["Name"] == stack_name:
                    return template
    return None


def find_dependent_stack(templates, account, accounts, stack_name, depends_on_stack_name):
    dependent_template = find_stack_in_cloudformation_templates(templates, depends_on_stack_name)
    if dependent_template is None:
        dependent_template = find_stack_in_account(account, depends_on_stack_name)
        if dependent_template is None:
            dependent_template = find_stack_in_all_accounts(accounts, depends_on_stack_name)
            if dependent_template is None:
                error_msg = "Dependency incorrect: dependency in stack {} refers to non existing stack name {}".format(stack_name, depends_on_stack_name)
                trace(error_msg)
                raise DependencyException(error_msg)
    return dependent_template


def find_stack_in_region_in_accounts_list(accounts, account_name, region, stack_name):
    account = find_account(accounts, account_name)
    if account is not None:
        dependent_template = find_stack_in_region_in_account(account, region, stack_name)
    else:
        dependent_template = None

    return dependent_template


def get_commandline_arguments(accounts, groups, landingzone_config, args):
    parser = argparse.ArgumentParser(
        description="Deploys resources to an AWS Landing Zone",
        epilog="""
       When -e, -g, -a, -p are used in combination, the landingzone will only
       deploy to (all of) the accounts that are specified. Example:
       landingzone-deploy.py --no-dry-run -e dev -e sandbox -p audit -r eu-west-1 -r us-east-1
       will deploy to all accounts that are part of the dev AND sandbox environments AND to the
       account with the audit profile but ONLY in regions eu-west-1 AND us-east-1""")
    parser.add_argument(
        "--no-dry-run",
        help="Change resources in the landing zone (default: dry-run)",
        action="store_true")
    parser.add_argument(
        "--no-abort-when-stack-fails",
        help="Continue when there is an error in a stack that is changed (default: stop immediately)",
        action="store_true",
    )
    parser.add_argument(
        "-e", "--environment",
        nargs="+",
        help="environment name of accounts to deploy into"
    )
    parser.add_argument(
        "-g", "--group",
        nargs="+",
        help="group name of accounts to deploy into"
    )
    parser.add_argument(
        "-p", "--profile",
        nargs="+",
        help="profile name of accounts to deploy into"
    )
    parser.add_argument(
        "-a", "--account",
        nargs="+",
        help="account name of accounts to deploy into"
    )
    parser.add_argument(
        "-r", "--region",
        nargs="+",
        help="region name of regions to deploy into"
    )
    arguments = parser.parse_args(args)

    specified_accounts_only = []
    specified_regions_only = []

    landingzone_config["DryRun"] = not arguments.no_dry_run
    landingzone_config["AbortWhenStackFails"] = not arguments.no_abort_when_stack_fails

    if arguments.environment is not None:
        for environment in arguments.environment:
            environment_accounts = find_account_names_based_on_environment(accounts, environment)
            if environment_accounts is not None:
                specified_accounts_only += environment_accounts
            else:
                error_msg = "Environment " + environment + " not configured"
                trace(error_msg)
                raise InvalidParameterException(error_msg)

    if arguments.group is not None:
        for group in arguments.group:
            group_accounts = find_account_names_based_on_group_name(groups, group)
            if group_accounts is not None:
                specified_accounts_only += group_accounts
            else:
                error_msg = "Group " + group + " not configured"
                trace(error_msg)
                raise InvalidParameterException(error_msg)

    if arguments.account is not None:
        for account in arguments.account:
            account_accounts = find_account_names_based_on_account_name(accounts, account)
            if account_accounts is not None:
                specified_accounts_only += account_accounts
            else:
                error_msg = "Account " + account + " not configured"
                trace(error_msg)
                raise InvalidParameterException(error_msg)

    if arguments.profile is not None:
        for profile in arguments.profile:
            profile_accounts = find_account_names_based_on_profile_name(accounts, profile)
            if profile_accounts is not None:
                specified_accounts_only += profile_accounts
            else:
                error_msg = "Profile " + profile + " not configured"
                trace(error_msg)
                raise InvalidParameterException(error_msg)

    if arguments.region is not None:
        for region in arguments.region:
            regions = find_region_based_on_region_name(landingzone_config["DefaultRegions"], region)
            if regions is not None:
                specified_regions_only += [region]
            else:
                error_msg = "Region " + region + " not configured"
                trace(error_msg)
                raise InvalidParameterException(error_msg)

    landingzone_config["SpecifiedAccountsOnly"] = specified_accounts_only
    landingzone_config["SpecifiedRegionsOnly"] = specified_regions_only


def init_cloudformation(accounts, landingzone_config):
    for account in accounts:
        for region in landingzone_config["DefaultRegions"]:
            session = boto3.session.Session(region_name=region, profile_name=account["ProfileName"])
            cloudformation = session.client("cloudformation")

            account["cloudformation", region] = cloudformation


def describe_deployed_stacks(accounts, landingzone_config):
    for account in accounts:
        landingzone_stacks = {}
        for region in landingzone_config["DefaultRegions"]:
            trace("Describe stacks in account {} - region {}".format(account["Name"], region))

            current_stacks = account["cloudformation", region].describe_stacks()
            landingzone_stacks[region] = []
            while True:
                for stack in current_stacks["Stacks"]:
                    is_landingzone_stack = True
                    for landingzone_tag in landingzone_config["Tags"]:
                        if find_value_in_tag_list(stack["Tags"], landingzone_tag["Key"]) != landingzone_tag["Value"]:
                            is_landingzone_stack = False
                    if is_landingzone_stack:
                        landingzone_stacks[region] += [
                            {
                                "Name": stack["StackName"],
                                "FileHash": find_value_in_tag_list(stack["Tags"], "FileHash"),
                                "Step": find_value_in_tag_list(stack["Tags"], "Step"),
                                "Status": stack["StackStatus"],
                            }
                        ]

                if "NextToken" in current_stacks:
                    current_stacks = account["cloudformation", region].describe_stacks(
                        NextToken=current_stacks["NextToken"]
                    )
                else:
                    break

        account["DeployedStacks"] = landingzone_stacks


def add_stack_to_accounts(accounts, file_name, stack_name, file_hash, role, capabilities, parameters, depends_on, to_accounts, to_region):
    for account_name in to_accounts:
        account = find_account(accounts, account_name)
        for region in to_region:
            account["CloudformationTemplates"][region] += [
                {
                    "Name": stack_name,
                    "FileName": file_name,
                    "FileHash": file_hash,
                    "Step": None,
                    "Role": role,
                    "Capabilities": capabilities,
                    "Parameters": parameters,
                    "DependsOn": depends_on
                }
            ]

    return


def determine_cloudformation_file_name_from_config_filename(config_filename):
    pos_forward_slash = config_filename.rfind("/")
    pos_backslash = config_filename.rfind("\\")
    pos = pos_forward_slash if pos_forward_slash > pos_backslash else pos_backslash

    dirname = config_filename[0:pos + 1]
    filename = config_filename[pos + 1:]

    pos = filename.find(".")
    filename_without_extension = filename[0:pos]
    return {"dir": dirname, "filename_without_extension": filename_without_extension}


def get_file_hash(filename):
    file_hash = "0"
    try:
        with open(filename, "rb") as file:
            file_hash = hashlib.md5(file.read()).hexdigest()
    except Exception as e:
        print(e)

    return file_hash


def init_cloudformation_templates(accounts, landingzone_config):
    for account in accounts:
        account["CloudformationTemplates"] = {}
        for region in landingzone_config["DefaultRegions"]:
            account["CloudformationTemplates"][region] = []


def check_cloudformation_config(accounts, regions, to_accounts, to_regions):
    for account_name in to_accounts:
        account = find_account_names_based_on_account_name(accounts, account_name)
        if account == None:
            error_msg = "Account {} does not exist".format(account_name)
            trace(error_msg)
            raise InvalidConfigFileException(error_msg)

    for region_name in to_regions:
        region = find_region_based_on_region_name(regions, region_name)
        if region == None:
            error_msg = "Region {} does not exist".format(region_name)
            trace(error_msg)
            raise InvalidConfigFileException(error_msg)


def parse_cloudformation_config(landingzone_config, groups, file_name, config):

    cloudformation_stackname_and_dir = determine_cloudformation_file_name_from_config_filename(file_name)
    cloudformation_filename = \
        cloudformation_stackname_and_dir["dir"] \
        + cloudformation_stackname_and_dir["filename_without_extension"] \
        + ".cfn.yaml"
    
    stack_name = (config["StackName"] if "StackName" in config else cloudformation_stackname_and_dir["filename_without_extension"])

    role = config["Role"] if "Role" in config else ""
    depends_on = config["DependsOn"] if "DependsOn" in config else []

    capabilities = config["Capabilities"] if "Capabilities" in config else []
    parameters = config["Parameters"] if "Parameters" in config else []

    if "DeployTo" in config:
        deploy_to = config["DeployTo"]

        to_accounts = []
        if "Accounts" in deploy_to:
            for account_name in deploy_to["Accounts"]:
                to_accounts += unfold_group_list(groups, [account_name])
        else:
            to_accounts = landingzone_config["DefaultAccounts"]

        to_regions = []
        if "Regions" in deploy_to:
            for region_name in deploy_to["Regions"]:
                to_regions += unfold_group_list(groups, [region_name])
        else:
            to_regions = landingzone_config["DefaultRegions"]
    else:
        to_accounts = landingzone_config["DefaultAccounts"]
        to_regions = landingzone_config["DefaultRegions"]

    file_hash = get_file_hash(cloudformation_filename)

    return (cloudformation_filename, stack_name, file_hash, role, capabilities, parameters, depends_on, to_accounts, to_regions)
    

def get_cloudformation_templates(accounts, groups, landingzone_config, config_files_pattern):

    for file_name in glob.iglob(config_files_pattern, recursive=True):
        try:
            trace("Found: " + file_name)
            with open(file_name, "r") as file:
                cloudformation_config_file = yaml.safe_load(file)

            config = cloudformation_config_file["TemplateConfig"]

            (cloudformation_filename, stack_name, file_hash, role, capabilities, parameters, depends_on, to_accounts, to_regions) = parse_cloudformation_config(landingzone_config, groups, file_name, config)
            check_cloudformation_config(accounts, landingzone_config["DefaultRegions"], to_accounts, to_regions)

            add_stack_to_accounts(
                accounts,
                cloudformation_filename,
                stack_name,
                file_hash,
                role,
                capabilities,
                parameters,
                depends_on,
                to_accounts,
                to_regions
            )
        except Exception as e:
            print(e)
            raise Exception(e)


def determine_dependent_on(accounts):
    for account in accounts:
        for region in account["CloudformationTemplates"]:
            templates = account["CloudformationTemplates"][region]
            for template in templates:
                stack_name = template["Name"]
                for depends_on in template["DependsOn"]:
                    dependent_template = find_dependent_stack(
                        templates, account, accounts, stack_name, depends_on
                    )
                    if "DependentOn" not in dependent_template:
                        dependent_template["DependentOn"] = [(account["Name"], region, stack_name)]
                    else:
                        dependent_template["DependentOn"] += [(account["Name"], region, stack_name)]


def set_deployment_order(accounts, step, landingzone_config):
    order_set = False
    highest_step = step
    for account in accounts:
        for region in account["CloudformationTemplates"]:
            templates = account["CloudformationTemplates"][region]
            for template in templates:
                stack_name = template["Name"]
                if (template["DependsOn"] == []) and (template["Step"] == step or template["Step"] is None):
                    order_set = True
                    template["Step"] = step
                    if "DependentOn" in template:
                        for dependent_on in template["DependentOn"]:
                            dependent_on_account_name, dependent_on_region, dependent_on_stackname = dependent_on
                            dependent_stack = find_stack_in_region_in_accounts_list(
                                accounts, dependent_on_account_name, dependent_on_region, dependent_on_stackname
                            )
                            dependent_stack["Step"] = step + 1
                            highest_step = step + 1

                            # In multi-region deployments a stack where both regions are dependent on can be deployed
                            # in 1 region (f.e. IAM roles). In this case the DependsOn will not be present (anymore)
                            #
                            # Work around:
                            new_depends_on = []
                            for depend_on_stack_name in dependent_stack["DependsOn"]:
                                if depend_on_stack_name != stack_name:
                                    new_depends_on += [depend_on_stack_name]
                            if dependent_stack["DependsOn"] == []:
                                del dependent_stack["DependsOn"]
                            dependent_stack["DependsOn"] = new_depends_on

                        del template["DependentOn"]

    if order_set:
        set_deployment_order(accounts, step + 1, landingzone_config)
    else:
        landingzone_config["HighestStep"] = highest_step


def determine_deployment_order(accounts, landingzone_config):
    determine_dependent_on(accounts)
    set_deployment_order(accounts, 0, landingzone_config)


def plan_create_stack(account, region, stack_name, file_name, role, capabilities, parameters, file_hash, step):
    return [
        {
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
        }
    ]


def plan_update_stack(account, region, stack_name, file_name, role, capabilities, parameters, file_hash, step):
    return [
        {
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
        }
    ]


def plan_delete_stack(account, region, stack_name, step):
    return [{"Action": "Delete", "Name": stack_name, "Account": account["Name"], "Region": region, "Step": step}]


def plan_change_landingzone(accounts, landingzone_config):
    change_list = []
    for step in range(0, landingzone_config["HighestStep"] + 1):
        for account in accounts:
            for region in account["CloudformationTemplates"]:
                deployed_stacks = account["DeployedStacks"][region]
                cloudformation_templates = account["CloudformationTemplates"][region]

                for cloudformation_template in cloudformation_templates:
                    stack_name = cloudformation_template["Name"]
                    file_name = cloudformation_template["FileName"]
                    role = cloudformation_template["Role"]
                    capabilities = cloudformation_template["Capabilities"]
                    parameters = cloudformation_template["Parameters"]
                    file_hash = cloudformation_template["FileHash"]

                    deployed_stack = find_stack_in_cloudformation_templates(deployed_stacks, stack_name)

                    if deployed_stack == None and cloudformation_template["Step"] == step:
                        change_list += plan_create_stack(
                            account, region, stack_name, file_name, role, capabilities, parameters, file_hash, step
                        )

                for deployed_stack in deployed_stacks:
                    stack_name = deployed_stack["Name"]
                    cloudformation_template = find_stack_in_cloudformation_templates(
                        cloudformation_templates, stack_name
                    )

                    if cloudformation_template == None:
                        if "Step" in deployed_stack and deployed_stack["Step"] != None:
                            deployed_stack_step = deployed_stack["Step"]
                            delete_step = landingzone_config["HighestStep"] - int(deployed_stack_step)
                        else:
                            delete_step = landingzone_config["HighestStep"]
                        if step == delete_step:
                            change_list += plan_delete_stack(account, region, stack_name, delete_step)
                    else:
                        stack_name = cloudformation_template["Name"]
                        file_name = cloudformation_template["FileName"]
                        role = cloudformation_template["Role"]
                        capabilities = cloudformation_template["Capabilities"]
                        parameters = cloudformation_template["Parameters"]
                        file_hash = cloudformation_template["FileHash"]

                        if file_hash != deployed_stack["FileHash"] and cloudformation_template["Step"] == step:
                            change_list += plan_update_stack(
                                account, region, stack_name, file_name, role, capabilities, parameters, file_hash, step
                            )

    return change_list


def limit_number_of_accounts(plan, landingzone_config):
    if landingzone_config["SpecifiedAccountsOnly"] != []:
        for plan_item in plan.copy():
            if plan_item["Account"] not in landingzone_config["SpecifiedAccountsOnly"]:
                plan.remove(plan_item)

    if landingzone_config["SpecifiedRegionsOnly"] != []:
        for plan_item in plan.copy():
            if plan_item["Region"] not in landingzone_config["SpecifiedRegionsOnly"]:
                plan.remove(plan_item)

    return plan


def print_plan(plan):
    if len(plan) > 0:
        for plan_item in plan:
            step = plan_item["Step"]
            action = plan_item["Action"]
            name = plan_item["Name"]
            account = plan_item["Account"]
            region = plan_item["Region"]

            trace("DryRun: Step {} - {} - {} in account {} in region {} ".format(step, action, name, account, region))
    else:
        trace("No changes")


def determine_current_step(current_deployments, plan):
    if len(current_deployments) > 0:
        step = current_deployments[0]["Step"]
    else:
        if len(plan) > 0:
            step = plan[0]["Step"]
        else:
            step = 0

    return step


#FRA 
def replace_account_names_in_template_body(accounts, original_text):
    new_text = original_text
    for account in accounts:
        new_text = new_text.replace("{" + account["Name"] + "}", account["AccountId"])
        new_text = new_text.replace("{" + account["ProfileName"] + "}", account["AccountId"])

    return new_text


def get_template_body(file_name):
    content = ""
    try:
        with open(file_name, "r") as file:
            content = file.read()
    except Exception as e:
        trace(str(e))

    return content


def get_role_arn(account, role_name):
    return "arn:aws:iam::" + account["AccountId"] + ":role/" + role_name


def execute_create(accounts, plan_item, landingzone_config):
    account = find_account(accounts, plan_item["Account"])
    region = plan_item["Region"]
    file_name = plan_item["FileName"]

    template_text = get_template_body(file_name)
    template_body = replace_account_names_in_template_body(accounts, template_text)

    capabilities = plan_item["Capabilities"]
    parameters = plan_item["Parameters"]
    file_hash = plan_item["FileHash"]
    step = plan_item["Step"]
    role_name = plan_item["Role"]

    role_arn = get_role_arn(account, role_name)

    file_hashAndStepTag = [{"Key": "FileHash", "Value": file_hash}, {"Key": "Step", "Value": str(step)}]

    cloudformation = account["cloudformation", region]

    if role_name != "":
        cloudformation.create_stack(
            StackName=plan_item["Name"],
            Tags=landingzone_config["Tags"] + landingzone_config["AddTags"] + file_hashAndStepTag,
            TemplateBody=template_body,
            Capabilities=capabilities,
            Parameters=parameters,
            RoleARN=role_arn
        )
    else:
        cloudformation.create_stack(
            StackName=plan_item["Name"],
            Tags=landingzone_config["Tags"] + landingzone_config["AddTags"] + file_hashAndStepTag,
            TemplateBody=template_body,
            Capabilities=capabilities,
            Parameters=parameters
        )


def execute_update(accounts, plan_item, landingzone_config):
    account = find_account(accounts, plan_item["Account"])
    region = plan_item["Region"]
    file_name = plan_item["FileName"]

    template_text = get_template_body(file_name)
    template_body = replace_account_names_in_template_body(accounts, template_text)

    capabilities = plan_item["Capabilities"]
    parameters = plan_item["Parameters"]
    file_hash = plan_item["FileHash"]
    step = plan_item["Step"]
    role_name = plan_item["Role"]

    role_arn = get_role_arn(account, role_name)

    file_hashAndStepTag = [{"Key": "FileHash", "Value": file_hash}, {"Key": "Step", "Value": str(step)}]

    cloudformation = account["cloudformation", region]
    if role_name != "":
        cloudformation.update_stack(
            StackName=plan_item["Name"],
            Tags=landingzone_config["Tags"] + landingzone_config["AddTags"] + file_hashAndStepTag,
            TemplateBody=template_body,
            Capabilities=capabilities,
            Parameters=parameters,
            RoleARN=role_arn
        )
    else:
        cloudformation.update_stack(
            StackName=plan_item["Name"],
            Tags=landingzone_config["Tags"] + landingzone_config["AddTags"] + file_hashAndStepTag,
            TemplateBody=template_body,
            Capabilities=capabilities,
            Parameters=parameters
        )


def execute_delete(accounts, plan_item):
    account = find_account(accounts, plan_item["Account"])
    region = plan_item["Region"]

    cloudformation = account["cloudformation", region]
    cloudformation.delete_stack(StackName=plan_item["Name"])


def execute_plan_item(accounts, plan_item, landingzone_config):
    stack_name = plan_item["Name"]
    account_name = plan_item["Account"]
    region = plan_item["Region"]
    if plan_item["Action"] == "Create":
        trace("> Create stack " + stack_name + " in account " + account_name + " in region " + region)
        execute_create(accounts, plan_item, landingzone_config)
    if plan_item["Action"] == "Update":
        trace("> Update stack " + stack_name + " in account " + account_name + " in region " + region)
        execute_update(accounts, plan_item, landingzone_config)
    if plan_item["Action"] == "Delete":
        trace("> Delete stack " + stack_name + " in account " + account_name + " in region " + region)
        execute_delete(accounts, plan_item)


def check_current_deployments(accounts, current_deployments, landingzone_config):
    for deployment in current_deployments.copy():
        account_name = deployment["Account"]
        account = find_account(accounts, account_name)
        region = deployment["Region"]
        action = deployment["Action"].lower()
        stack_name = deployment["Name"]

        cloudformation = account["cloudformation", region]

        stack_info = []
        try:
            stack_info = cloudformation.describe_stacks(StackName=stack_name)
        except Exception as e:
            if "Stack with id " + stack_name + " does not exist" in str(e) and deployment["Action"] == "Delete":
                trace("Status {} stack {} in account {} in region {}: stack deleted".format(action, stack_name, account_name, region))
                current_deployments.remove(deployment)
                continue
            else:
                print(e)
                Exception(e)

        if stack_info["Stacks"] != []:
            status = stack_info["Stacks"][0]["StackStatus"]
            trace("Status {} stack {} in account {} in region {}: {}".format(action, stack_name, account_name, region, status))

            if status in ["CREATE_COMPLETE", "UPDATE_COMPLETE", "DELETE_COMPLETE"]:
                current_deployments.remove(deployment)

            if status in [
                "CREATE_FAILED",
                "ROLLBACK_COMPLETE",
                "ROLLBACK_FAILED",
                "UPDATE_FAILED",
                "UPDATE_ROLLBACK_COMPLETE",
                "UPDATE_ROLLBACK_FAILED",
                "DELETE_FAILED",
            ]:
                error_msg = "Stack " + stack_name + " failed: " + status
                if landingzone_config["AbortWhenStackFails"]:
                    trace(error_msg)
                    os._exit(1)
                else:
                    trace(error_msg + ", continue")
                    current_deployments.remove(deployment)


def determine_concurrent_accounts(current_deployments):
    different_accounts = []
    for deployment in current_deployments:
        if deployment["Account"] not in different_accounts:
            different_accounts += [deployment["Account"]]

    return different_accounts


def determine_concurrent_stacks_per_account(current_deployments):
    different_stacks_per_accounts = {}
    for deployment in current_deployments:
        if not deployment["Account"] in different_stacks_per_accounts:
            different_stacks_per_accounts[deployment["Account"]] = 1
        else:
            different_stacks_per_accounts[deployment["Account"]] += 1

    return different_stacks_per_accounts


def wait_for_now(wait_time, current_deployments, plan):
    current_accounts = determine_concurrent_accounts(current_deployments)
    step = determine_current_step(current_deployments, plan)

    msg = "Step {}: {} changes in {} accounts are being deployed. ".format(step, len(current_deployments), len(current_accounts))
    steplist = {}
    for plan_item in plan:
        if plan_item["Step"] not in steplist:
            steplist[plan_item["Step"]] = 1
        else:
            steplist[plan_item["Step"]] += 1
    for step in steplist:
        msg += "Step {}: {} changes waiting. ".format(step, steplist[step])
    trace(msg)
    time.sleep(wait_time)


def execute_plan(accounts, plan, landingzone_config):
    max_concurrent_tacks_per_account = landingzone_config["MaxConcurrentStacksPerAccount"]
    max_concurrent_accounts = landingzone_config["MaxConcurrentAccounts"]

    current_deployments = []
    current_item = 0
    current_step = 0
    changed = False

    while True:
        if plan == [] and current_deployments == []:
            break

        old_step = current_step
        current_step = determine_current_step(current_deployments, plan)
        if old_step != current_step:
            trace("Step {} finished, new step: {}".format(old_step, current_step))

        concurrent_accounts = determine_concurrent_accounts(current_deployments)
        no_concurrent_accounts = len(concurrent_accounts)

        concurrent_stacks_per_account = determine_concurrent_stacks_per_account(current_deployments)

        if plan != []:
            current_item_account = plan[current_item]["Account"]
            if current_item_account not in concurrent_stacks_per_account:
                concurrent_items_current_account = 0
            else:
                concurrent_items_current_account = concurrent_stacks_per_account[current_item_account]

            if plan[current_item]["Step"] == current_step:
                if (
                    no_concurrent_accounts < max_concurrent_accounts
                    or (
                        no_concurrent_accounts == max_concurrent_accounts
                        and current_item_account in concurrent_accounts
                    )
                ) and (concurrent_items_current_account < max_concurrent_tacks_per_account):
                    current_deployments += [plan[current_item]]
                    execute_plan_item(accounts, plan[current_item], landingzone_config)
                    plan.remove(plan[current_item])
                    current_item = current_item - 1
                    changed = True

        if current_item < len(plan) - 1:
            current_item = current_item + 1
        else:
            if not changed:
                wait_for_now(landingzone_config["WaitTimeInSec"], current_deployments, plan)
                check_current_deployments(accounts, current_deployments, landingzone_config)
            current_item = 0
            changed = False


def print_all_stacks(accounts):
    for account in accounts:
        for region in account["DeployedStacks"]:
            for stack in account["DeployedStacks"][region]:
                stack_name = stack["Name"]
                stack_status = stack["Status"]

                print(stack_name, "in account", account["Name"], "in region", region, "has status", stack_status)


def print_stacks_with_errors(accounts):
    for account in accounts:
        for region in account["DeployedStacks"]:
            for stack in account["DeployedStacks"][region]:
                stack_name = stack["Name"]
                stack_status = stack["Status"]

                if stack_status in [
                    "CREATE_FAILED",
                    "ROLLBACK_COMPLETE",
                    "ROLLBACK_FAILED",
                    "UPDATE_FAILED",
                    "UPDATE_ROLLBACK_COMPLETE",
                    "UPDATE_ROLLBACK_FAILED",
                    "DELETE_FAILED",
                ]: trace("Warning: {} in account {} in region {} has status {}".format(stack_name, account["Name"], region, stack_status))


# Main

def main(args=None) -> argparse.Namespace:
    accounts = read_accounts_from_file(ACCOUNTS_FILENAME)
    enrich_accounts(accounts)

    groups = read_groups_from_file(GROUPS_FILENAME)
    enrich_groups(groups)

    landingzone_config = read_landingzone_config_from_file(LANDINGZONE_CONFIG_FILENAME)
    enrich_landingzone_config(landingzone_config)

    landingzone_config["DefaultAccounts"] = unfold_group_list(groups, [landingzone_config["GroupNameAllAccounts"]])
    landingzone_config["DefaultRegions"] = unfold_group_list(groups, [landingzone_config["GroupNameAllRegions"]])

    get_commandline_arguments(accounts, groups, landingzone_config, args)

    if landingzone_config["LogLevel"] == "Debug":
        print("Accounts:")
        print(accounts)
        print()
        print("Groups:")
        print(groups)
        print()
        print("Landingzone config after commandline parameters:")
        print(landingzone_config)

    init_cloudformation(accounts, landingzone_config)

    describe_deployed_stacks(accounts, landingzone_config)
    init_cloudformation_templates(accounts, landingzone_config)
    get_cloudformation_templates(accounts, groups, landingzone_config, CLOUDFORMATION_CONFIG_FILES)

    determine_deployment_order(accounts, landingzone_config)

    plan = plan_change_landingzone(accounts, landingzone_config)
    plan = limit_number_of_accounts(plan, landingzone_config)

    if landingzone_config["LogLevel"] == "Debug":
        print_all_stacks(accounts)

    if landingzone_config["LogLevel"] in ["Debug", "Info"]:
        print_stacks_with_errors(accounts)

    if plan == []:
        trace("No changes needed")
        os._exit(0)

    if landingzone_config["DryRun"]:
        print_plan(plan)
    else:
        execute_plan(accounts, plan, landingzone_config)


if __name__ == "__main__":
    main()