# REST API Service

All data from Perfion can be queried via two different endpoints. The endpoints differ in their input methods, but the response of both endpoints is the same.

The syntax of the JSON formatted response data is described in the [Query Reference](/wiki/spaces/PIM/pages/244332821).

---

## POST Data Endpoint

This endpoint accepts a Perfion JSON query and queries the Perfion Database for data.

### URL

```
POST /data
```

### Parameters

| Parameter | Description | Properties |
|-----------|-------------|------------|
| `string query` | JSON formatted search. The Perfion Query JSON is separated into the sections: Select, From, Where, Having, and Order. The syntax is inspired by SQL. | Content type: `application/json`<br>Parameter type: Body |

The input is a Perfion Query in JSON format, inspired by SQL but enhanced with features like multi-valued, sequenced, and localized data.

The method returns all data in JSON format. For binary features (images, files), a `binaryID` GUID is returned. The actual binary data can be retrieved via the File & Image Server included in the Perfion API service.

### Authentication

Requires a JWT bearer token. See [Authentication](/wiki/spaces/PIM/pages/244330998) for how to obtain a token.

The token must be supplied in the request header. In C#, it can be done on an `HttpClient` like this:

```csharp
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "<token>");
```

### Response Codes

- **200 OK**: Request successful. Response body is a JSON object (see [Query Reference](/wiki/spaces/PIM/pages/244332821)).
- **400 Bad Request**: Missing or invalid parameters. Response body contains error details.
- **401 Unauthorized**: No valid authentication token supplied.
- **500 Internal Server Error**: Unexpected error occurred. Response body contains error details.

---

## GET Data Endpoint

This endpoint accepts an ID reference of a saved search feature item and executes the Perfion query saved on it.

### URL

```
GET /data?searchId=123&index=0&maxCount=5
```

### Parameters

| Parameter | Description | Properties |
|-----------|-------------|------------|
| `int searchId` | Identifier for a feature data item placed under a search feature. | Parameter type: query |
| `int index` | Optional. Page index for paging control. | Parameter type: query |
| `int maxCount` | Optional. Max count per page for paging control. | Parameter type: query |

Returns data in JSON format. For binary features, a `binaryID` GUID is returned, which can be used to retrieve the actual binary data.

### Authentication

Requires a JWT bearer token. See [Authentication](/wiki/spaces/PIM/pages/244330998).

Example in C#:

```csharp
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "<token>");
```

### Response Codes

- **200 OK**: Request successful. Response body is a JSON object.
- **400 Bad Request**: Missing or invalid parameters.
- **401 Unauthorized**: No valid authentication token supplied.
- **500 Internal Server Error**: Unexpected error occurred.

---

## GET Version Endpoint

Returns the version number of the API service.

### URL

```
GET /get-version
```

### Parameters

None.

### Authentication

Requires a JWT bearer token. See [Authentication](/wiki/spaces/PIM/pages/244330998).

Example in C#:

```csharp
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "<token>");
```

### Response Codes

- **200 OK**

```json
{
  "Version": "5.2.0"
}
```

- **400 Bad Request**: Missing or invalid parameters.
- **401 Unauthorized**: No valid authentication token supplied.
- **500 Internal Server Error**: Unexpected error occurred.

---

## POST Execute Action Endpoint

Executes an action and returns an execution ID.

### URL

```
POST /execute-action/{actionId}
```

### Parameters

| Parameter | Description | Properties |
|-----------|-------------|------------|
| `int actionId` | Action ID to be executed. | Content type: `application/json`<br>Parameter type: URI |
| `string actionInput` | JSON formatted table. Example:<br>{ "ActionInput": { "ActionTable1": [ { "Col1": "123", "Col2": "456" }, { "Col1": "123", "Col3": "456" } ], "ActionTable2": { "Col1": "123", "Col2": "456" } }} | Content type: `application/json`<br>Parameter type: Body |

### Authentication

Requires a JWT bearer token. See [Authentication](/wiki/spaces/PIM/pages/244330998).

Example in C#:

```csharp
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "<token>");
```

### Response Codes

- **200 OK**

```json
{
  "ExecutionQueueId": 19
}
```

- **400 Bad Request**: Missing or invalid parameters.
- **401 Unauthorized**: No valid authentication token supplied.
- **500 Internal Server Error**: Unexpected error occurred.

---

## POST Process Report Endpoint

Processes a report and returns the processed report file.

*Available from Perfion 2023 R1 SR1.*

### URL

```
POST /reports/{reportId}/process?id=3027&language=dan&streamtype=pdf
```

### Parameters

| Parameter | Description | Properties |
|-----------|-------------|------------|
| `int reportId` | Report ID to be processed. | Parameter type: URI |
| `int id` | ID(s) of item(s) to include in the report. Can be comma-separated list. | Parameter type: URI |
| `string language` | Language for the report. Optional. | Parameter type: URI |
| `string streamtype` | Report format. Optional. Supported formats:<br>- Pdf<br>- Html<br>- Mht<br>- Rtf<br>- Xls<br>- Xlsx<br>- Csv<br>- Text<br>- AddInOutput | Parameter type: URI |
| `string action` | Action parameter as described for Media Services URL Parameters. Optional. | Parameter type: URI |
| `string parameters` | JSON array of report parameters as specified in the report's superquery. Optional.<br>Example:<br>```json<br>[<br> {"id":"StringTestParam","values":["Testing"]},<br> {"id":"IntTestParam","values":["123"]},<br> {"id":"DateTestParam","values":["2022-12-01"]},<br> {"id":"SelectTestParam","values":["3593"]},<br> {"id":"MultiTestParam","values":["1st value","2nd value"]}<br>]``` | Content type: `application/json`<br>Parameter type: Body |

### Authentication

Requires a JWT bearer token. See [Authentication](/wiki/spaces/PIM/pages/244330998).

Example in C#:

```csharp
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", "<token>");
```

### Response Codes

- **200 OK**: Response body is a streamed report file.
- **400 Bad Request**: Missing or invalid parameters.
- **401 Unauthorized**: No valid authentication token supplied.
- **500 Internal Server Error**: Unexpected error occurred.

---