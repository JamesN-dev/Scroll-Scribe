# Database Functions

## DenseRank

```python
class DenseRank(*expressions, **extra)
```

Equivalent to [Rank](#rank) but does not have gaps.

## FirstValue

```python
class FirstValue(expression, **extra)
```

Returns the value evaluated at the row that’s the first row of the window frame, or `None` if no such value exists.

## Lag

```python
class Lag(expression, offset=1, default=None, **extra)
```

Calculates the value offset by `offset`, and if no row exists there, returns `default`.

`default` must have the same type as the `expression`, however, this is only validated by the database and not in Python.

### MariaDB and `default`

MariaDB [doesn’t support](https://jira.mariadb.org/browse/MDEV-12981) the `default` parameter.

## LastValue

```python
class LastValue(expression, **extra)
```

Comparable to [FirstValue](#firstvalue), it calculates the last value in a given frame clause.

## Lead

```python
class Lead(expression, offset=1, default=None, **extra)
```

Calculates the leading value in a given [frame](../expressions/#window-frames). Both `offset` and `default` are evaluated with respect to the current row.

`default` must have the same type as the `expression`, however, this is only validated by the database and not in Python.

### MariaDB and `default`

MariaDB [doesn’t support](https://jira.mariadb.org/browse/MDEV-12981) the `default` parameter.

## NthValue

```python
class NthValue(expression, nth=1, **extra)
```

Computes the row relative to the offset `nth` (must be a positive value) within the window. Returns `None` if no row exists.

Some databases may handle a nonexistent nth-value differently. For example, Oracle returns an empty string rather than `None` for character-based expressions. Django doesn’t do any conversions in these cases.

## Ntile

```python
class Ntile(num_buckets=1, **extra)
```

Calculates a partition for each of the rows in the frame clause, distributing numbers as evenly as possible between 1 and `num_buckets`. If the rows don’t divide evenly into a number of buckets, one or more buckets will be represented more frequently.

## PercentRank

```python
class PercentRank(*expressions, **extra)
```

Computes the relative rank of the rows in the frame clause. This computation is equivalent to evaluating:

```plaintext
(rank - 1) / (total rows - 1)
```

The following table explains the calculation for the relative rank of a row:

| Row # | Value | Rank | Calculation | Relative Rank |
|-------|-------|------|-------------|---------------|
| 1     | 15    | 1    | (1-1)/(7-1) | 0.0000        |
| 2     | 20    | 2    | (2-1)/(7-1) | 0.1666        |
| 3     | 20    | 2    | (2-1)/(7-1) | 0.1666        |
| 4     | 20    | 2    | (2-1)/(7-1) | 0.1666        |
| 5     | 30    | 5    | (5-1)/(7-1) | 0.6666        |
| 6     | 30    | 5    | (5-1)/(7-1) | 0.6666        |
| 7     | 40    | 7    | (7-1)/(7-1) | 1.0000        |

## Rank

```python
class Rank(*expressions, **extra)
```

Comparable to [RowNumber](#rownumber), this function ranks rows in the window. The computed rank contains gaps. Use [DenseRank](#denserank) to compute rank without gaps.

## RowNumber

```python
class RowNumber(*expressions, **extra)
```

Computes the row number according to the ordering of either the frame clause or the ordering of the whole query if there is no partitioning of the [window frame](../expressions/#window-frames).