# Deriving an Ossie ontology from a semantic view

An Ossie ontology file has `version`, `name`, `ontology` (concepts) and `ontology_mappings`. Each mapping embeds one `semantic_model` and a list of `concept_mappings` from logical **fields** to concepts. Mapping expressions reference `dataset.field` of the embedded model, never physical columns directly.

## Deterministic rules (`derive_ontology.py`)

| Semantic model | Ontology |
|---|---|
| dataset `orders` | EntityType `Orders` (PascalCase; rename to a business name during review) |
| single-column `primary_key: [order_id]` | ValueType `OrdersKey` (extends a built-in by datatype), relationship `order_id` → `OrdersKey`, `OneToOne`, `identify_by: [order_id]` |
| composite `primary_key` | one identifying relationship per column; the role is an entity when the column is a single-column FK, otherwise a built-in value type |
| relationship `orders → customers` | relationship `customers` on `Orders`, role `Customers`, `ManyToOne`, verbalization marked `TODO` |
| dimension field (with `--attributes`) | attribute relationship, `ManyToOne`, role = built-in by datatype (`String` when unknown) |
| PK / FK columns | fields are **added to the embedded model** if the semantic view did not expose them, so mappings stay valid |
| metrics | stay in the embedded core model; not ontology concepts |

Mappings generated:
- **`object_mappings`**: `{expression: orders.order_id}` for a simple identifier, or `referent_mappings` for composite identifiers, nested when a part is an entity.
- **`link_mappings`**: one tree per concept. The root is the concept's object mapping. The children are FK relationships (`object_mapping.concept` = target entity) and attribute relationships.

Built-in concepts available without definition: `Any`, `Boolean`, `Date`, `DateTime`, `Decimal`, `Float`, `Integer`, `String`.

## What the agent and the human finish

| Placeholder | Agent drafts | Human confirms |
|---|---|---|
| `verbalizes: ["{Orders} TODO relates to {Customers}"]` | `"{Order} is placed by {Customer}"`, using table/column comments and synonyms | wording and direction |
| Concept names | `Orders` → `Order`, `OrderItems` → `OrderLine` (update every reference: roles, identify_by, concept_mappings, verbalizes) | naming |
| `requires` (none generated) | candidate rules from enum values, comments, data checks, e.g. `"Amount > 0"`, `"OrderLine.nr > 0"` | every rule |
| `derived_by` (none generated) | only when the user describes a derived concept | yes |
| `multiplicity` | defaults are from keys; change to `OneToOne` only if the data proves it | yes |

After editing, run `validate_ossie.py`. It must report no errors and no `TODO` warnings. The validator checks:
- the schema;
- concept references in roles, `extends` and `identify_by`;
- that verbalization placeholders are roles of the relationship;
- that mapping expressions reference fields of the embedded model.

Keep the ClickZetta semantic view as the source of truth for metrics and fields. Re-run the derivation after structural changes, and carry over the reviewed wording.
