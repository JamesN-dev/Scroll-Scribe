# Perfion Query Reference

## Overview

The Perfion Query syntax and all its possibilities are described in the following sections. The Perfion Query can be defined in either XML or JSON format. All examples are shown in each version.

### A simple example

Below is a very simple example of a Perfion Query. The query returns data for the features **ItemNumber**, **Image**, and **Description** in English for Products with `PowerW = 1600`.

#### XML

```xml
<Query>
  <Select languages='EN'>
    <Feature id='ItemNumber' />
    <Feature id='Image' />
    <Feature id='Description' />
  </Select>
  <From id='Product'/>
  <Where>
    <Clause id='PowerW' operator='=' value='1600' />
  </Where>
</Query>
```

#### JSON

```json
{
  "Query": {
    "Select": {
      "languages": "EN",
      "Features": [
        { "id": "ItemNumber" },
        { "id": "Image" },
        { "id": "Description" }
      ]
    },
    "From": [
      { "id": "Product" }
    ],
    "Where": {
      "Clauses": [
        { "Clause": { "id": "PowerW", "operator": "=", "value": "1600" } }
      ]
    }
  }
}
```

### Example Result

Below is an example of the results from the above query.

#### XML

```xml
<Data totalExecutionTime="00:00:00.1105121">
  <Features>
    <Image id="105" language="EN" caption="Image" group="All" dataType="Image" />
    <Description id="148" language="EN" caption="Description" group="All" dataType="Text" />
    <Product id="100" language="EN" caption="Product" group="All" dataType="String" />
  </Features>
  <Product id="853" parentId="0" brand="Normal" order="0">
    <Value seq="0" modifiedDate="2016-07-12T11:01:22.93">TE717209RW</Value>
    <Image seq="0" modifiedDate="2019-11-27T09:09:56.437" string="MCSA00992759_SE_K_12_KV7_EQ7_TE717209RW_picture_KF1_coffeemachine_ENG_230215_def_(48).jpg.jpg" fileSize="18967" fileModifiedDate="2019-11-27T09:09:50.123" width="300" height="300" widthDpi="48" heightDpi="48">5fd1e0be-56bd-407f-bce8-6e6d35f1e792</Image>
    <Description language="EN" seq="0" modifiedDate="2017-11-23T13:48:44.45">
      Siemens TE717209RW is a beautiful piano black fully automatic espresso machine from Siemens EQ7 series. With just a tap you make cappuccino, latte, espresso or coffee.
      This model has the smart and practical "My Coffee" function so you can configure the relationship between milk and espresso in your drink - you could choose up to 80% coffee, so you have extra power and heat your milk drink!
      The grinder automatically adjusts itself to the coffee blend you use. And the individual programming ensures that up to 6 people can have their own coffee profile, where each button is programmed after the personal wishes.
    </Description>
  </Product>
  <Product id="858" parentId="0" brand="Normal" order="0" createdDate="2016-07-12T11:15:10.52" modifiedDate="2020-04-21T14:59:11.317">
    <Value seq="0" modifiedDate="2016-07-12T11:15:18.887">TE806201RW</Value>
    <Image seq="0" modifiedDate="2019-11-27T09:09:56.437" string="MCSA01088244_SE_K_12_KV8_EQ8_TE806201RW_picture_KF1_machine_ENG_120615_def_(48).jpg.jpg" fileSize="36135" fileModifiedDate="2019-11-27T09:09:50.17" width="452" height="480" widthDpi="48" heightDpi="48">004ede8a-592a-4466-90ae-f5f97aa117dc</Image>
    <Description language="EN" seq="0" modifiedDate="2016-07-12T11:50:54.053">
      EQ8 series espresso machines in a class by itself, with a beautiful stainless steel design and an intelligent heating system: sensoFlow-ensuring system constant brewing temperature and thus guarantees maximum enjoyment espresso every time.
      Siemens EQ8 also the smart aroma double shot mode makes extra strong coffee less bitter because the machine grinds and brews twice with 19 bar.
      Furthermore ensures EQ8 an exclusive convenience through OneTouch Feature creamCleaner, cup warmer, lighting and insulated milk container.
    </Description>
  </Product>
</Data>
```

#### JSON

