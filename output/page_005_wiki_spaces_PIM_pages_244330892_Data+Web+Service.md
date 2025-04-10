# Data Web Service

All data from Perfion can be queried via a single method:

```csharp
string ExecuteQuery(string query);
```

### Parameters

| Parameter        | Description                                                                                                                      |
|------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `string query`   | XML formatted search. The Perfion Query XML is separated into the sections: `<Select>`, `<From>`, `<Where>`, `<Having>`, and `<Order>`. The syntax is inspired by normal SQL and should therefore be easy to learn. |

As input, the method takes a Perfion Query in XML-format or JSON-format. The syntax is inspired by SQL but enhanced with the ability to return multi-valued and sequenced data, localized data in multiple languages, and other advanced features not possible with regular SQL tabular results.

The method returns all data in XML-format. For binary features such as images and files, the `binaryID` GUID value is returned. The actual binary data can then be retrieved via the File & Image Server.

## Calling the Web Service with Authentication

If authentication has been enabled during installation and configuration of the Perfion API Service (see the [Perfion API - Installation Guide](https://perfion.atlassian.net/wiki/spaces/PIM/pages/244330766/Installation+guide)), any call to the `GetData` endpoint must be authenticated.

Refer to the [Authentication](https://perfion.atlassian.net/wiki/spaces/NKP/pages/3670275/Reference+Guide#Authentication) guide for details on how to authenticate against the data endpoint.

## Getting Perfion API Version

To retrieve the Perfion API version, call:

```csharp
string GetVersion();
```

## Proportioning of Multiple Images

To display multiple images side-by-side proportionally, it may be necessary to scale them using the same DPI. The following method calculates the DPI resolution to use so each image fits within a specified width x height frame and matches proportionally:

```csharp
float CalcImageScale(int maxWidth, int maxHeight, Guid[] imageIDs);
```

### Parameters

| Parameter                 | Description                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------|
| `int maxWidth`            | Maximum width (in pixels) that each image must fit within.                                      |
| `int maxHeight`           | Maximum height (in pixels) that each image must fit within.                                    |
| `Guid[] imageIDs`         | List of image GUIDs to be scaled equally.                                                      |