---
title: "Train-Serving Skew and the Shared Feature Function"
tags: [foundations, pattern]
summary: "Skew is the same input producing different features in two code paths; an unknown category vectorises to all zeros without an error, so the fix is one normalising feature function, a contract test, and logged serving features."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--01-feature-stores.md
---

# Train-Serving Skew and the Shared Feature Function

Leakage ([[Point-in-Time As-Of Join for Features]]) is wrong information across time. Skew is wrong information across code: the same ride yields different features in the training path and the serving path.

## A silent example

A categorical feature is built as the string `PU_DO = "<pickup>_<dropoff>"` and one-hot encoded by a `DictVectorizer`, whose fitted vocabulary is part of the model. A serving path that goes through JSON turns the integer IDs into floats, so the key becomes `130.0_205.0`, which is not in the vocabulary. The vectoriser treats an unknown category as all zeros and raises nothing: the service keeps answering with the pair's effect silently gone (train path `[1, 0, 3.66]`, serve path `[0, 0, 3.66]`).

Fix: normalise types inside the one shared function, and pin it with a test that sends both shapes and asserts equal output:

```python
def prepare_features_v2(ride):
    pu, do = int(ride["PULocationID"]), int(ride["DOLocationID"])
    return {"PU_DO": f"{pu}_{do}", "trip_distance": float(ride["trip_distance"])}

assert prepare_features_v2(train_row) == prepare_features_v2(served_row)
```

## Practices

| Practice | Why |
|---|---|
| Pickle the vectoriser and model together, or log an sklearn `Pipeline` | The fitted vocabulary is part of the model |
| One feature function used by training, batch, web and stream | Otherwise two code paths drift apart |
| Test the function directly | A unit test on it is the cheapest skew guard |
| Log feature values at serving and compare with what training would compute | The direct skew check: the same example should give identical values on both paths |
| Monitor the share of unknown categories at serving | An alarm that costs almost nothing |

## Limits

One shared function suffices for one team, one language and one model. It stops sufficing when training is a Spark job, serving is a Go service and several teams have each written their own "rides in the last hour"; that is when [[Feature Stores: Parts and When You Need One]] earn their keep. Skew can also hide inside a healthy-looking score; see [[Drift Types and What Monitors Can See]].

## See Also
- [[Point-in-Time As-Of Join for Features]] — related
- [[Feature Stores: Parts and When You Need One]] — extends
- [[Drift Types and What Monitors Can See]] — related
- [[Categorical Encoding Choices]] — related
- [[Pipelines Prevent Preprocessing Leakage]] — related
