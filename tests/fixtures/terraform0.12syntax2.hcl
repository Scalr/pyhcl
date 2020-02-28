# nested ternary
structure1 = foo ? true : bar ? true : baz ? true : false

# nested ternary with boolean expression
structure2 = foo ? true : bar || baz ? true : bak ? true : false
structure2_1 = tok1 ? tok2 ? "tok3" : "tok4" || "tok5" ? "tok6" : "tok7" : "tok8"

# ternary with nested boolean expressions
structure3 = foo && bar > 0 ? baz : 0
structure4 = length(foo.bar.*.id) > 0 ? foo.bar.*.id : foo.baz.*.id

# ternary with nested boolean expressions functions as arguments
structure4 = foo && length(bar) > 0 ? length(baz) : 0

# ternary with nested boolean expressions functions and numbers as arguments
structure5 = foo && bar && length(baz) > 0 ? 1 : 0

# nested boolean expressions with ternary
structure6 = foo  && bar  && length(baz) > 0  && var.foo  && false == var.bar ? 1 : 0
structure6_1 = foo && length(bar) > 0 && false == baz || length(var.foo) >= length(var.bar) ? length(var.baz) : 0

# getting element of list
structure7 = foo.bar.*.id[count.index]
structure7_1 = concat(foo, [""])[count.index]
structure7_2 = concat(foo.bar.*.id, [""])[0]

# ternary as function argument
structure8 = split(
  ",",
  var.reuse_nat_ips ? join(",", var.external_nat_ip_ids) : join(",", aws_eip.nat.*.id),
)
structure8_1 = element(
  coalescelist(aws_route_table.database.*.id, aws_route_table.private.*.id),
  var.single_nat_gateway || var.create_database_subnet_route_table ? 0 : count.index,
)

structure9 = [
  foo.bar.baz.names[0],
  foo.bar.baz.names[1],
  foo.bar[0].baz[0].names[1].id
]

# empty list as function argument
structure10 = lookup(foo, "bar", [])
# function as argument of boolean expression
structure11 = element(split("-", foo), 0) == "bar"
# list as function argument
structure12 = flatten([foo, bar, baz])
# number as function argument
structure13 = element(foo, 0)
# accessing list if lists element
structure14 = foo[bar[count.index]][1]
# comma after last funciton argument
structure15 = foo[lookup(bar[count.index], "baz", "_",)][0]
structure15_1 = split(",", lookup(foo[count.index], "bar", join(",", baz), ), )

# for statement
structure15 =  [for foo in bar : foo]
structure15_1 =  [for foo in bar : foo if foo.baz > 0]
structure15_2 =  [for foo in bar : { baz = upper(foo) }]
structure15_3 =  {for foo in bar : baz => upper(foo)}

structure15_4 = [
  for foo in lookup(bar[count.index], "baz", 0) > 0 ? [
    {
      type = lookup(var.foo[count.index], "type", "")
      count = lookup(var.foo[count.index], "count", 0)
    }
  ] : [] : {
    type = foo["type"]
    count = foo["count"]
  }
]

structure15_5 = distinct(flatten([for service_account in var.service_accounts : [for value in flatten([for k, v in var.bindings : [for val in v : {
  "role_name" = k,
  "member_id" = val
}]]) : merge({
  "service_account_name" = service_account
}, value)]]))

structure15_6 =  [for k, v in bar : foo]

# arithmetic operations with functions
structure16 = length(foo) + length(bar) - length(baz)*length(foo)/length(baz)
# asterisk in brackets syntax to retrieve list
structure17 = distinct(foo.bar[*].baz)

# list of lists
structure18 = [["string"], [0], [], [length(foo)], [bar ? true : false]]