```json
{
  "Data": {
    "totalExecutionTime": "00:00:00.0882522",
    "Features": [
      { "name": "Image", "id": 105, "language": "EN", "caption": "Image", "group": "All", "dataType": "Image" },
      { "name": "Description", "id": 148, "language": "EN", "caption": "Description", "group": "All", "dataType": "Text" },
      { "name": "Product", "id": 100, "language": "EN", "caption": "Product", "group": "All", "dataType": "String" }
    ],
    "Items": [
      {
        "featureId": 100,
        "featureName": "Product",
        "id": 853,
        "parentId": 0,
        "brand": "Normal",
        "order": 0,
        "Values": [
          { "featureId": 100, "featureName": "Value", "seq": 0, "modifiedDate": "2016-07-12T11:01:22.93", "value": "TE717209RW" },
          { "featureId": 105, "featureName": "Image", "seq": 0, "modifiedDate": "2019-11-27T09:09:56.437", "string": "MCSA00992759_SE_K_12_KV7_EQ7_TE717209RW_picture_KF1_coffeemachine_ENG_230215_def_(48).jpg.jpg", "fileSize": 18967, "fileModifiedDate": "2019-11-27T09:09:50.123", "width": 300, "height": 300, "widthDpi": 48, "heightDpi": 48, "value": "5fd1e0be-56bd-407f-bce8-6e6d35f1e792" },
          { "featureId": 148, "featureName": "Description", "language": "EN", "seq": 0, "modifiedDate": "2017-11-23T13:48:44.45", "value": "Siemens TE717209RW is a beautiful piano black fully automatic espresso machine from Siemens EQ7 series. With just a tap you make cappuccino, latte, espresso or coffee.\r\n\r\nThis model has the smart and practical \"My Coffee\" function so you can configure the relationship between milk and espresso in your drink - you could choose up to 80% coffee, so you have extra power and heat your milk drink!\r\n\r\nThe grinder automatically adjusts itself to the coffee blend you use. And the individual programming ensures that up to 6 people can have their own coffee profile, where each button is programmed after the personal wishes." }
        ]
      },
      {
        "featureId": 100,
        "featureName": "Product",
        "id": 858,
        "parentId": 0,
        "brand": "Normal",
        "order": 0,
        "createdDate": "2016-07-12T11:15:10.52",
        "modifiedDate": "2020-04-21T14:59:11.317",
        "Values": [
          { "featureId": 100, "featureName": "Value", "seq": 0, "modifiedDate": "2016-07-12T11:15:18.887", "value": "TE806201RW" },
          { "featureId": 105, "featureName": "Image", "seq": 0, "modifiedDate": "2019-11-27T09:09:56.437", "string": "MCSA01088244_SE_K_12_KV8_EQ8_TE806201RW_picture_KF1_machine_ENG_120615_def_(48).jpg.jpg", "fileSize": 36135, "fileModifiedDate": "2019-11-27T09:09:50.17", "width": 452, "height": 480, "widthDpi": 48, "heightDpi": 48, "value": "004ede8a-592a-4466-90ae-f5f97aa117dc" },
          { "featureId": 148, "featureName": "Description", "language": "EN", "seq": 0, "modifiedDate": "2016-07-12T11:50:54.053", "value": "EQ8 series espresso machines in a class by itself, with a beautiful stainless steel design and an intelligent heating system: sensoFlow-ensuring system constant brewing temperature and thus guarantees maximum enjoyment espresso every time.\r\n\r\nSiemens EQ8 also the smart aroma double shot mode makes extra strong coffee less bitter because the machine grinds and brews twice with 19 bar.\r\n\r\nFurthermore ensures EQ8 an exclusive convenience through OneTouch Feature creamCleaner, cup warmer, lighting and insulated milk container." }
        ]
      }
    ]
  }
}
```

The result always starts with metadata about the returned features, followed by the actual data.

---

## Result Metadata

The first part of the result contains a `<Features>` section with metadata about the returned features:

| Attribute             | Description                                                                                                                                                                                                                                         |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **id**                | The unique ID of the feature. Both feature name and ID can be used in queries.                                                                                                                               |
| **Name**              | The unique name of the feature. Both feature name and ID can be used in queries.                                                                                                                             |
| **Language**          | Indicates the language of the values of the other attributes in the XML element.                                                                                                                             |
| **Caption**           | The caption to precede the value on e.g., a web page, catalog, or other output.                                                                                                                              |
| **captionAlternative**| An alternative caption.                                                                                                                                                                                                                            |
| **Unit**              | The unit of the feature's value.                                                                                                                                                                                                                   |
| **Abbr**              | The abbreviation (could be used instead of the caption).                                                                                                                                                                                           |
| **Group**             | The Information Group the feature belongs to.                                                                                                                                                                                                      |
| **groupOrder**        | The order of the Information Group as defined in Perfion.                                                                                                                                                                                          |
| **viewGroup**         | The View Group the feature belongs to (if defined).                                                                                                                                                                                                |
| **viewGroupOrder**    | The order of the View Group as defined in Perfion.                                                                                                                                                                                                 |
| **dataType**          | The Perfion data type of the feature (string, number, date, text, image, file, query, table).                                                                                                                                                      |
| **viewOrder**         | The order of appearance of the features. This is a first-seen order of appearance. Each item may have a different viewOrder defined in Perfion. Relevant when multiple items are shown together in a list.                                         |
| **Form**              | Indicates the form/nature of the feature: <br> - **Simple**: Contains only its own base values. <br> - **Complex**: Extended with additional features (e.g., a Product with many features, or a Designer with additional features).                 |

