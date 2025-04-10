# Perfion GetVersion Query

The **Perfion GetVersion** query returns the Perfion API version. The query can be defined in either **XML** or **JSON** format.

## XML Query

```xml
<GetVersion />
```

### XML Query Response

```xml
<?xml version="1.0" encoding="utf-8"?> 
<Response> 
  <Result> 
    <Version>5.0.0</Version> 
  </Result> 
</Response>
```

## JSON Query

```json
{ "GetVersion": {} }
```

### JSON Query Response

```json
{
  "Version": "5.0.0"
}
```