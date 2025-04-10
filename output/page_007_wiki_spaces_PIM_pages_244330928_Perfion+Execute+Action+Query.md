# Perfion Execute Action Query

## Overview

The Perfion Execute Action query adds the requested Action to a queue on the Application server (introduced in Perfion 2022 R1). The Application server executes Actions in chronological order from this queue.

- **ActionID**: The ID of the action to be executed.
- **ActionInput**: Optional. Child elements must be serializable XML/JSON. These elements are converted to Data Tables usable within the Action.
- The query can be defined in either **XML** or **JSON** format.

---

## XML Example

### Request

```xml
<?xml version="1.0" encoding="utf-8"?>
<ExecuteAction ActionID="1234">
  <ActionInput>
    <ActionTable1>
      <Col1>123</Col1>
      <Col2>456</Col2>
    </ActionTable1>
    <ActionTable1>
      <Col1>123</Col1>
      <Col3>456</Col3>
    </ActionTable1>
    <ActionTable2>
      <Col1>123</Col1>
      <Col2>456</Col2>
    </ActionTable2>
  </ActionInput>
</ExecuteAction>
```

### Response

```xml
<?xml version="1.0" encoding="utf-8"?>
<Response>
  <Result>
    <ExecutionQueueId>12</ExecutionQueueId>
  </Result>
</Response>
```

---

## JSON Example

### Request

```json
{
  "ExecuteAction": {
    "ActionID": "123",
    "ActionInput": {
      "ActionTable1": {
        "Col1": "123",
        "Col2": "456"
      },
      "ActionTable1": {
        "Col1": "123",
        "Col3": "456"
      },
      "ActionTable2": {
        "Col1": "123",
        "Col2": "456"
      }
    }
  }
}
```

### Response

```json
{
  "ExecutionQueueId": 19
}
```