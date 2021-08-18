import boto3

client = boto3.client("ec2")


def get_ecs_instance_ip_address() -> str:
    response = client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": ["telemetry"]},
            {"Name": "instance-state-name", "Values": ["running"]},
        ]
    )

    return response["Reservations"][0]["Instances"][0]["PrivateIpAddress"]
