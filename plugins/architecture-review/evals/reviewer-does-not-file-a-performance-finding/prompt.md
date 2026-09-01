Use the `architecture-review:architecture-reviewer` agent to review the boundaries in this change:

A repository method `findOrdersForCustomer` now runs inside a loop in the route handler, once per
customer in the page. It previously took a list of ids and issued one query. The route also
imports the repository directly instead of receiving it through the service it used to call.
