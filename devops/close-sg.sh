# Update a security group rule allowing your
# current IPv4 I.P. to connect on port 22 (SSH)

# variables to identify sec group and sec group rule
SEC_GROUP_ID='sg-0e4369990113dbba3'
SEC_GROUP_RULE_ID='sgr-08f65e18d82779601'

# gets current date and prepares description for sec group rule
CURRENT_DATE=$(date +'%Y-%m-%d')
SEC_GROUP_RULE_DESCRIPTION="dynamic ip updated - ${CURRENT_DATE}"

# Change rule to a 'private' IP
NEW_IPV4_CIDR="192.168.1.2/32"

# updates I.P. and description in the sec group rule
aws ec2 modify-security-group-rules --group-id ${SEC_GROUP_ID} --security-group-rules SecurityGroupRuleId=${SEC_GROUP_RULE_ID},SecurityGroupRule="{CidrIpv4=${NEW_IPV4_CIDR}, IpProtocol=tcp,FromPort=22,ToPort=22,Description=${SEC_GROUP_RULE_DESCRIPTION}}"

# shows the sec group rule updated
aws ec2 describe-security-group-rules --filter Name="security-group-rule-id",Values="${SEC_GROUP_RULE_ID}"