---

## Result Data

The rest of the XML contains the actual data. In the example, the enclosing elements are `<Product>` since the returned items are of type Product, as specified by the `<From>` element.

### Item Attributes

Each `<Product>` item contains:

| Attribute    | Description                                                                                                                                    |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **id**       | Unique ID of the item.                                                                                                                        |
| **parentId** | ID of the parent item (0 if none).                                                                                                            |
| **Brand**    | Brand of the item (Virtual, Normal, CatalogRoot, or Brand).                                                                                   |
| **Order**    | Order of the item as defined on the item itself. For features without custom ordering, this is always 0.                                      |
| **childCount** | Number of child items (optional, included if `IncludeChildCount` is specified).                                                             |

### Feature Value Attributes

Feature value elements inside `<Product>` may have:

| Attribute       | Description                                                                                                                                                                                                                     |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **id**          | Unique ID of the item (for features defined as 'Selectable', e.g., lookup values).                                                                                                                                             |
| **Language**    | Language of the value (for features defined as 'Localizable').                                                                                                                                                                 |
| **Seq**         | Sequence number for features allowing multiple and sortable values. 0 otherwise.                                                                                                                                               |
| **relatedOrder**| Order when the feature includes 'Sortable Related Items'. Indicates how the item is ordered in relation to the feature (e.g., order of a Product within a Section).                                                            |
| **viewOrder**   | Order in which features for an item should appear. Explicitly included features are ordered as in the query, followed by others as defined in the feature configuration. Optional, included if `IncludeFeatureViewOrder` is set. |

### Image and File Feature Attributes

For image and file features:

| Attribute          | Description                                  |
|--------------------|----------------------------------------------|
| **string**         | Filename of the image or file.               |
| **fileSize**       | File size in bytes.                          |
| **fileModifiedDate** | Date when the file was last modified.     |

---

## Additional Notes

- The Boolean data type returns `"True"` and `"False"` as values.
- In two-state mode, only `"True"` is returned; false is represented as `Null` in the system.

---

## Table of Contents

1. [Overview](#overview)
    - [A simple example](#a-simple-example)
    - [Result Metadata](#result-metadata)
    - [Result Data](#result-data)

---

## Further Reading

- [The Perfion Query – SELECT](/wiki/spaces/PIM/pages/244332898/The+Perfion+Query+SELECT)
- [The Perfion Query – UPDATE](/wiki/spaces/PIM/pages/244333000/The+Perfion+Query+UPDATE)
- [The Perfion Query – INSERT](/wiki/spaces/PIM/pages/244333019/The+Perfion+Query+INSERT)
- [The Perfion Query – DELETE](/wiki/spaces/PIM/pages/244333038/The+Perfion+Query+DELETE)
- [The Perfion Query - FROM](/wiki/spaces/PIM/pages/244333057/The+Perfion+Query+-+FROM)
- [The Perfion Query - WHERE](/wiki/spaces/PIM/pages/244333076/The+Perfion+Query+-+WHERE)
- [The Perfion Query - ORDER](/wiki/spaces/PIM/pages/244333109/The+Perfion+Query+-+ORDER)
- [The Perfion Query - HAVING](/wiki/spaces/PIM/pages/244333145/The+Perfion+Query+-+HAVING)
- [The Perfion Query - Expressions](/wiki/spaces/PIM/pages/244333164/The+Perfion+Query+-+Expressions)
- [Response of the Perfion Query](/wiki/spaces/PIM/pages/244333217/Response+of+the+Perfion+Query)
- [The Perfion Query - Known Issues](/wiki/spaces/PIM/pages/244333236/The+Perfion+Query+-+Known+Issues)
- [Changes to the Perfion Query](/wiki/spaces/PIM/pages/244333255/Changes+to+the+Perfion+Query)