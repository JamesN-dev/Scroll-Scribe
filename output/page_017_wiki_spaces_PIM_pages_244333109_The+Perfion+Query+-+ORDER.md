# The Perfion Query - ORDER

When no `Order` part is specified, there is no guaranteed order; the order depends on the query plan.

## Syntax

### XML

```xml
<Order mode='Hierarchical'>
  <By id='Brand' />
  <By id='PowerW' direction='desc' />
  <By id='String(EN)' />
</Order>
```

### JSON

```json
"Order": {
  "Mode": "Hierarchical",
  "By": [
    { "id": "Brand" },
    { "id": "PowerW", "direction": "desc" },
    { "id": "String(EN)" }
  ]
}
```

## Mode Attribute

Introduced in version 4.7.5, the `mode` attribute on the `Order` element controls whether sorting considers the item hierarchy.

| mode          | Description                                               |
|---------------|-----------------------------------------------------------|
| `Flat`        | Default if no mode is supplied. Ignores hierarchy.        |
| `Hierarchical`| Considers item hierarchy during sorting.                  |

## `<By>` Element / `"By"` Array Properties

| Attribute   | Description                                                                                   |
|-------------|-----------------------------------------------------------------------------------------------|
| `id`        | The Name, ID, or Property of a feature on the items in the `From` part of the clause.        |
| `direction` | Optional. Defaults to ascending order unless specified as `'desc'`.                          |

## Language Specification in `id`

| Example                 | Interpretation                                                                                   |
|-------------------------|-------------------------------------------------------------------------------------------------|
| `id='String'`           | Uses the first language specified by the `languages` attribute/property on the `Select` clause. |
| `id='String(EN)'`       | Uses the specified language (`EN`).                                                             |
| `id='String(*)'`        | No specific language is used.                                                                   |

If no specific language is used and values exist for multiple languages, the value with the lowest alphanumeric order determines the sorting. For example, ascending order will prioritize `'Black'` (English) over `'Schwarz'` (German).

---

# Ordering Using a Relation to Another Feature

In addition to ordering by feature values, you can order items using the **Sortable Related Items** property on selectable features.

When defining a feature, enabling **Sortable Related Items** allows related items to be ordered based on the value of the original feature.

### Example: Catalog and Products

In the Coffee Demo database:

- The **Catalog** feature has **Sortable Related Items** enabled.
- Products related to a Catalog can be sorted differently per Catalog.
- Changing the order in the GUI is done by selecting a product and pressing `ALT + Up` or `ALT + Down`.

### Query Result Example

When querying products in the "Mixed products on sale" catalog, the response includes a `relatedOrder` attribute:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Data totalExecutionTime="00:00:00.1269285" totalCount="3">
  <Features>
    <Product id="100" language="EN" caption="Product" ... />
    <ItemName id="101" language="EN" caption="Item Name" ... />
    <Image id="105" language="EN" caption="Image" ... />
    <Color id="210" language="EN" caption="Color" ... />
    <Catalog id="104" language="EN" caption="Catalog" ... />
  </Features>
  <Product id="560" parentId="559" brand="Normal" order="0" ...>
    <Value seq="0" viewOrder="0" ...>1923-16</Value>
    <Color language="EN" id="598" ...>Chrome</Color>
    ...
    <Catalog language="EN" id="2809" ... relatedOrder="7" ...>Mixed products on sale</Catalog>
  </Product>
  <Product id="566" parentId="559" brand="Normal" order="0" ...>
    <Value seq="0" viewOrder="0" ...>1923-18</Value>
    <Color language="EN" id="598" ...>Sand</Color>
    ...
    <Catalog language="EN" id="2809" ... relatedOrder="6" ...>Mixed products on sale</Catalog>
  </Product>
  <Product id="653" parentId="711" brand="Normal" order="0" ...>
    <Value seq="0" viewOrder="0" ...>40511-565-0</Value>
    <Color language="EN" id="598" ...>Red</Color>
    ...
    <Catalog language="EN" id="2809" ... relatedOrder="5" ...>Mixed products on sale</Catalog>
  </Product>
</Data>
```

- `relatedOrder` values determine the order within the catalog.
- The values are numerically ordered but may not start from 1 or be consecutive.

### Ordering by Related Order

By default, output is **not** ordered by `relatedOrder`. To order by it, use an `Order` clause like:

```xml
<Query>
  <Select languages='EN' options='IncludeFeatureViewOrder'>
    <Feature id='**' view='WebVariant' />
  </Select>
  <From id='100' />
  <Where>
    <Clause id='Catalog' operator='=' value='Mixed products on sale' />
  </Where>
  <Order>
    <By id='Catalog.RelatedOrder(2809)' />
  </Order>
</Query>
```

- The `By` clause orders products by their catalog feature relative to the item with ID `2809` ("Mixed products on sale").
- This ordering is meaningful only when combined with a `Where` clause restricting to items in that catalog.
- Including unrelated products results in undefined order for those items.

---

# Summary

- The `Order` clause controls sorting in Perfion queries.
- Supports hierarchical or flat sorting modes.
- Can specify multiple fields and directions.
- Supports language-specific sorting.
- Allows ordering by related feature order when **Sortable Related Items** is enabled.