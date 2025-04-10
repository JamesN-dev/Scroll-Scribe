# Report Service

Report Server API is hosted on a Microsoft IIS Web Server. The service is designed according to a pull-strategy such that it scales linearly.

Reports are retrieved using a URL similar to:

```
http://ServiceHostName/Perfion/Report.ashx?id=fileId
```

Reports have a variety of parameters, allowing delivery in different languages, inclusion of multiple items, etc. These parameters are described below.

---

## Parameters

### `id`

Specifies which item(s) to include in the report. Multiple items can be included, separated by commas:

```
http://ServiceHostName/Perfion/Report.ashx?id=fileId1,fileId2
```

### `reportId`

Specifies which Perfion Database report to run.  
**This parameter is required!**

```
http://ServiceHostName/Perfion/Report.ashx?reportId=id&id=fileId1,fileId2
```

### `name`

Specifies the generated report's name (optional).

```
http://ServiceHostName/Perfion/Report.ashx?reportId=id&id=fileId&name=Test
```

### `action`

Works similarly to the Image & File Server.

### `streamtype`

Exports the report in different formats. Supported formats:

- Pdf
- Html
- Mht
- Rtf
- Xls
- Xlsx
- Csv
- Text
- AddInOutput

Example usage:

```
http://ServiceHostName/Perfion/Report.ashx?id=fileId1&streamtype=Mht
```

### `lg`

Generates reports in different languages, if data exists in Perfion in that language.

Example for German:

```
http://ServiceHostName/Perfion/Report.ashx?id=fileId1&lg=de
```

### `parameters`

Specifies report parameters as defined in the superquery (optional).  
Available from Perfion 2023 R1 SR1.

Format:

```
parameters=[{"id":'ParameterName',"values":['ParameterValue']}, …]
```

Example:

```
http://ServiceHostName/Perfion/Report.ashx?reportId=id&id=fileId&name=Test&parameters=[{"id":'ColorParam',"values":['Green']},{"id":'NumberParam',"values":['12,35']}]
```