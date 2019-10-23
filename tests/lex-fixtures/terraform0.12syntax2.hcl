list_of_lists = [["a"], ["b"], [], [0], [bar ? true : false], [length(bar)]]
foo = tok1 ? tok2 ? "tok3" : "tok4" || "tok5" ? "tok6" : "tok7" : "tok8"
foo = "bar" ? "foo" : "baz"
baz = ! foo
foo = bar ? true : false
bar = foo ? true : baz ? true : false ? true : false
count = var.create_vpc && local.max_subnet_length > 0 ? local.nat_gateway_count : 0
count = var.create_vpc && length(var.secondary_cidr_blocks) > 0 ? length(var.secondary_cidr_blocks) : 0
count = var.create_vpc && var.create_database_subnet_route_table && length(var.database_subnets) > 0 ? 1 : 0
count = var.create_vpc  && var.create_database_subnet_route_table  && length(var.database_subnets) > 0  && var.create_database_internet_gateway_route  && false == var.create_database_nat_gateway_route ? 1 : 0
count = var.create_vpc && length(var.public_subnets) > 0 && (false == var.one_nat_gateway_per_az || length(var.public_subnets) >= length(var.azs)) ? length(var.public_subnets) : 0

route_table_id = aws_route_table.private.*.id[count.index]
cidr_block = concat(var.public_subnets, [
  ""])[count.index]
default_network_acl_id = concat(aws_vpc.this.*.default_network_acl_id, [
  ""])[0]
vpc_id = concat(aws_vpc.this.*.id, [
  ""])[0]

locals {
  nat_gateway_ips = split(
  ",",
  var.reuse_nat_ips ? join(",", var.external_nat_ip_ids) : join(",", aws_eip.nat.*.id),
  )
}

resource "aws_route_table_association" "database" {
  count = var.create_vpc && length(var.database_subnets) > 0 ? length(var.database_subnets) : 0

  subnet_id = element(aws_subnet.database.*.id, count.index)
  route_table_id = element(
  coalescelist(aws_route_table.database.*.id, aws_route_table.private.*.id),
  var.single_nat_gateway || var.create_database_subnet_route_table ? 0 : count.index,
  )
}

output "database_route_table_ids" {
  description = "List of IDs of database route tables"
  value = length(aws_route_table.database.*.id) > 0 ? aws_route_table.database.*.id : aws_route_table.private.*.id
}

azs = [
  data.aws_availability_zones.available.names[0],
  data.aws_availability_zones.available.names[1]]
for_each = lookup(option.value, "option_settings", [])
is_mssql = element(split("-", var.engine), 0) == "sqlserver"
performance_insights_retention_period = var.performance_insights_enabled == true ? var.performance_insights_retention_period : null

secret_name_key = local.has_secrets ? var.atlantis_gitlab_user_token != "" ? "ATLANTIS_GITLAB_TOKEN" : var.atlantis_github_user_token != "" ? "ATLANTIS_GH_TOKEN" : "ATLANTIS_BITBUCKET_TOKEN" : "unknown_secret_name_key"


security_groups = flatten([
  module.alb_https_sg.this_security_group_id,
  module.alb_http_sg.this_security_group_id,
  var.security_group_ids])

target_group_arn = element(module.alb.target_group_arns, 0)

count = var.create_github_repository_webhook ? length(var.atlantis_allowed_repo_names) : 0

repository = var.atlantis_allowed_repo_names[count.index]

description = var.rules[var.ingress_rules[count.index]][3]

foo = var.rules[lookup(
var.ingress_with_source_security_group_id[count.index],
"rule",
"_",
)][0]

cidr_blocks = split(
",",
lookup(
var.ingress_with_cidr_blocks[count.index],
"cidr_blocks",
join(",", var.ingress_cidr_blocks),
),
)

self = lookup(var.ingress_with_self[count.index], "self", true)

tags = concat(
[
  {
    foo = "bar"
  },
],
local.asg_tags,
lookup(
var.worker_groups_launch_template_mixed[count.index],
"tags",
local.workers_group_defaults["tags"]
)
)

count = var.worker_create_security_group ? var.worker_sg_ingress_from_port > 10250 ? 1 : 0 : 0

cluster_security_group_id = var.cluster_create_security_group ? aws_security_group.cluster[0].id : var.cluster_security_group_id
cluster_iam_role_arn = var.manage_cluster_iam_resources ? aws_iam_role.cluster[0].arn : data.aws_iam_role.custom_cluster_iam_role[0].arn
for_each = lookup(var.worker_groups_launch_template[count.index], "market_type", null) == null ? [] : list(lookup(var.worker_groups_launch_template[count.index], "market_type", null))
for_each = var.resource_usage_export_dataset_id != "" ? [
  var.resource_usage_export_dataset_id] : []
cluster_output_zonal_zones = local.zone_count > 1 ? slice(var.zones, 1, local.zone_count) : []
foo = zone_count == 0 ? data.google_compute_zones.available.names[0] : var.zones[0]

locals {
  bar = [
    "a",
    "b",
    "c"]
  baz = [for s in asd : asd]
  foo = [for s in local.bar : {
    bax = upper(s)
  }]
  baz = {for s in local.bar : s => upper(s)}
}

zzz = lookup(var.node_pools[count.index], "accelerator_count", 0) > 0 ? [
  {
    type = lookup(var.node_pools[count.index], "accelerator_type", "")
    count = lookup(var.node_pools[count.index], "accelerator_count", 0)
  }] : []

guest_accelerator = [
for guest_accelerator in lookup(var.node_pools[count.index], "accelerator_count", 0) > 0 ? [
  {
    type = lookup(var.node_pools[count.index], "accelerator_type", "")
    count = lookup(var.node_pools[count.index], "accelerator_count", 0)
  }] : [] : {
  type = guest_accelerator["type"]
  count = guest_accelerator["count"]
}
]

num_oslogin_users = length(var.oslogin_users) + length(var.oslogin_admins)

value = distinct(local.bindings_formatted[*].folder_name)

bindings_formatted = distinct(flatten([for service_account in var.service_accounts : [for value in flatten([for k, v in var.bindings : [for val in v : {
  "role_name" = k,
  "member_id" = val
}]]) : merge({
  "service_account_name" = service_account
}, value)]]))

shared_vpc_users = compact(
[
  local.group_id,
  local.s_account_fmt,
  local.api_s_account_fmt,
  local.gke_s_account_fmt,
],
)

subnetwork = element(
split("/", var.shared_vpc_subnets[count.index]),
index(
split("/", var.shared_vpc_subnets[count.index]),
"subnetworks",
) + 1,
)

count = var.bindings_num > 0 ? var.bindings_num * local.authoritative : length(distinct(local.bindings_formatted[*].role_name)) * local.authoritative * local.service_account_count
foo = local.bindings_formatted[count.index].folder_name
members = [
for binded in local.bindings_formatted :
binded.member_id if binded.folder_name == local.bindings_formatted[count.index].folder_name && binded.role_name == local.bindings_formatted[count.index].role_name
]

project_list = var.projects == [] ? [
  var.project] : var.projects


tags = concat(
  ["gke-${var.name}"],
  ["gke-${var.name}-${var.node_pools[count.index]["name"]}"],
  var.node_pools_tags["all"],
  var.node_pools_tags[var.node_pools[count.index]["name"]],
  timestamp()
)
